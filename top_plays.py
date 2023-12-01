import json
import os
import pathlib
import re
import subprocess
from typing import List
from typing import NamedTuple
from typing import Pattern
from typing import Set

import requests


SEP = '____'


class Playlist(NamedTuple):
    url: str
    tag: str
    pattern: Pattern[str]


class Video(NamedTuple):
    url: str
    title: str


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
                r'top\s+\d+\s+plays|Dunk\s+Contest\s+Highlight',
                flags=re.IGNORECASE,
            ),
        ),
        Playlist(
            url='https://www.youtube.com/@FIBA3x3/videos',
            tag='euroleague',
            pattern=re.compile(r'Top\s+\d+\s+Plays', flags=re.IGNORECASE),
        ),
        Playlist(
            url='https://www.youtube.com/@vtbleague',
            tag='vtbleague',
            pattern=re.compile(r'Top\s+\d+\s+Plays', flags=re.IGNORECASE),
        ),
    ]


def _make_message(url: str, tag: str) -> str:
    return f'{url}\n\n#{tag}'


def _notify(url: str, tag: str) -> None:
    token = os.environ['NBA_TOKEN']
    chat_id = os.environ['NBA_CHAT_ID']
    text = _make_message(url=url, tag=tag)
    params = {
            'chat_id': chat_id,
            'text': text,
            'disable_web_page_preview': 'False',
        }
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    response = requests.get(url=url, params=params)
    response.raise_for_status()


def notify(urls: set[tuple[str, str]]) -> None:
    for url, tag in urls:
        _notify(url, tag)


def _parse_output(
        pattern: Pattern[str],
        output: str,
) -> Set[Video]:
    result = set()
    base_url = 'https://www.youtube.com/watch?v={video_id}'
    for line in output.splitlines():
        if pattern.search(line):
            title, _, rest = line.strip('"').partition(SEP)
            _, _, video_id = rest.rpartition('=')
            url = base_url.format(video_id=video_id)
            title = title.strip()
            result.add(Video(title=title, url=url))
    return result


def _get_new_videos(playlist: Playlist) -> Set[Video]:
    cmd = (
            'yt-dlp', '-I0:30', '-s', '--flat-playlist', '-o',
            f'"%(title)s {SEP} %(original_url)s"', '--print', 'filename',
            playlist.url,

        )
    p = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
    return _parse_output(pattern=playlist.pattern, output=p.stdout)


def main() -> int:
    for p in playlists:
        history = History(
                pathlib.Path(f'./storage/{p.tag}') / 'history.json'
            )
        last_videos = _get_new_videos(p)
        new_video_tags = {
                (url, p.tag) for
                url in
                {v.url for v in last_videos} - set(history.old_videos)
            }
        notify(new_video_tags)
        new_url = {v.url for v in last_videos}
        all_videos = set(history.old_videos).union(new_url)
        history.update_history(videos=list(all_videos))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
