import logging
from collections import defaultdict
from datetime import datetime
from typing import List

import vk_api
from vk_api import VkUserPermissions, ApiError

from base import Exporter


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

    def _resolve_group_ids(self):
        self.log.info('Solving group ids from provided links...')

        for name in set(self._group_names):
            try:
                result = self.api.groups.getById(
                    group_id=name, fields=f'id,screen_name,can_see_all_posts'
                )
                is_accessible = result[0].get('can_see_all_posts', False)
                is_same_group = result[0].get('screen_name', None) == name

                if is_same_group:
                    if is_accessible:
                        self._group_list.add(result[0]['id'])
                    else:
                        self.log.warning(
                            f"Posts of the group '{name}' are not accessible"
                        )
                else:
                    self.log.warning(f"Unable to resolve group '{name}' id")
            except ApiError as e:
                self.log.error(e, exc_info=True)
                self.log.warning(f"Unable to access group {name}")
                continue

    def scrape_post_comments(
            self,
            group_identifier,
            post_identifier,
    ) -> List[dict]:
        try:
            return self.api.wall.getComments(
                owner_id=group_identifier,
                post_id=post_identifier,
                count=self.comment_limit,
                extended=1,
                preview_length=0
            )['items']
        except ApiError as e:
            self.log.error(e, exc_info=True)
            return []

    def _scrape_groups(self, *group_ids: int):
        self.log.info('Applying town portal spell on all detected orcs...')

        def to_group_id(value: int) -> str:
            return f'g{value}'

        joined_ids = ','.join(map(to_group_id, group_ids))

        self.log.info('Calculating time constraints...')
        time_constraints = dict()
        if self.ts_start is not None:
            time_constraints['start_time'] = self.ts_start
        if self.ts_end is not None:
            time_constraints['end_time'] = self.ts_end
        self.log.info(
            f'start: {datetime.fromtimestamp(self.ts_start)}; '
            f'end: {datetime.fromtimestamp(self.ts_end)}'
        )

        self.log.info('Scraping group posts...')
        return self.api.newsfeed.get(
            filters='post',
            source_ids=joined_ids,
            **time_constraints
        )['items']

    def scrape(self):
        self._resolve_group_ids()
        res = self.api.groups.get()
        import pprint
        pprint.pprint(res)
        exit(0)

        if not self._group_list:
            self.log.error('No groups to scrape')
            return

        # TODO: make it thread safe with locks/mutex/etc and parallelize
        #  (consider splitting groups into bins based on threads available)

        scraped = self._scrape_groups(*self._group_list)

        staged = defaultdict(list)
        for item in scraped:
            staged[item.get('source_id', 'source_unknown')].append(item)

        for gid, items in staged.items():
            self.log.info(f"Exporting group {gid}...")
            self.exporter.consume_group_posts(f'vk_{gid}', items)
