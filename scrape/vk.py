import logging
from typing import List, Optional

import vk_api
from vk_api import VkUserPermissions, ApiError

from base import Exporter

MAX_PER_WALL_PAGE = 100


class VKScraper:
    def __init__(
            self, config: dict,
            exporter: Exporter = None,
            # lock: RLock = None, FIXME
            group_list=None,
            group_names=None,
            post_limit=1000,
            comment_limit=1000,
            ts_start: int = None,
            ts_end: int = None
    ):
        # self._lock = lock FIXME
        self.log = logging.getLogger(name=type(self).__name__)

        if 'vk' not in config:
            raise ValueError('json config must contain "vk" section')

        for mandatory in ['login', 'token', 'app_id']:
            if not config['vk'].get(mandatory, False):
                raise ValueError(f'{mandatory} field must be provided')

        self.post_limit = post_limit
        self.comment_limit = comment_limit
        self.exporter = exporter
        self.ts_start = ts_start
        self.ts_end = ts_end
        self._group_list = group_list if group_list is not None else []
        self._group_names = group_names if group_names is not None else []

        self.log.info('Initializing API...')
        self.__session = vk_api.VkApi(
            login=config['vk']['login'],
            token=config['vk']['token'],
            app_id=config['vk']['app_id'],
            scope=sum(VkUserPermissions) - VkUserPermissions.MESSAGES
        )
        # noinspection PyProtectedMember
        self.__session._auth_token()
        self.api = self.__session.get_api()

    def _get_newsfeed(self, **kwargs):
        try:
            return self.api.newsfeed.get(**kwargs)
        except ApiError as e:
            self.log.error('Failed during api.newsfeed.get')
            self.log.error(e, exc_info=True)
            raise e

    def _get_by_groups(self, **kwargs):
        try:
            return self.api.groups.getById(**kwargs)
        except ApiError as e:
            self.log.error('Failed during api.groups.getById')
            self.log.error(e, exc_info=True)
            raise e

    def _get_wall_comments(self, **kwargs):
        try:
            return self.api.wall.getComments(**kwargs)
        except ApiError as e:
            self.log.error('Failed during api.wall.getComments')
            self.log.error(e, exc_info=True)
            raise e

    def _get_wall(self, **kwargs):
        try:
            return self.api.wall.get(**kwargs)
        except ApiError as e:
            self.log.error('Failed during api.wall.get')
            self.log.error(e, exc_info=True)
            raise e

    def _resolve_group_id(self, name: str) -> Optional[int]:
        self.log.info(f'Solving group id from provided shortname: {name}')
        try:
            result = self._get_by_groups(
                group_id=name, fields=f'id,screen_name,can_see_all_posts'
            )
            if not result:
                return None

            if result[0].get('can_see_all_posts', False):
                return result[0].get('id', None)
            else:
                self.log.warning(
                    f"Posts of the group '{name}' are not accessible"
                )
        except ApiError:
            self.log.warning(f"Unable to access group {name}")

    def scrape_post_comments(
            self,
            group_identifier,
            post_identifier,
    ) -> List[dict]:
        try:
            return self._get_wall_comments(
                owner_id=group_identifier,
                post_id=post_identifier,
                count=self.comment_limit,
                extended=1,
                preview_length=0
            )['items']
        except ApiError:
            return []

    def _scrape_group(self, gid: int):
        collected, offset, oldest_ts = [], 0, None

        def is_enough():
            return len(collected) >= self.post_limit

        def can_fetch_more():
            return oldest_ts is None or oldest_ts > self.ts_start

        while not is_enough() and can_fetch_more():
            fetched = self._get_wall(
                owner_id=-gid, count=MAX_PER_WALL_PAGE, offset=offset
            ).get('items', [])
            if not fetched:
                break

            filtered = [
                i for i in fetched if self.ts_start < i['date'] < self.ts_end
            ]
            collected.extend(filtered)

            oldest_ts = fetched[-1]['date']
            offset += MAX_PER_WALL_PAGE

        return collected

    def scrape(self):
        # TODO: make it thread safe with locks/mutex/etc and parallelize
        #  (consider splitting groups into bins based on threads available)

        self.log.info('Applying town portal spell on all detected orcs...')
        for name in set(self._group_names):
            gid = self._resolve_group_id(name)
            if gid is None:
                continue

            self.log.info(f'Scraping group {gid} posts...')
            items = self._scrape_group(gid)
            self.log.info(f"Exporting group {gid}...")
            self.exporter.consume_group_posts(f'vk_{gid}', items)
