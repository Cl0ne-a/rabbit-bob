import json
import os
from argparse import ArgumentParser

from export.mongo import MongoTelegramExporter
from scrape.telegram import TGScraper


if __name__ == '__main__':
    # TODO: consider having date filter
    #  (tg api provides convenient search by date offset)
    parser = ArgumentParser()
    parser.add_argument(
        '-C',
        dest='config', required=True,
        help='config file with login credentials, export(db) settings, etc.'
    )
    parser.add_argument(
        '--posts-limit',
        type=int, default=1000,
        help='maximum amount of posts (latest) to scrape from single group'
    )
    args = parser.parse_args()

    if not os.path.exists(args.config):
        raise FileNotFoundError(args.config)

    config = json.load(open(args.config))
    exporter = MongoTelegramExporter(config)
    scraper = TGScraper(
        config=config,
        exporter=exporter,
        post_limit=args.posts_limit
    )
    scraper.scrape()
