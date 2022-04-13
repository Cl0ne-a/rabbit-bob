from abc import ABC, abstractmethod


class Exporter(ABC):

    @abstractmethod
    def save_record(self, *args, **kwargs):
        ...
