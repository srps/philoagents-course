import json
from pathlib import Path

import opik

from philoagents.infrastructure import opik_utils


def create_dataset(name: str, data_path: Path) -> opik.Dataset:
    assert data_path.exists(), f"File {data_path} does not exist."

    with open(data_path, "r") as f:
        evaluation_data = json.load(f)

    dataset_items = []
    for philosopher_id, pairs in evaluation_data.items():
        for pair in pairs:
            dataset_items.append(
                {
                    "philosopher_id": philosopher_id,
                    "question": pair["question"],
                    "answer": pair["answer"],
                }
            )

    dataset = opik_utils.create_dataset(
        name=name,
        description="Dataset containing question-answer pairs for multiple philosophers.",
        items=dataset_items,
    )

    return dataset
