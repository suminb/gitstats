import sys

from logbook import Logger, StreamHandler

__author__ = 'Sumin Byeon'
__email__ = 'suminb@gmail.com'
__version__ = '0.2.4'


StreamHandler(sys.stderr).push_application()
log = Logger(__name__)
