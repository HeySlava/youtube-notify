import os
import pathlib
import re
import subprocess
from typing import Iterable
from typing import List
from typing import NamedTuple
from typing import Pattern

import requests
import yaml


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


flag_mapping = {
    'ASCII': re.ASCII,
    'IGNORECASE': re.IGNORECASE,
    'LOCALE': re.LOCALE,
    'UNICODE': re.UNICODE,
    'MULTILINE': re.MULTILINE,
    'DOTALL': re.DOTALL,
    'VERBOSE': re.VERBOSE,
    'TEMPLATE': re.TEMPLATE,
    'DEBUG': re.DEBUG,
    'A': re.A,
    'S': re.S,
    'X': re.X,
    'I': re.I,
    'L': re.L,
    'M': re.M,
    'U': re.U,
}


def _parse_re_flags(flags: str) -> int:
    flag_values = [
            flag_mapping[flag.strip()] for flag in flags.split('|')
        ]
    compiled_flags = 0
    for flag_value in flag_values:
        compiled_flags |= flag_value
    return compiled_flags


def read_config(config_path: str) -> list[Playlist]:
    with open(config_path) as f:
        config = yaml.safe_load(f)

    playlists = []
    for p in config['playlists']:
        url = p['url'].strip()
        tag = p['tag'].strip()
        regex = p['pattern']['regex'].strip()
        flags_s = p['pattern']['flags'].strip()

        pattern = re.compile(regex, flags=_parse_re_flags(flags_s))
        playlist = Playlist(
                url=url,
                tag=tag,
                pattern=pattern,
            )
        playlists.append(playlist)
    return playlists


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
    playlists = read_config('./config.yaml')
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