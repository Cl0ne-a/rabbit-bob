import asyncio
import json
from typing import Set, Optional, List

from pyrogram import Client, filters, idle
from pyrogram.types import Chat

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

        self.client = Client(
            name="tg_scraper",
            api_id=config['telegram']['api_id'],
            api_hash=config['telegram']['token'],
        )

        self._chats: List[Chat] = []
        self.post_limit = post_limit
        self.exporter = exporter
        self.group_list = group_list if group_list is not None else {}

    async def scrape_group_posts(self, gid: int):
        return [
            json.loads(str(msg))
            async for msg in self.client.get_chat_history(
                gid, limit=self.post_limit
            )
        ]

    async def _resolve_entity(self, name) -> Optional[Chat]:
        # noinspection PyBroadException
        try:
            result = await self.client.get_chat(name)
        except Exception:
            return None
        else:
            return result

    async def _resolve_group_chats(self):
        collected = await asyncio.gather(*[
            self._resolve_entity(name) for name in self.group_list
        ])
        self._chats.extend(filter(None.__ne__, collected))
        if not self._chats:
            print('No groups to scrape')
        else:
            self._subscribe_handlers()

    # noinspection PyUnusedLocal
    async def new_message_handler(self, client, message):
        self.exporter.consume_group_posts(
            f'tg_{message.chat.username}', [json.loads(str(message))]
        )

    def _subscribe_handlers(self):
        chat_ids = [c.id for c in self._chats]
        self.client.on_message(filters.chat(chats=chat_ids))(
            self.new_message_handler
        )

    async def scrape(self):
        await self.client.start()

        # TODO: make it thread safe with locks/mutex/etc and parallelize
        await self._resolve_group_chats()

        for chat in self._chats:
            scraped = await self.scrape_group_posts(chat.id)
            print(scraped[-1].get('text',''))
            self.exporter.consume_group_posts(
                f'tg_{chat.username}', list(scraped)
            )

        print('listening...')
        await idle()
        await self.client.stop()

