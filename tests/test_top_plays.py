import pytest

from top_plays import _make_message


@pytest.mark.parametrize(
        'url,expected',
        [
            ('https://bla_bla.com', 'https://bla_bla.com\n\n#NBA'),
            ('https://video.com', 'https://video.com\n\n#NBA'),
        ]
    )
def test_make_message(url, expected):
    assert _make_message(url) == expected
