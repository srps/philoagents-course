from pathlib import Path

from philoagents.application.evaluation import EvaluationDatasetGenerator
from philoagents.domain.philosopher import PhilosopherExtract
from philoagents.settings import settings


def main(metadata_file: Path) -> None:
    philosophers = PhilosopherExtract.from_json(metadata_file)
    evaluation_dataset_generator = EvaluationDatasetGenerator()
    evaluation_dataset_generator(philosophers)


if __name__ == "__main__":
    main(metadata_file=settings.EXTRACTION_METADATA_FILE_PATH)
