from typing import Protocol


class Exporter(Protocol):
    def consume_group_posts(self, *args, **kwargs):
        ...
