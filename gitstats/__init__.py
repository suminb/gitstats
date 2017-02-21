import sys
import logging

__author__ = 'Sumin Byeon'
__email__ = 'suminb@gmail.com'
__version__ = '0.2.0'


# TODO: Name the following variable as `log`
logger = logging.getLogger('gitstats')
# handler = logging.FileHandler('gitstats.log')
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(
    logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
