from telethon import TelegramClient

from base import Exporter


class TGScraper:
    def __init__(
            self, config: dict,
            exporter: Exporter = None,
            # lock: RLock = None, FIXME
            post_limit=1000,
    ):
        # self._lock = lock FIXME

        if 'telegram' not in config:
            raise ValueError('json config must contain "telegram" section')

        for mandatory in ['token', 'api_id']:
            if not config['telegram'].get(mandatory, False):
                raise ValueError(f'{mandatory} field must be provided')

        # TODO:
        #   fix logging in (2FA is annoying and is not fully automated)
        #   consider using bot token
        #   or checking out https://github.com/paulpierre/informer approach
        #   (masquerades as real user)
        # noinspection PyTypeChecker
        self._client = TelegramClient(
            session=None,
            api_id=config['telegram']['api_id'],
            api_hash=config['telegram']['token'],
        )

        self.post_limit = post_limit
        self.exporter = exporter

    def scrape_group_posts(self, gid):
        return map(
            lambda x: x.to_dict(),
            self._client.iter_messages(gid, limit=self.post_limit)
        )

    def scrape(self):
        self._client.start()
        chats = [d for d in self._client.iter_dialogs() if not d.is_user]
        # TODO:
        #  - implement chat filtering (takes all groups/chats at this moment)
        #  - make it thread safe with locks/mutex/etc
        #   (as the task can be parallelized)

        for chat in chats:
            scraped = self.scrape_group_posts(chat.name)
            self.exporter.consume_group_posts(chat.name, list(scraped))
        self._client.disconnect()
