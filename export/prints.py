
class StdoutExporter:
    """Simple example of exporting data to standard output"""
    @staticmethod
    def consume_group_posts(gid, posts):
        for item in posts:
            print(f'[{gid}/{item["id"]}] {item["text"]:.50s}...')
