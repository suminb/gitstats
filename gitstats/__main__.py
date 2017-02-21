import os
# import StringIO

import click

from gitstats import logger
from gitstats.utils import (
    discover_repositories, generate_git_log, make_svg_report, process_log,
    sort_by_year)


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--year', type=str, help='Specify a year or \'all\'')
@click.option('--out')
def analyze(path, year, out):
    repositories = discover_repositories(os.path.expanduser(path))

    logs = []
    for repo in repositories:
        try:
            logs += generate_git_log(repo)
        except RuntimeError:
            logger.warn('Not able to generate logs for {}', repo)

    log_by_year = sort_by_year(logs)

    max_commits = []
    for y in log_by_year:
        data = process_log(log_by_year[y], y)
        max_commits.append(data['max_commits'])

    if not year:
        year = y
    else:
        year = int(year)
    global_max = max(max_commits)
    processed_logs = process_log(log_by_year[year], year)
    logger.info('Generating report for year {}'.format(year))
    if out:
        with open(out, 'w') as fout:
            make_svg_report(processed_logs, global_max, fout)
    else:
        make_svg_report(processed_logs, global_max)

if __name__ == '__main__':
    cli()
