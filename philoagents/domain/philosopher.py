class Philosopher:
    """A class representing a philosopher agent with memory capabilities.

    Attributes:
        id (str): Unique identifier for the philosopher.
        name (str): Name of the philosopher.
        personality (str): Description of the philosopher's theoretical views
            about AI.
        style (str): Description of the philosopher's talking style.
    """

    def __init__(self, id: str, name: str, perspective: str, style: str):
        self.id = id
        self.name = name
        self.perspective = perspective
        self.style = style

    def __str__(self):
        return f"Philosopher(id={self.id}, name={self.name}, perspective={self.perspective}, style={self.style})"
