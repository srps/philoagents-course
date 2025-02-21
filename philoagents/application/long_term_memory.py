from langchain_community.document_loaders import WikipediaLoader
from langchain_core.documents import Document
from tqdm import tqdm

from philoagents.application.rag.retrievers import Retriever, get_retriever
from philoagents.application.rag.splitters import Splitter, get_splitter
from philoagents.infrastructure.mongo import MongoClientWrapper, MongoIndex
from philoagents.settings import settings


class LongTermMemoryCreation:
    def __init__(self, retriever: Retriever, splitter: Splitter) -> None:
        self.retriever = retriever
        self.splitter = splitter

    @classmethod
    def build_from_settings(cls) -> "LongTermMemoryCreation":
        retriever = get_retriever(
            embedding_model_id=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
            k=settings.RAG_TOP_K,
            device=settings.RAG_DEVICE,
        )
        splitter = get_splitter(chunk_size=settings.RAG_CHUNK_SIZE)

        return cls(retriever, splitter)

    def __call__(self, characters: list[dict]) -> None:
        progress_bar = tqdm(
            characters,
            desc="Processing characters",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{postfix}]",
        )
        for character in progress_bar:
            progress_bar.set_postfix_str(f"Character: {character['name']}")

            loader = WikipediaLoader(
                query=character["name"],
                lang="en",
                load_max_docs=1,
                doc_content_chars_max=1000000,
            )
            docs = loader.load()

            chunked_docs = self.splitter.split_documents(docs)
            self.retriever.vectorstore.add_documents(chunked_docs)

        self.__create_index()

    def __create_index(self) -> None:
        with MongoClientWrapper(
            model=Document, collection_name=settings.MONGO_LONG_TERM_MEMORY_COLLECTION
        ) as client:
            self.index = MongoIndex(
                retriever=self.retriever,
                mongodb_client=client,
            )
            self.index.create(
                is_hybrid=True, embedding_dim=settings.RAG_TEXT_EMBEDDING_MODEL_DIM
            )


class LongTermMemoryRetrieval:
    def __init__(self, retriever: Retriever) -> None:
        self.retriever = retriever

    @classmethod
    def build_from_settings(cls) -> "LongTermMemoryRetrieval":
        retriever = get_retriever(
            embedding_model_id=settings.RAG_TEXT_EMBEDDING_MODEL_ID,
            k=settings.RAG_TOP_K,
            device=settings.RAG_DEVICE,
        )

        return cls(retriever)

    def __call__(self, query: str) -> list[Document]:
        return self.retriever.invoke(query)
