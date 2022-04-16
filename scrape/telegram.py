import asyncio
from typing import Set, Optional

from telethon import TelegramClient, events
from telethon.hints import EntityLike

from base import Exporter


class TGScraper:
    def __init__(
            self, config: dict,
            group_list: Set[str] = None,
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

        self._client = TelegramClient(
            session='TG_Scraper',
            api_id=config['telegram']['api_id'],
            api_hash=config['telegram']['token'],
        )

        self._chats = []
        self.post_limit = post_limit
        self.exporter = exporter
        self.group_list = group_list if group_list is not None else {}

    def scrape_group_posts(self, gid):
        return map(
            lambda x: x.to_dict(),
            self._client.iter_messages(gid, limit=self.post_limit)
        )

    async def _resolve_entity(self, name) -> Optional[EntityLike]:
        # noinspection PyBroadException
        try:
            result = await self._client.get_entity(name)
        except Exception:
            return None
        else:
            return result

    def _resolve_group_chats(self):
        collected = asyncio.get_event_loop().run_until_complete(
            asyncio.gather(*[
                self._resolve_entity(name) for name in self.group_list
            ])
        )
        self._chats.extend([e for e in collected if e is not None])
        if not self._chats:
            print('No groups to scrape')
        else:
            self._subscribe_handlers()

    async def new_message_handler(self, event):
        who = await self._client.get_entity(event.message.from_id)
        self.exporter.consume_group_posts(
            f'tg_{who.username}', [event.message.to_dict()]
        )

    def _subscribe_handlers(self):
        chat_ids = [chat.id for chat in self._chats]
        self._client.on(events.NewMessage(chats=chat_ids))(
            self.new_message_handler
        )

    def scrape(self):
        self._client.start()
        # TODO: make it thread safe with locks/mutex/etc and parallelize
        self._resolve_group_chats()

        for chat in self._chats:
            scraped = self.scrape_group_posts(chat.username)
            self.exporter.consume_group_posts(
                f'tg_{chat.username}', list(scraped)
            )
        print('listening...')
        self._client.run_until_disconnected()
