import json
from pathlib import Path
from typing import List

from philoagents.application import LongTermMemoryCreator
from philoagents.domain.philosopher import PhilosopherExtract


def main(data_dir: Path) -> None:
    """Main function to create long-term memory for philosophers.

    Args:
        data_dir: Directory containing the philosopher data.
    """
    philosophers = load_philosophers(data_dir)

    long_term_memory_creator = LongTermMemoryCreator.build_from_settings()
    long_term_memory_creator(philosophers)


def load_philosophers(data_dir: Path) -> List[PhilosopherExtract]:
    """Load philosopher data from JSON file and convert to PhilosopherExtract objects.

    Args:
        data_dir: Directory containing the philosopher data.

    Returns:
        List of PhilosopherExtract objects parsed from the JSON file.
    """

    with open(data_dir / "philosophers.json", "r") as f:
        philosophers_data = json.load(f)

    return [PhilosopherExtract(**philosopher) for philosopher in philosophers_data]


if __name__ == "__main__":
    main(data_dir=Path("data"))
