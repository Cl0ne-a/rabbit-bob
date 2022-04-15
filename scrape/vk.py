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
            comment_limit=1000
    ):
        # self._lock = lock FIXME

        if 'vk' not in config:
            raise ValueError('json config must contain "vk" section')

        for mandatory in ['login', 'token', 'app_id']:
            if not config['vk'].get(mandatory, False):
                raise ValueError(f'{mandatory} field must be provided')

        self.post_limit = post_limit
        self.comment_limit = comment_limit
        self.exporter = exporter
        self._group_list = group_list if group_list is not None else []
        self._group_names = group_names if group_names is not None else []

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
                        print(f"Posts of the group '{name}' aren't accessible")
                else:
                    print(f"Unable to resolve group '{name}' id")
            except ApiError:
                print(f"Unable to access group {name}")
                continue

    def scrape_group_posts(self, group_identifier) -> List[dict]:
        try:
            return self.api.wall.get(
                owner_id=group_identifier,
                count=self.post_limit,
                extended=1
            )['items']
        except ApiError:
            return []

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
        except ApiError:
            return []

    def scrape(self):
        self._resolve_group_ids()
        if not self._group_list:
            return

        # TODO: make it thread safe with locks/mutex/etc
        # TODO: as the task can be parallelized

        while self._group_list:
            gid = self._group_list.pop()
            scraped = self.scrape_group_posts(gid)
            self.exporter.consume_group_posts(gid, scraped)
