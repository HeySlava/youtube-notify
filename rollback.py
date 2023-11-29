#!/usr/bin/env python3
from pathlib import Path


def main() -> int:
    nba_folder = Path('./storage/NBA')
    history = Path('./storage/NBA/history.json')
    if history.exists():
        history.rename(nba_folder.parent / history.name)
        nba_folder.rmdir()

    return 0


if __name__ == '__main__':
    main()
