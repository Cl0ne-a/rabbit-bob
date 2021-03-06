import logging
from abc import abstractmethod

from pymongo import MongoClient


class MongoExporter:
    _DEFAULT_DB = 'chatters'

    def __init__(self, config: dict):
        self.log = logging.getLogger(name=type(self).__name__)
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
        group_collection = self._db.get_collection(gid)
        staged = self.filter_existing_posts(gid, posts)
        if staged:
            group_collection.insert_many(staged)
        else:
            self.log.info("All records are already exported"
                          "(or no records were provided)")

    @abstractmethod
    def filter_existing_posts(self, *args, **kwargs):
        ...


class MongoVKExporter(MongoExporter):
    def filter_existing_posts(self, gid, posts):
        group_collection = self._db.get_collection(gid)
        requested_ids = [p['id'] for p in posts]
        self.log.info(f"Posts collected: {requested_ids}")

        existing = {
            p['id']
            for p in group_collection.find({"id": {"$in": requested_ids}})
        }
        self.log.info(f"Ignoring(already exist): {existing}")

        staged = [p for p in posts if p['id'] not in existing]
        self.log.info(
            f"Posts staged to export: {[p['id'] for p in staged]}"
        )
        return staged


class MongoTelegramExporter(MongoVKExporter):
    def filter_existing_posts(self, gid, posts):
        group_collection = self._db.get_collection(gid)
        requested_ids = [p['id'] for p in posts]
        self.log.info(f"Posts collected: {requested_ids}")

        existing = {
            p['id']
            for p in group_collection.find({"id": {"$in": requested_ids}})
        }
        self.log.info(f"Ignoring(already exist): {existing}")
        staged = [p for p in posts if p['id'] not in existing]
        self.log.info(
            f"Posts staged to export: {[p['id'] for p in staged]}"
        )
        return staged
