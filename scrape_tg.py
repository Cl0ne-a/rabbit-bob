"""
TODO:
 - implement opportunity to subscribe on several channels
 - consider accepting images
 - consider having date filter (offset/depth)

"""

import json
import logging
import os
import re
import sys
from argparse import ArgumentParser
from urllib.parse import urlparse

from export.mongo import MongoTelegramExporter
from scrape.telegram import TGScraper

logging.basicConfig(level=logging.INFO, stream=sys.stdout)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-C',
        dest='config', required=True,
        help='config file with login credentials, export(db) settings, etc.'
    )
    parser.add_argument(
        '-G', '--group-file',
        dest='group_file', required=False,
        help='file with group links'
    )
    parser.add_argument(
        '--posts-limit',
        type=int, default=1000,
        help='maximum amount of posts (latest) to scrape from single group'
    )
    args = parser.parse_args()

    if not os.path.exists(args.config):
        raise FileNotFoundError(args.config)

    group_names = set()
    if args.group_file:
        lines = [
            line.strip()
            for line in open(args.group_file).read().splitlines()
            if line
        ]

        for n, line in enumerate(lines):
            if line.startswith("@"):
                group_names.add(line)
            else:
                re_link = re.compile(r'^(?:https?:)?//')
                url = line if re_link.search(line) else f'//{line}'
                path = urlparse(url).path
                assert path.count('/') == 1, \
                    f"(Line: {n:04d})Invalid group link: {line}. " \
                    f"Correct format: http://t.me/groupname"
                short_name = path.split('/')[-1]
                group_names.add(short_name)

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
    scraper.scrape()
