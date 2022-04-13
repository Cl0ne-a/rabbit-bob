import json
import os.path
from argparse import ArgumentParser

from scrape.vk import VKScraper, VKStdoutExporter

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
        default=1000,
        help='maximum amount of posts (latest) to scrape from single group'
    )
    parser.add_argument(
        '--comments-limit',
        default=1000,
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
    if args.group_file:
        lines = [
            line.strip()
            for line in open(args.group_file).read().splitlines()
            if line
        ]
        for line in lines:
            try:
                group_ids.add(int(line))
            except ValueError:
                continue
        if not group_ids:
            raise ValueError('File does not contain any group ids')

    group_ids.update(args.group_list)
    config = json.load(open(args.config))

    vs = VKScraper(
        config=config,
        exporter=VKStdoutExporter(),
        group_list=group_ids,
        post_limit=args.posts_limit,
        comment_limit=args.comments_limit,
    )
    vs.scrape()
