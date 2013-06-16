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
    '../base62',
    '../clare',
    '../gitstat',
    '../mendel',
    '../scalable-appliance',
    '../secondary-brain',

    '../../smartrek/smartrek-android',
    '../../smartrek/smartrek-experiments',
)

def generate_git_log(path):
    abs_path = os.path.abspath(path)

    logger.info('Analyzing %s' % abs_path)
    return subprocess.check_output(['git', 'log', '--pretty=format:%an|%ae|%ad'], cwd=abs_path) + '\n'


def parse_log(log, year=2012):
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
        if timetuple.tm_year == year:
            key = timetuple.tm_yday

            if not key in daily_commits:
                daily_commits[key] = 1
            else:
                daily_commits[key] += 1

    max_commits = max(daily_commits.values())

    return {'year': year,
        'max_commits': max_commits,
        'daily_commits': daily_commits}


def make_svg_report(log):
    """
    :param log: parsed log
    :type log: dict
    """

    def make_colorcode(color):
        return '%02x%02x%02x' % color

    print '<?xml version="1.0" encoding="utf-8"?>'
    print '<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.0//EN" "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd" ['
    print '  <!ENTITY st0 "fill-rule:evenodd;clip-rule:evenodd;fill:#000000;">'
    print '  <!ENTITY st1 "fill:#000000;">'
    print ']>'
    print '<svg version="1.0" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" width="667px" height="107px" viewBox="0 0 667 107" style="enable-background:new 0 0 667 107;" xml:space="preserve">'

    max_commits = log['max_commits']
    daily_commits = log['daily_commits']

    for week in range(52):
        print '<g transform="translate(%d, 0)">' % (week*12)
        for day in range(7):
            count = 0
            try:
                count = daily_commits[week*7 + day]
            except:
                pass

            density = float(count + 5) / (max_commits + 5) if count > 0 else 0.0

            color = (238 - density*180, 238 - density*140, 238)

            print '<rect class="day" width="10px" height="10px" y="%d" style="fill: #%s"/>' \
                % (day*12, make_colorcode(color))
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
