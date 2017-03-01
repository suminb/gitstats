from datetime import datetime
import os
import subprocess
import sys

from dateutil.parser import parse as parse_datetime
from gitstats import log


def datetime_handler(d):
    if isinstance(d, datetime):
        return d.isoformat()
    raise TypeError('Unknown type')


def discover_repositories(root_path):
    """Discover git repositories under a given directory, excluding repositores
    that contain a .exclude file."""

    repositories = []
    for root, dirs, files in os.walk(root_path):
        if os.path.exists(os.path.join(root, '.git')) and \
                not os.path.exists(os.path.join(root, '.exclude')):
            log.info('Git repository discovered: {}'.format(root))
            repositories.append(root)

    return repositories


def generate_git_log(path, format='format:%an|%ae|%ad'):
    """Get the entire commit logs in a raw string for a given repository.

    NOTE: We would like to use the `%aI` format (strict ISO 8601 format) for
    author dates, but it appears that Git 1.8.4, which is installed on Travis
    CI by default, does not support it.  So we will fallback to `%ad` for now.

    :param path: an absolute or relative path of a git repository
    """
    abs_path = os.path.abspath(path)

    log.info('Analyzing %s' % abs_path)
    command = ['git', 'log', '--pretty={}'.format(format)]
    try:
        log_rows = subprocess.check_output(
            command, cwd=abs_path).decode('utf-8')
    except subprocess.CalledProcessError:
        raise RuntimeError('Git command failed: {}'.format(command))

    return [parse_log_row(row) for row in log_rows.strip().split('\n')]


def get_annual_data(gitlogs, year, my_emails):
    """Filters out git logs by the given year.

    :param gitlogs: A list of (name, email, datetime) tuples
    :type gitlogs: list

    :type year: int

    :param my_emails: A list of email addresses
    :type my_emails: list

    :return:
        A dictionary containing information required to draw a commit graph.
    :rtype: dict
    """
    daily_commits_mine = {}
    daily_commits_others = {}

    for gitlog in gitlogs:
        email = gitlog[1]
        timetuple = gitlog[2].timetuple()
        if timetuple.tm_year == year:
            yday = timetuple.tm_yday

            is_mine = email in my_emails

            if is_mine:
                if yday not in daily_commits_mine:
                    daily_commits_mine[yday] = 1
                else:
                    daily_commits_mine[yday] += 1
            else:
                if yday not in daily_commits_others:
                    daily_commits_others[yday] = 1
                else:
                    daily_commits_others[yday] += 1

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


def sort_by_year(gitlog):
    """
    :param gitlog: parsed gitlog
    :type gitlog: list
    """
    basket = {}
    for r in gitlog:
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


def make_svg_report(gitlog, global_max, out=sys.stdout):
    """
    :param gitlog: parsed gitlog for a particular year
    :type gitlog: dict

    :param global_max: global maximum of the number of commits at any given day
    :type global_max: int
    """

    svg_epilogue = """
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN"
      "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [
      <!ENTITY st0 "fill-rule:evenodd;clip-rule:evenodd;fill:#000000;">
      <!ENTITY st1 "fill:#000000;">
    ]>
    <svg version="1.0" id="Layer_1" xmlns="http://www.w3.org/2000/svg"
      xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px"
      width="667px" height="107px"
      viewBox="-10 -10 667 107"
      style="enable-background:new 0 0 667 107;"
      xml:space="preserve">
    """.strip()

    out.write(svg_epilogue)

    daily_commits_mine = gitlog['daily_commits_mine']
    daily_commits_others = gitlog['daily_commits_others']

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

            color_mine = (
                238 - density_mine * 180,
                238 - density_mine * 140,
                238)
            color_others = (
                238,
                238 - density_others * 180,
                238 - density_others * 140)

            rect = """
            <rect class="day" width="10px" height="10px" y="%d"
              style="fill: #%s"/>
            """ % (day * 12,
                   make_colorcode(average_color(color_mine, color_others)))
            out.write(rect.strip())
        out.write('</g>')

    out.write('</svg>')
