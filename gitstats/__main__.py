import subprocess
import os
# import StringIO
import sys
import logging

import click
from dateutil.parser import parse as parse_datetime

from gitstats import __email__


logger = logging.getLogger('gitstat')
# handler = logging.FileHandler('gitstat.log')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def discover_repositories(root_path):
    """Discover git repositories under a given directory, excluding repositores
    that contain a .exclude file."""

    repositories = []
    for root, dirs, files in os.walk(root_path):
        if os.path.exists(os.path.join(root, '.git')) and \
                not os.path.exists(os.path.join(root, '.exclude')):
            logger.info('Git repository discovered: {}'.format(root))
            repositories.append(root)

    return repositories


def generate_git_log(path, format='format:%an|%ae|%ad'):
    """Get the entire commit logs in a raw string for a given repository.

    :param path: an absolute or relative path of a git repository
    """
    abs_path = os.path.abspath(path)

    logger.info('Analyzing %s' % abs_path)
    log_rows = subprocess.check_output(
        ['git', 'log', '--pretty={}'.format(format)],
        cwd=abs_path).decode('utf-8')

    return [parse_log_row(row) for row in log_rows.strip().split('\n')]


def process_log(logs, year):
    """Filters out logs by the given year.

    :param logs: A list of (name, email, datetime) tuples
    :type logs: list

    :type year: int

    :return:
        A dictionary containing information required to draw a commit graph.
    :rtype: dict
    """
    daily_commits_mine = {}
    daily_commits_others = {}

    for log in logs:
        email = log[1]
        timetuple = log[2].timetuple()
        if timetuple.tm_year == year:
            key = timetuple.tm_yday

            # TODO: Make it more general...
            is_mine = email == __email__

            if is_mine:
                if key not in daily_commits_mine:
                    daily_commits_mine[key] = 1
                else:
                    daily_commits_mine[key] += 1
            else:
                if key not in daily_commits_others:
                    daily_commits_others[key] = 1
                else:
                    daily_commits_others[key] += 1

    # Calculate the maximum number of commits
    max_commits = 0

    if daily_commits_mine:
        max_commits = max(max_commits, max(daily_commits_mine.values()))

    if daily_commits_others:
        max_commits = max(max_commits, max(daily_commits_others.values()))

    return {'year': year,
            'max_commits': max_commits,
            'daily_commits_mine': daily_commits_mine,
            'daily_commits_others': daily_commits_others}


def parse_log_row(row):
    columns = row.strip().split('|')
    return columns[0], columns[1], parse_datetime(columns[2])


def sort_by_year(log):
    """
    :param log: parsed log
    :type log: list
    """
    basket = {}
    for r in log:
        name, email, timestamp = r

        timetuple = timestamp.timetuple()
        year = timetuple.tm_year

        if year in basket:
            basket[year].append(r)
        else:
            basket[year] = [r]

    return basket


def average_color(color1, color2):
    """Takes two RGB color tuples to calculate their average.

    :param color1: An RGB tuple
    :param color2: An RGB tuple
    :return: An RGB tuple
    """
    return tuple(map(lambda x: int(x / 2), map(sum, zip(color1, color2))))


def make_colorcode(color):
    """Makes a hexadecimal string representation of a color tuple.

    :param color: An RGB tuple
    """
    return '%02x%02x%02x' % color


def make_svg_report(log, global_max, out=sys.stdout):
    """
    :param log: parsed log for a particular year
    :type log: dict

    :param global_max: global maximum of the number of commits at any given day
    :type global_max: int
    """

    out.write('<?xml version="1.0" encoding="utf-8"?>\n')
    out.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [\n')
    out.write('  <!ENTITY st0 "fill-rule:evenodd;clip-rule:evenodd;fill:#000000;">\n')
    out.write('  <!ENTITY st1 "fill:#000000;">\n')
    out.write(']>\n')
    out.write('<svg version="1.0" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="667px" height="107px" viewBox="-10 -10 667 107" style="enable-background:new 0 0 667 107;" xml:space="preserve">\n')

    daily_commits_mine = log['daily_commits_mine']
    daily_commits_others = log['daily_commits_others']

    # Gives clear distinction between no-commit day and a day with at least one
    # commit
    density_offset = global_max * 0.25

    for week in range(52):
        out.write('<g transform="translate(%d, 0)">' % (week * 12))
        for day in range(7):
            count_mine, count_others = 0, 0
            try:
                count_mine = daily_commits_mine[week * 7 + day]
            except:
                pass
            try:
                count_others = daily_commits_others[week * 7 + day]
            except:
                pass

            denominator = float(global_max + density_offset)

            density_mine = (count_mine + density_offset) / denominator \
                if count_mine > 0 else 0.0
            density_others = (count_others + density_offset) / denominator \
                if count_others > 0 else 0.0

            color_mine = (238 - density_mine * 180, 238 - density_mine * 140, 238)
            color_others = (238, 238 - density_others * 180, 238 - density_others * 140)

            out.write('<rect class="day" width="10px" height="10px" y="%d" style="fill: #%s"/>' \
                % (day * 12, make_colorcode(average_color(color_mine, color_others))))
        out.write('</g>')

    out.write('</svg>')


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
        logs += generate_git_log(repo)

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
