#!/usr/bin/env python3
from pathlib import Path


def main() -> int:
    nba_folder = Path('./storage/NBA')
    history = Path('./storage/history.json')
    if history.exists():
        nba_folder.mkdir()
        history.rename(nba_folder / history.name)

    return 0


if __name__ == '__main__':
    main()
