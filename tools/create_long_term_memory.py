from pathlib import Path

from philoagents.application import LongTermMemoryCreator
from philoagents.domain.philosopher import PhilosopherExtract
from philoagents.settings import settings


def main(metadata_file: Path) -> None:
    """Main function to create long-term memory for philosophers.

    Args:
        metadata_file: Path to the philosophers extraction metadata JSON file.
    """

    philosophers = PhilosopherExtract.from_json(metadata_file)

    long_term_memory_creator = LongTermMemoryCreator.build_from_settings()
    long_term_memory_creator(philosophers)


if __name__ == "__main__":
    main(metadata_file=settings.EXTRACTION_METADATA_FILE_PATH)
