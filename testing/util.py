from pathlib import Path


HERE = Path(__file__).resolve().parent


def path_to_resource(filename: str) -> Path:
    return HERE / 'resources' / filename
