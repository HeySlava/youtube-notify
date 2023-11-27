import json
import os
import pathlib
from typing import NamedTuple
from typing import Sequence

import pytube
import requests


class Playlist(NamedTuple):
    url: str
    tag: str


class History:

    def __init__(
            self,
            history: pathlib.Path = pathlib.Path('storage') / 'history.json',
    ) -> None:
        self.history = history
        self._init()

    def _init(self) -> None:
        if not self.history.parent.exists():
            self.history.parent.mkdir()
        if not self.history.exists():
            with open(self.history, 'w') as f:
                json.dump([], f)

    def update_history(self, videos: Sequence[str]) -> None:
        with open(self.history, 'w') as f:
            json.dump(list(videos), f)

    @property
    def old_videos(self) -> list[str]:
        with open(self.history) as f:
            videos = json.load(f)
        return videos


playlist = Playlist(
        url='https://www.youtube.com/playlist?list=PLlVlyGVtvuVnHgxDVDxbRuObq6XSKiCxZ',  # noqa: E501
        tag='#NBA',
    )


def _make_message(url: str, tag: str) -> str:
    return f'{url}\n\n{tag}'


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


def main() -> int:
    history = History()
    p = pytube.Playlist(playlist.url)
    new_videos = {
            (url, playlist.tag) for
            url in
            set(p) - set(history.old_videos)
        }
    notify(new_videos)
    history.update_history(videos=p)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
