import json
from pathlib import Path

from philoagents.application import LongTermMemoryCreation


def main(data_dir: Path) -> None:
    characters = load_characters(data_dir)

    pipeline = LongTermMemoryCreation.build_from_settings()
    pipeline(characters)


def load_characters(data_dir: Path) -> list[dict]:
    with open(data_dir / "characters.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    main(data_dir=Path("data"))
