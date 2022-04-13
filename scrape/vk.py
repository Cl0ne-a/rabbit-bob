from typing import List
import vk_api
from vk_api import VkUserPermissions

from base import Exporter


# TODO: remove when not needed
class VKStdoutExporter(Exporter):
    """Simple example of exporting data to standard output"""
    def save_record(self, items, *args, **kwargs):
        for item in items:
            print(f'[{item["owner_id"]}/{item["id"]}] {item["text"][:50]}...')


class VKScraper:
    def __init__(
            self, config: dict,
            exporter: Exporter = None,
            # lock: RLock = None, FIXME
            group_list=None,
            post_limit=1000,
            comment_limit=1000
    ):
        # self._lock = lock FIXME

        for mandatory in ['login', 'token', 'app_id']:
            if not config.get('login', False):
                raise ValueError(f'{mandatory} field must be provided')

        self.post_limit = post_limit
        self.comment_limit = comment_limit
        self.exporter = exporter
        self._group_list = group_list if group_list is not None else []

        self.__session = vk_api.VkApi(
            login=config['login'],
            token=config['token'],
            app_id=config['app_id'],
            scope=sum(VkUserPermissions) - VkUserPermissions.MESSAGES
        )
        # noinspection PyProtectedMember
        self.__session._auth_token()
        self.api = self.__session.get_api()

    def scrape_group_posts(self, group_identifier,) -> List[dict]:
        scraped = self.api.wall.get(
            owner_id=group_identifier,
            count=self.post_limit,
            extended=1
        )

        return scraped['items']

    def scrape_post_comments(
            self,
            group_identifier,
            post_identifier,
    ) -> List[dict]:
        scraped = self.api.wall.getComments(
            owner_id=group_identifier,
            post_id=post_identifier,
            count=self.comment_limit,
            extended=1,
            preview_length=0
        )
        return scraped['items']

    def scrape(self):
        if not self._group_list:
            return

        # TODO: make it thread safe with locks/mutex/etc
        # TODO: as the task can be parallelized

        while self._group_list:
            gid = self._group_list.pop()
            scraped = self.scrape_group_posts(gid)
            # for post in scraped:
            #     pid = post['id']
            #     comments = self.scrape_post_comments(gid, pid)
            self.exporter.save_record(scraped)
