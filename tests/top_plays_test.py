import re
from unittest import mock

import pytest

from testing import util
from top_plays import _get_new_videos
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
                util.path_to_resource('NBA_raw.txt').read_text(),
                Playlist(
                    pattern=re.compile('match'),
                    url='fake_url',
                    tag='nba',
                ),
                set(
                    (
                        Video(
                            url='https://test2.com',
                            title='match title2',
                            tag='nba',
                        ),
                        Video(
                            url='https://test1.com',
                            title='match title1',
                            tag='nba',
                        ),
                    ),
                ),
            )
        ]
    )
def test_get_new_videos(output, playlist, expected):
    mock_result = mock.MagicMock()
    with mock.patch('subprocess.run', return_value=mock_result):
        mock_result.stdout = output
        assert _get_new_videos(playlist) == expected


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
