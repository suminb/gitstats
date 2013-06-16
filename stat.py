from dateutil.parser import parse as parse_datetime

import subprocess
import os, sys
import logging

logger = logging.getLogger()


logger = logging.getLogger('gitstat')
#handler = logging.FileHandler('gitstat.log')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


REPOSITORIES = (
    '../hanja',
    '../labs',
    '../web',
    '../translator',
)

def generate_git_log(path):
    abs_path = os.path.abspath(path)

    logger.info('Analyzing %s' % abs_path)
    return subprocess.check_output(['git', 'log', '--pretty=format:%an|%ae|%ad'], cwd=abs_path) + '\n'


def parse_log(log):
    """
    :param log: raw log
    :type log: str
    """
    daily_commits = {}

    for line in log.strip().split('\n'):
        # split columns
        name, email, timestamp = line.split('|')

        # parse datetime
        timestamp = parse_datetime(timestamp)

        # day of the year
        timetuple = timestamp.timetuple()
        year = timetuple.tm_year
        yday = timetuple.tm_yday

        key = (year, yday)

        if not key in daily_commits:
            daily_commits[key] = 1
        else:
            daily_commits[key] += 1

    return daily_commits


def make_svg_report(log):
    """
    :param log: parsed log
    :type log: dict
    """

    print '<?xml version="1.0" encoding="utf-8"?>'
    print '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" ['
    print '  <!ENTITY st0 "fill-rule:evenodd;clip-rule:evenodd;fill:#000000;">'
    print '  <!ENTITY st1 "fill:#000000;">'
    print ']>'
    print '<svg version="1.0" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="667px" height="107px" viewBox="0 0 667 107" style="enable-background:new 0 0 667 107;" xml:space="preserve">'

    for week in range(52):
        print '<g transform="translate(%d, 0)">' % (week*12)
        for day in range(7):
            print '<rect class="day" width="10px" height="10px" y="%d" style="fill: #eeeeee"/>' % (day*12)
        print '</g>'

    print '</svg>'

def main():
    log = ''
    for repo in REPOSITORIES:
        log += generate_git_log(repo)

    parsed_log = parse_log(log)
    make_svg_report(parsed_log)


if __name__ == '__main__':
    main()
