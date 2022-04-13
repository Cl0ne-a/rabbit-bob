from abc import abstractmethod

from pymongo import MongoClient


class MongoExporter:
    _DEFAULT_DB = 'chatters'

    def __init__(self, config: dict):
        if 'mongo' not in config:
            raise ValueError('json config must contain "mongo" section')
        else:
            config = config

        for mandatory in ['uri']:
            if not config['mongo'].get(mandatory, False):
                raise ValueError(f'{mandatory} field must be provided')

        self.__mongo_client = MongoClient(config['mongo']['uri'])
        self._db = self.__mongo_client.get_database(
            config['mongo'].get('db_name', self._DEFAULT_DB)
        )

    def consume_group_posts(self, gid, posts):
        group_collection = self._db.get_collection(str(gid))
        group_collection.insert_many(self.filter_existing_posts(gid, posts))

    @abstractmethod
    def filter_existing_posts(self, *args, **kwargs):
        ...


class MongoVKExporter(MongoExporter):
    def filter_existing_posts(self, gid, posts):
        requested = {"id": {"$in": [p['id'] for p in posts]}}
        group_collection = self._db.get_collection(str(gid))
        existing = {p['id'] for p in group_collection.find(requested)}

        return [p for p in posts if p['id'] not in existing]
