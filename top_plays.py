import json
import os
import pathlib
from typing import Sequence

import pytube
import requests


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


def _notify(url: str) -> None:
    token = os.environ['NBA_TOKEN']
    chat_id = os.environ['NBA_CHAT_ID']
    params = {
            'chat_id': chat_id,
            'text': url,
            'disable_web_page_preview': 'False',
        }
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    requests.get(url=url, params=params)


def notify(urls: set[str]) -> None:
    for url in urls:
        _notify(url)


def main() -> int:
    history = History()
    watch_url = 'https://www.youtube.com/playlist?list=PLlVlyGVtvuVnHgxDVDxbRuObq6XSKiCxZ'  # noqa: E501
    p = pytube.Playlist(watch_url)
    new_videos = set(p) - set(history.old_videos)
    notify(new_videos)
    history.update_history(videos=p)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
