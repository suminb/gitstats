from dateutil.parser import parse as parse_datetime

import subprocess
import os, sys
import logging

logger = logging.getLogger()


logger = logging.getLogger('gitstat')
#handler = logging.FileHandler('gitstat.log')
handler = logging.StreamHandler(sys.stdout)
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
    return subprocess.check_output(['git', 'log', '--pretty=format:%an|%ae|%ad'], cwd=abs_path)


def parse_log(log):
    daily_commits = {}

    for line in log.split('\n'):
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


def main():
    for repo in REPOSITORIES:
        log = generate_git_log(repo)
        print parse_log(log)


if __name__ == '__main__':
    main()
