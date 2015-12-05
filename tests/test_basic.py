from gitstats import generate_git_log, parse_log_row


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
    assert len(columns) == 3
