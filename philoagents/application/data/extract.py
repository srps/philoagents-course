from typing import Generator

from langchain_community.document_loaders import WikipediaLoader
from langchain_core.documents import Document
from tqdm import tqdm

from philoagents.domain.philosopher import Philosopher, PhilosopherExtract
from philoagents.domain.philosopher_factory import PhilosopherFactory


def get_extraction_generator(
    philosophers: list[PhilosopherExtract],
) -> Generator[tuple[Philosopher, Document], None, None]:
    """
    Extract documents for a list of philosophers, yielding one document at a time along with the philosopher.

    Args:
        philosophers: A list of dictionaries containing philosopher information.

    Yields:
        tuple[Philosopher, Document]: A tuple containing the philosopher dictionary and a document
            extracted for that philosopher, one at a time.
    """

    progress_bar = tqdm(
        philosophers,
        desc="Extracting docs",
        unit="philosopher",
        bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}",
        ncols=100,
        position=0,
        leave=True,
    )

    philosophers_factory = PhilosopherFactory()
    for philosopher in progress_bar:
        philosopher = philosophers_factory.get_philosopher(philosopher.id)
        progress_bar.set_postfix_str(f"Philosopher: {philosopher.name}")

        yield from ((philosopher, doc) for doc in extract(philosopher))


def extract(philosopher: Philosopher) -> list[Document]:
    """
    Extract documents for a single philosopher from Wikipedia.

    Args:
        philosopher: Dictionary containing philosopher information.

    Returns:
        list[Document]: List of documents extracted for the philosopher.
    """

    loader = WikipediaLoader(
        query=philosopher.name,
        lang="en",
        load_max_docs=1,
        doc_content_chars_max=1000000,
    )

    return loader.load()
