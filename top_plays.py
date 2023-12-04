import json
import os
import pathlib
import re
import subprocess
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Pattern

import requests


class Playlist(NamedTuple):
    url: str
    tag: str
    pattern: Pattern[str]


class Video(NamedTuple):
    url: str
    title: str
    tag: str


class History:

    def __init__(
            self,
            history: pathlib.Path,
    ) -> None:
        self.history = history
        self._init()

    def _init(self) -> None:
        if not self.history.parent.exists():
            self.history.parent.mkdir()

    def update_history(self, videos: List[str]) -> None:
        with open(self.history, 'w') as f:
            json.dump(videos, f)

    @property
    def old_videos(self) -> list[str]:
        if (
                not self.history.exists() or
                not self.history.read_text()
        ):
            return []
        with open(self.history) as f:
            videos = json.load(f)
        return videos


playlists = [
        Playlist(
            url='https://www.youtube.com/@NBA/videos',
            tag='NBA',
            pattern=re.compile(
                r"NBA's\s+Top\s+\d+\s+Plays\s+Of\s+The\s+Night",
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@FIBA3x3/videos',
            tag='FIBA3x3',
            pattern=re.compile(
                r'top\s+\d+\s+plays|highlights',
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@euroleague/videos',
            tag='euroleague',
            pattern=re.compile(r'Top\s+\d+\s+Plays', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@vtbleague',
            tag='vtbleague',
            pattern=re.compile(r'Top\s+\d+\s+Plays', flags=re.IGNORECASE),
        ),
    ]


def escape(s: str) -> str:
    d = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
    escaped = ''
    for char in s:
        escaped += d.get(char, char)
    return escaped


def _make_message(video: Video) -> str:
    return (
            f'<a href="{video.url}">{escape(video.title)}</a>'
            '\n\n'
            f'#{video.tag}'
        )


def _notify(video: Video) -> None:
    token = os.environ['NBA_TOKEN']
    chat_id = os.environ['NBA_CHAT_ID']
    text = _make_message(video)
    params = {
            'chat_id': chat_id,
            'text': text,
            'disable_web_page_preview': 'False',
            'parse_mode': 'HTML',
        }
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    response = requests.get(url=url, params=params)
    response.raise_for_status()


def notify(videos: Iterable[Video]) -> None:
    for v in videos:
        _notify(v)


def _parse_output(
        playlist: Playlist,
        output: str,
) -> List[Video]:
    result = []
    output_lines = output.strip().splitlines()
    titles = output_lines[::2]
    urls = output_lines[1::2]
    for title, url in zip(titles, urls):
        if playlist.pattern.search(title):
            result.append(Video(title=title, url=url, tag=playlist.tag))
    result.reverse()
    return result


def _get_last_videos(playlist: Playlist) -> List[Video]:
    cmd = (
            'yt-dlp', '-I0:30', '-s', '--flat-playlist',
            '--print', '%(title)s', '--print', 'urls',
            playlist.url,

        )
    p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return _parse_output(playlist=playlist, output=p.stdout)


def main() -> int:
    for p in playlists:
        history = History(
                pathlib.Path(f'./storage/{p.tag}') / 'history.json'
            )
        last_videos = _get_last_videos(p)
        new_videos = [
                v for v in last_videos if v.url not in history.old_videos
            ]
        notify(new_videos)
        new_url = {v.url for v in last_videos}
        all_videos = set(history.old_videos).union(new_url)
        history.update_history(videos=list(all_videos))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
