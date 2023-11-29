import pytest

from top_plays import _make_message


@pytest.mark.parametrize(
        'url,tag,expected',
        [
            ('https://bla_bla.com', 'NBA', 'https://bla_bla.com\n\n#NBA'),
            ('https://video.com', 'NBA', 'https://video.com\n\n#NBA'),
        ]
    )
def test_make_message(url, tag, expected):
    assert _make_message(url, tag) == expected
