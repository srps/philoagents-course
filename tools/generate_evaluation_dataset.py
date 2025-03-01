from pathlib import Path

from loguru import logger

from philoagents.application.evaluation import EvaluationDatasetGenerator
from philoagents.domain.philosopher import PhilosopherExtract
from philoagents.settings import settings


def main(metadata_file: Path, temperature: float, max_samples: int) -> None:
    philosophers = PhilosopherExtract.from_json(metadata_file)

    logger.info(
        f"Generating evaluation dataset with temperature {temperature} and {max_samples} samples."
    )
    logger.info(f"Count of philosophers: {len(philosophers)}")

    evaluation_dataset_generator = EvaluationDatasetGenerator(
        temperature=temperature, max_samples=max_samples
    )
    evaluation_dataset_generator(philosophers)


if __name__ == "__main__":
    main(
        metadata_file=settings.EXTRACTION_METADATA_FILE_PATH,
        temperature=1.0,
        max_samples=30,
    )
