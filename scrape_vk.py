import json
import re
import os.path
from argparse import ArgumentParser
from urllib.parse import urlparse

from export.mongo import MongoVKExporter
from scrape.vk import VKScraper

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        '-C',
        dest='config', required=True,
        help='config file with login credentials, export(db) settings, etc.'
    )
    parser.add_argument(
        '-G',
        dest='group_file', required=False,
        help='file with group id list'
    )
    parser.add_argument(
        '-g',
        nargs='+', default=[], type=int, dest='group_list', required=False,
        help='space separated list of group ids'
    )
    parser.add_argument(
        '--posts-limit',
        type=int, default=1000,
        help='maximum amount of posts (latest) to scrape from single group'
    )
    parser.add_argument(
        '--comments-limit',
        type=int, default=1000,
        help='maximum amount of comments (latest) '
             'to scrape from single group post'
    )

    args = parser.parse_args()

    # validate args
    if not os.path.exists(args.config):
        raise FileNotFoundError(args.config)

    if not args.group_file \
            and not args.group_list\
            and not args.city:
        raise ValueError('Either file (-G) or list (-g) of groups or city '
                         'must be specified')

    # fetch group_ids
    group_ids = set()
    group_names = set()
    if args.group_file:
        lines = [
            line.strip()
            for line in open(args.group_file).read().splitlines()
            if line
        ]
        for n, line in enumerate(lines):
            url = line if re.search(r'^(?:https?:)?//', line) else f'//{line}'
            path = urlparse(url).path
            assert path.count('/') == 1, \
                f"(Line: {n:04d})Invalid group link: {line}. " \
                f"Correct format: http://vk.com/groupname"
            short_name = path.split('/')[-1]
            group_names.add(short_name)

        if not group_ids and not group_names:
            raise ValueError('No groups were provided')

    group_ids.update(args.group_list)
    config = json.load(open(args.config))
    exporter = MongoVKExporter(config)
    scraper = VKScraper(
        config=config,
        exporter=exporter,
        group_list=group_ids,
        group_names=group_names,
        post_limit=args.posts_limit,
        comment_limit=args.comments_limit,
    )
    scraper.scrape()
