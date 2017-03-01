import json
import os

import click
from dateutil.parser import parse as parse_datetime

from gitstats import log
from gitstats.utils import (
    datetime_handler, discover_repositories, generate_git_log, make_svg_report,
    get_annual_data, sort_by_year)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
def analyze(path):
    """Analyzes Git repositories to generate a report in JSON format."""

    repositories = discover_repositories(os.path.expanduser(path))

    gitlogs = []
    for repo in repositories:
        try:
            gitlogs += generate_git_log(repo)
        except RuntimeError:
            log.warn('Not able to generate logs for {}', path)

    print(json.dumps(gitlogs, default=datetime_handler))


@cli.command()
@click.argument('json_input', type=click.File('r'))
@click.argument('year', type=int)
@click.option('--email', help='My email address', multiple=True, required=True)
def generate_graph(json_input, year, email):
    """Generates an annual commit graph in .svg format."""

    gitlogs = json.loads(json_input.read())
    gitlogs = [(x, y, parse_datetime(z)) for x, y, z in gitlogs]

    gitlogs_by_year = sort_by_year(gitlogs)
    annual_data = {}
    for y, l in gitlogs_by_year.items():
        annual_data[y] = get_annual_data(l, y, email)

    global_max = max([x['max_commits'] for x in annual_data.values()])

    log.info('Generating report for year {}', year)
    make_svg_report(annual_data[year], global_max)


if __name__ == '__main__':
    cli()
