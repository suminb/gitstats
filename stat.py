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

EMAIL = 'suminb@gmail.com'


def discover_repositories(root_path):
    repositories = []
    for root, dirs, files in os.walk(root_path):
        if os.path.exists('%s/.git' % root):
            logger.info('Git repository discovered: %s' % root)
            repositories.append(root)

    return repositories


def generate_git_log(path):
    abs_path = os.path.abspath(path)

    logger.info('Analyzing %s' % abs_path)
    return subprocess.check_output(['git', 'log', '--pretty=format:%an|%ae|%ad'], cwd=abs_path) + '\n'


def parse_log(log, year=2012):
    """
    :param log: raw log
    :type log: str
    """
    daily_commits_mine = {}
    daily_commits_others = {}

    for line in log.strip().split('\n'):
        # split columns
        name, email, timestamp = line.split('|')

        # parse datetime
        timestamp = parse_datetime(timestamp)

        # day of the year
        timetuple = timestamp.timetuple()
        if timetuple.tm_year == year:
            key = timetuple.tm_yday

            is_mine = email == EMAIL

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

    max_commits = max([max(daily_commits_mine.values()), max(daily_commits_others.values())])

    return {'year': year,
        'max_commits': max_commits,
        'daily_commits_mine': daily_commits_mine,
        'daily_commits_others': daily_commits_others}


def make_svg_report(log):
    """
    :param log: parsed log
    :type log: dict
    """

    def average_colors(color1, color2):
        return map(lambda x: x/2, map(sum, zip(color1, color2)))

    def make_colorcode(color):
        return '%02x%02x%02x' % tuple(color)

    print '<?xml version="1.0" encoding="utf-8"?>'
    print '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" ['
    print '  <!ENTITY st0 "fill-rule:evenodd;clip-rule:evenodd;fill:#000000;">'
    print '  <!ENTITY st1 "fill:#000000;">'
    print ']>'
    print '<svg version="1.0" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="667px" height="107px" viewBox="-10 -10 667 107" style="enable-background:new 0 0 667 107;" xml:space="preserve">'

    max_commits = log['max_commits']
    daily_commits_mine = log['daily_commits_mine']
    daily_commits_others = log['daily_commits_others']

    for week in range(52):
        print '<g transform="translate(%d, 0)">' % (week*12)
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

            density_mine = float(count_mine + 5) / (max_commits + 5) if count_mine > 0 else 0.0
            density_others = float(count_others + 5) / (max_commits + 5) if count_others > 0 else 0.0

            color_mine = (238 - density_mine*180, 238 - density_mine*140, 238)
            color_others = (238, 238 - density_others*180, 238 - density_others*140)

            print '<rect class="day" width="10px" height="10px" y="%d" style="fill: #%s"/>' \
                % (day*12, make_colorcode(average_colors(color_mine, color_others)))
        print '</g>'

    print '</svg>'

def main():
    repositories = discover_repositories(os.path.expanduser('~/dev'))

    log = ''
    for repo in repositories:
        log += generate_git_log(repo)

    parsed_log = parse_log(log)
    make_svg_report(parsed_log)


if __name__ == '__main__':
    main()
