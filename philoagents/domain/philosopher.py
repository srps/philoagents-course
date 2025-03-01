from typing import List

from pydantic import BaseModel, Field


class PhilosopherExtract(BaseModel):
    """A class representing raw philosopher data extracted from external sources.

    This class follows the structure of the philosophers.json file and contains
    basic information about philosophers before enrichment.

    Attributes:
        name (str): Name of the philosopher.
        urls (List[str]): List of URLs with information about the philosopher.
    """

    name: str = Field(description="Name of the philosopher")
    urls: List[str] = Field(
        description="List of URLs with information about the philosopher"
    )


class Philosopher(BaseModel):
    """A class representing a philosopher agent with memory capabilities.

    Attributes:
        id (str): Unique identifier for the philosopher.
        name (str): Name of the philosopher.
        perspective (str): Description of the philosopher's theoretical views
            about AI.
        style (str): Description of the philosopher's talking style.
    """

    id: str = Field(description="Unique identifier for the philosopher")
    name: str = Field(description="Name of the philosopher")
    perspective: str = Field(
        description="Description of the philosopher's theoretical views about AI"
    )
    style: str = Field(description="Description of the philosopher's talking style")

    def __str__(self) -> str:
        """Returns a string representation of the Philosopher.

        Returns:
            str: String representation of the Philosopher instance.
        """

        return f"Philosopher(id={self.id}, name={self.name}, perspective={self.perspective}, style={self.style})"
