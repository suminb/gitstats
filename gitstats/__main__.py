import json
import os

import click

from gitstats import log
from gitstats.utils import (
    datetime_handler, discover_repositories, generate_git_log, make_svg_report,
    process_log, sort_by_year)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--email', help='My email address', multiple=True, required=True)
def analyze(path, email):
    """Analyzes Git repositories to generate a report in JSON format."""

    repositories = discover_repositories(os.path.expanduser(path))

    gitlogs = []
    for repo in repositories:
        try:
            gitlogs += generate_git_log(repo)
        except RuntimeError:
            log.warn('Not able to generate logs for {}', path)

    print(json.dumps(gitlogs, default=datetime_handler))


if __name__ == '__main__':
    cli()
