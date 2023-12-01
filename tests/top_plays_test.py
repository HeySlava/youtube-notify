import re

import pytest

from testing import util
from top_plays import _make_message
from top_plays import _parse_output
from top_plays import Video


@pytest.mark.parametrize(
        'url,tag,expected',
        [
            ('https://bla_bla.com', 'NBA', 'https://bla_bla.com\n\n#NBA'),
            ('https://video.com', 'NBA', 'https://video.com\n\n#NBA'),
        ]
    )
def test_make_message(url, tag, expected):
    assert _make_message(url, tag) == expected


@pytest.mark.parametrize(
        'output,pattern,expected',
        [
            (
                util.path_to_resource('NBA_raw.txt').read_text(),
                re.compile(r"NBA's Top \d+ Plays Of The Night"),
                set(
                    (
                        Video(
                            url='https://www.youtube.com/watch?v=Kws_FSbcMbY',
                            title="NBA's Top 10 Plays Of The Night ｜ November 29, 2023",  # noqa: E501
                        ),
                        Video(
                            url='https://www.youtube.com/watch?v=YjIPRN9sUR8',
                            title="NBA's Top 10 Plays Of The Night ｜ November 28, 2023",  # noqa: E501
                        ),
                    ),
                ),
            )
        ]
    )
def test_parse_output(output, pattern, expected):
    assert sorted(_parse_output(pattern, output)) == sorted(expected)
