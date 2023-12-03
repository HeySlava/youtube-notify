import re

import pytest

from testing import util
from top_plays import _make_message
from top_plays import _parse_output
from top_plays import escape
from top_plays import Playlist
from top_plays import Video


@pytest.mark.parametrize(
        'video,expected',
        [
            (
                Video(
                    url='https://bla_bla.com',
                    tag='NBA',
                    title='some title',
                ),
                '<a href="https://bla_bla.com">some title</a>\n\n#NBA',
            ),
        ]
    )
def test_make_message(video, expected):
    assert _make_message(video) == expected


@pytest.mark.parametrize(
        'output,playlist,expected',
        [
            (
                util.path_to_resource('NBA_raw.txt').read_text(),
                Playlist(
                    pattern=re.compile(r"NBA's Top \d+ Plays Of The Night"),
                    url='fake_url',
                    tag='fiba',
                ),
                set(
                    (
                        Video(
                            url='https://www.youtube.com/watch?v=Kws_FSbcMbY',
                            title="NBA's Top 10 Plays Of The Night ｜ November 29, 2023",  # noqa: E501
                            tag='fiba',
                        ),
                        Video(
                            url='https://www.youtube.com/watch?v=YjIPRN9sUR8',
                            title="NBA's Top 10 Plays Of The Night ｜ November 28, 2023",  # noqa: E501
                            tag='fiba',
                        ),
                    ),
                ),
            )
        ]
    )
def test_parse_output(output, playlist, expected):
    assert sorted(_parse_output(playlist, output)) == sorted(expected)


@pytest.mark.parametrize(
        's,expected',
        [
            ('<', '&lt;'),
            ('<<', '&lt;&lt;'),
            ('>', '&gt;'),
            ('&', '&amp;'),
            ('<slava>', '&lt;slava&gt;'),
        ]
    )
def test_escape(s, expected):
    assert escape(s) == expected
