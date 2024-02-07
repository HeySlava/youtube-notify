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
        self.videos = self.history.read_text().strip().splitlines()

    def _init(self) -> None:
        if not self.history.parent.exists():
            self.history.parent.mkdir(parents=True)
            self.history.touch()

    def update_history(self, videos: List[Video]) -> None:
        with open(self.history, 'a') as f:
            for v in videos:
                f.write(f'{v.url}\n')


playlists = [
        Playlist(
            url='https://www.youtube.com/@NBA/videos',
            tag='NBA',
            pattern=re.compile(
                r"NBA's\s*Top\s*\d+\s*Plays\s*Of\s*The\s*Night",
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@FIBA3x3/videos',
            tag='FIBA3x3',
            pattern=re.compile(
                r'top\s*\d+|highlights',
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@euroleague/videos',
            tag='euroleague',
            pattern=re.compile(
                r'top\s*\d+\s*(play|assist|block|dunk)?',
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@vtbleague/videos',
            tag='vtbleague',
            pattern=re.compile(r'Top\s*\d+\s*Plays', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@acbcom/videos',
            tag='ACB',
            pattern=re.compile(r'top\s*\d+', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@BasketballCL/videos',
            tag='BasketballCL',
            pattern=re.compile(r'top\s*\d+\s*play', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@FIBA/videos',
            tag='FIBA',
            pattern=re.compile(r'top\s*\d+\s*plays', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@nbagleague/videos',
            tag='nbagleague',
            pattern=re.compile(r'top\s*\d+\s*plays', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@legabasket/videos',
            tag='legabasket',
            pattern=re.compile(
                r'top\s*\d+\s*pokerstarsnews',
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@LNBOfficiel/videos',
            tag='LNBOfficiel',
            pattern=re.compile(r'elite\s*top\s*\d+\s', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@WNBA/videos',
            tag='WNBA',
            pattern=re.compile(r'best\s*of\s*wnba', flags=re.IGNORECASE),
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


NA = 'NA'


def _parse_output(
        playlist: Playlist,
        output: str,
) -> List[Video]:
    result = []
    output_lines = output.strip().splitlines()
    titles = output_lines[::3]
    urls = output_lines[1::3]
    video_types = output_lines[2::3]
    for title, url, video_type in zip(titles, urls, video_types):
        if playlist.pattern.search(title) and video_type == NA:
            result.append(Video(title=title, url=url, tag=playlist.tag))
    result.reverse()
    return result


def _get_last_videos(playlist: Playlist) -> List[Video]:
    cmd = (
            'yt-dlp', '-I0:30', '-s', '--flat-playlist',
            '--print', '%(title)s',
            '--print', 'urls',
            '--print', 'live_status',
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
                pathlib.Path(f'./storage/{p.tag}') / 'history.txt'
            )
        last_videos = _get_last_videos(p)
        new_videos = [
                v for v in last_videos if v.url not in history.videos
            ]
        notify(new_videos)
        history.update_history(videos=new_videos)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
