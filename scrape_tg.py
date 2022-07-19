"""
TODO:
 - implement opportunity to subscribe on several channels
 - consider accepting images
 - consider having date filter (offset/depth)

"""
import json
import logging
import os
import sys
from argparse import ArgumentParser

from export.mongo import MongoTelegramExporter
from scrape.telegram import TGScraper

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


async def main(scraper_: TGScraper):
    await scraper_.scrape()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-C',
        dest='config', required=True,
        help='Config file with login credentials, export(db) settings, etc.'
    )
    parser.add_argument(
        '-G', '--group-file',
        dest='group_file', required=True,
        help='File with group identifiers. '
             'Identifiers can either be '
             't.me/joinchat/ link '
             'or username of the target channel/supergroup '
             '(in the format @username)'
    )
    parser.add_argument(
        '--posts-limit',
        type=int, default=1000,
        help='maximum amount of posts (latest) to scrape from single group'
    )
    args = parser.parse_args()

    if not os.path.exists(args.config):
        raise FileNotFoundError(args.config)

    group_names = {
        line.strip()
        for line in open(args.group_file).read().splitlines()
        if line
    }

    if not group_names:
        raise ValueError('No groups were provided')

    config = json.load(open(args.config))
    exporter = MongoTelegramExporter(config)
    scraper = TGScraper(
        config=config,
        group_list=group_names,
        exporter=exporter,
        post_limit=args.posts_limit
    )
    scraper.client.run(scraper.scrape())
