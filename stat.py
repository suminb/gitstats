__author__ = 'Sumin Byeon'
__email__ = 'suminb@gmail.com'
__version__ = '0.1.1'

from dateutil.parser import parse as parse_datetime

import subprocess
import os, sys
import logging

logger = logging.getLogger('gitstat')
#handler = logging.FileHandler('gitstat.log')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


def discover_repositories(root_path):
    """Discover git repositories under a given directory, excluding repositores
    that contain a .exclude file."""

    repositories = []
    for root, dirs, files in os.walk(root_path):
        if os.path.exists('%s/.git' % root) and not os.path.exists('%s/.exclude' % root):
            logger.info('Git repository discovered: %s' % root)
            repositories.append(root)

    return repositories


def generate_git_log(path):
    """
    :param path: an absolute or relative path of a git repository
    """
    abs_path = os.path.abspath(path)

    logger.info('Analyzing %s' % abs_path)
    return subprocess.check_output(['git', 'log',
        '--pretty=format:%an|%ae|%ad'], cwd=abs_path) + '\n'


def process_log(logs, year):
    daily_commits_mine = {}
    daily_commits_others = {}

    for log in logs:
        email = log[1]
        timetuple = log[2].timetuple()
        if timetuple.tm_year == year:
            key = timetuple.tm_yday

            is_mine = email == __email__

            if is_mine:
                if not key in daily_commits_mine:
                    daily_commits_mine[key] = 1
                else:
                    daily_commits_mine[key] += 1
            else:
                if not key in daily_commits_others:
                    daily_commits_others[key] = 1
                else:
                    daily_commits_others[key] += 1

    max_commits = max([0] + daily_commits_mine.values() + daily_commits_others.values())

    return {'year': year,
        'max_commits': max_commits,
        'daily_commits_mine': daily_commits_mine,
        'daily_commits_others': daily_commits_others}


def parse_log(log):
    """
    :param log: raw log
    :type log: str
    """
    return map(lambda x: [x[0], x[1], parse_datetime(x[2])], \
        [line.split('|') for line in log.strip().split('\n')])


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


def make_svg_report(log, global_max, out=sys.stdout):
    """
    :param log: parsed log
    :type log: dict
    :param global_max: global maximum of the number of commits at any given day
    """

    def average_colors(color1, color2):
        """
        :param color1: RGB tuple
        :param color2: RGB tuple
        """
        return map(lambda x: x/2, map(sum, zip(color1, color2)))

    def make_colorcode(color):
        """
        :param color: RGB tuple
        """
        return '%02x%02x%02x' % tuple(color)

    out.write('<?xml version="1.0" encoding="utf-8"?>\n')
    out.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" [\n')
    out.write('  <!ENTITY st0 "fill-rule:evenodd;clip-rule:evenodd;fill:#000000;">\n')
    out.write('  <!ENTITY st1 "fill:#000000;">\n')
    out.write(']>\n')
    out.write('<svg version="1.0" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="667px" height="107px" viewBox="-10 -10 667 107" style="enable-background:new 0 0 667 107;" xml:space="preserve">\n')

    daily_commits_mine = log['daily_commits_mine']
    daily_commits_others = log['daily_commits_others']

    # Gives clear distinction between no-commit day and a day with at least one commit
    density_offset = global_max * 0.25

    for week in range(52):
        out.write('<g transform="translate(%d, 0)">' % (week*12))
        for day in range(7):
            count_mine, count_others = 0, 0
            try:
                count_mine = daily_commits_mine[week*7 + day]
            except:
                pass
            try:
                count_others = daily_commits_others[week*7 + day]
            except:
                pass

            density_mine = float(count_mine + density_offset) / (global_max + density_offset) \
                if count_mine > 0 else 0.0
            density_others = float(count_others + density_offset) / (global_max + density_offset) \
                if count_others > 0 else 0.0

            color_mine = (238 - density_mine*180, 238 - density_mine*140, 238)
            color_others = (238, 238 - density_others*180, 238 - density_others*140)

            out.write('<rect class="day" width="10px" height="10px" y="%d" style="fill: #%s"/>' \
                % (day*12, make_colorcode(average_colors(color_mine, color_others))))
        out.write('</g>')

    out.write('</svg>')


def main():
    repositories = discover_repositories(os.path.expanduser(argv[1]))

    log = ''
    for repo in repositories:
        log += generate_git_log(repo)

    parsed_log = parse_log(log)
    log_by_year = sort_by_year(parsed_log)

    max_commits = []
    for year in log_by_year:
        data = process_log(log_by_year[year], year)
        max_commits.append(data['max_commits'])

    global_max = max(max_commits)

    # NOTE: Inefficient, but works
    for year in log_by_year:
        data = process_log(log_by_year[year], year)
        with open('%d.svg' % year, 'w') as f:
            logger.info('Generating report for year %d' % year)
            make_svg_report(data, global_max, f)


if __name__ == '__main__':
    main()
