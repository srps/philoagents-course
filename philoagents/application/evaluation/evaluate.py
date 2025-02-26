import asyncio

import opik
from loguru import logger
from opik.evaluation import evaluate
from opik.evaluation.metrics import (
    AnswerRelevance,
    ContextRecall,
    Hallucination,
    Moderation,
)

from philoagents.application.conversation_service.generate_response import get_response
from philoagents.domain.philosopher_factory import PhilosopherFactory
from philoagents.infrastructure import opik_utils
from philoagents.settings import settings

opik_utils.configure()


async def evaluation_task(x: dict) -> dict:
    """Calls agentic app logic to evaluate philosopher responses.

    Args:
        x (dict): Dictionary containing:
            - question (str): The input question to evaluate
            - philosopher_id (str): ID of the philosopher to use
            - answer (str): Expected answer for evaluation

    Returns:
        dict: Evaluation results containing:
            - input (str): Original question
            - context (str): Context used (empty in current implementation)
            - output (str): Generated response from philosopher
            - expected_output (str): Expected answer for comparison
    """

    philosopher_factory = PhilosopherFactory()
    philosopher = philosopher_factory.get_philosopher(x["philosopher_id"])

    response = await get_response(
        message=x["question"],
        philosopher_id=philosopher.id,
        philosopher_name=philosopher.name,
        philosopher_perspective=philosopher.perspective,
        philosopher_style=philosopher.style,
        philosopher_context="",
    )

    return {
        "input": x["question"],
        "context": "",  # TODO: Extract context from the agent
        "output": response,
        "expected_output": x["answer"],
    }


def evaluate_agent(dataset: opik.Dataset | None, nb_samples: int | None = None) -> None:
    """Evaluates an agent using specified metrics and dataset.

    Runs evaluation using Opik framework with configured metrics for hallucination,
    answer relevance, moderation, and context recall.

    Args:
        dataset (opik.Dataset | None): Dataset containing evaluation examples.
            Must contain questions and expected answers.

    Raises:
        ValueError: If dataset is None
        AssertionError: If COMET_API_KEY is not set

    Returns:
        None
    """

    assert settings.COMET_API_KEY, (
        "COMET_API_KEY is not set. We need it to track the experiment with Opik."
    )

    if not dataset:
        raise ValueError("Dataset is 'None'.")

    logger.info("Starting evaluation...")

    experiment_config = {
        "model_id": settings.GROQ_LLM_MODEL,
        "dataset_name": dataset.name,
    }
    scoring_metrics = [
        Hallucination(),
        AnswerRelevance(),
        Moderation(),
        ContextRecall(),
    ]

    logger.info("Evaluation details:")
    logger.info(f"Dataset: {dataset.name}")
    logger.info(f"Metrics: {[m.__class__.__name__ for m in scoring_metrics]}")

    evaluate(
        dataset=dataset,
        task=lambda x: asyncio.run(evaluation_task(x)),
        scoring_metrics=scoring_metrics,
        experiment_config=experiment_config,
        task_threads=2,
        nb_samples=nb_samples,
    )
