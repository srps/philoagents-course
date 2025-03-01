from pathlib import Path

from philoagents.application.evaluation import create_dataset, evaluate_agent


def main(name: str, data_path: Path, workers: int = 2, nb_samples: int = 10) -> None:
    dataset = create_dataset(name=name, data_path=data_path)
    evaluate_agent(dataset, workers=workers, nb_samples=nb_samples)


if __name__ == "__main__":
    main(
        name="philoagents_evaluation_dataset",
        data_path=Path("data/evaluation.json"),
        workers=1,
        nb_samples=2,
    )
