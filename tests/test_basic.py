from datetime import datetime

from gitstats import average_color, generate_git_log, parse_log_row, \
    process_log, sort_by_year


def validate_log_row(columns):
    """
    :param columns: (name, email, datetime) tuple
    """
    assert len(columns) == 3
    for i in [0, 1]:
        try:
            # For Python 2.x
            assert isinstance(columns[i], basestring)
        except NameError:
            assert isinstance(columns[i], str)

    assert isinstance(columns[2], datetime)


def test_generate_git_log():
    """Ensures generate_git_log() works as intended."""

    # Extract logs for the current repository
    logs = generate_git_log('.')
    assert len(logs) > 0
    assert len(logs[0]) == 3


def test_parse_log_row():
    """Ensures parse_log_row() works as intended."""

    log = 'John Doe|john.doe@gmail.com|Sat Dec 5 17:10:45 2015 +0900'
    columns = parse_log_row(log)
    validate_log_row(columns)


def test_sort_by_year():
    """Ensures sort_by_year() works as intended."""

    # Extract logs for the current repository
    logs = generate_git_log('.')
    sorted_logs = sort_by_year(logs)
    years = sorted_logs.keys()

    assert 2012 not in years
    assert 2013 in years
    assert 2014 not in years
    assert 2015 in years

    for year in (2013, 2015):
        for row in sorted_logs[year]:
            validate_log_row(row)


def test_process_log():
    """Ensures process_log() works as intended."""

    # Extract logs for the current repository
    logs = generate_git_log('.')
    logs2013 = process_log(logs, 2013)
    assert logs2013['year'] == 2013
    assert logs2013['daily_commits_mine']
    assert logs2013['daily_commits_others'] == {}
    assert logs2013['max_commits'] > 0


def test_average_color():
    """Ensures average_color() works as intended."""
    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)
    assert (127, 127, 0) == average_color(red, green)
    assert (127, 0, 127) == average_color(red, blue)
    assert (0, 127, 127) == average_color(green, blue)
