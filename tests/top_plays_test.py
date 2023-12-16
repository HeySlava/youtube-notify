import re
from unittest import mock

import pytest

from top_plays import _get_last_videos
from top_plays import _make_message
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
                """\
bad title
https://test.com
NA
match title2
https://test2.com
NA
bad2 title
https://test.com
NA
match title1
https://test1.com
NA
""",
                Playlist(
                    pattern=re.compile('match'),
                    url='fake_url',
                    tag='nba',
                ),
                [
                    Video(
                        url='https://test1.com',
                        title='match title1',
                        tag='nba',
                    ),
                    Video(
                        url='https://test2.com',
                        title='match title2',
                        tag='nba',
                    ),
                ],
            )
        ]
    )
def test_get_last_videos(output, playlist, expected):
    mock_result = mock.MagicMock()
    with mock.patch('subprocess.run', return_value=mock_result):
        mock_result.stdout = output
        result = _get_last_videos(playlist)
        assert result == expected


@pytest.mark.parametrize(
        'output,playlist,expected',
        [
            (
                """\
match title2 with NA
https://test2.com
NA
match title1 with NA
https://test1.com
NA
match title without NA
https://test.com
is_upcoming
""",
                Playlist(
                    pattern=re.compile('match'),
                    url='fake_url',
                    tag='nba',
                ),
                [
                    Video(
                        url='https://test1.com',
                        title='match title1 with NA',
                        tag='nba',
                    ),
                    Video(
                        url='https://test2.com',
                        title='match title2 with NA',
                        tag='nba',
                    ),
                ],
            )
        ]
    )
def test_get_last_videos_only_na(output, playlist, expected):
    mock_result = mock.MagicMock()
    with mock.patch('subprocess.run', return_value=mock_result):
        mock_result.stdout = output
        result = _get_last_videos(playlist)
        assert result == expected


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
