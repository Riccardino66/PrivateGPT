from dataclasses import dataclass
from typing import TYPE_CHECKING

from injector import inject, singleton
from llama_index import ServiceContext, StorageContext, VectorStoreIndex
from llama_index.schema import NodeWithScore

from private_gpt.components.embedding.embedding_component import EmbeddingComponent
from private_gpt.components.llm.llm_component import LLMComponent
from private_gpt.components.node_store.node_store_component import NodeStoreComponent
from private_gpt.components.vector_store.vector_store_component import (
    VectorStoreComponent,
)
from private_gpt.open_ai.extensions.context_docs import ContextDocs

if TYPE_CHECKING:
    from llama_index.schema import RelatedNodeInfo


@dataclass
class Chunk:
    score: float
    doc_id: str
    doc_name: str
    text: str
    previous_texts: list[str] | None
    next_texts: list[str] | None


@singleton
class ChunksService:
    @inject
    def __init__(
        self,
        llm_component: LLMComponent,
        vector_store_component: VectorStoreComponent,
        embedding_component: EmbeddingComponent,
        node_store_component: NodeStoreComponent,
    ) -> None:
        self.vector_store_component = vector_store_component
        self.storage_context = StorageContext.from_defaults(
            vector_store=vector_store_component.vector_store,
            docstore=node_store_component.doc_store,
            index_store=node_store_component.index_store,
        )
        self.query_service_context = ServiceContext.from_defaults(
            llm=llm_component.llm, embed_model=embedding_component.embedding_model
        )

    def _get_sibling_nodes_text(
        self, node_with_score: NodeWithScore, related_number: int, forward: bool = True
    ) -> list[str]:
        explored_nodes_texts = []
        current_node = node_with_score.node
        for _ in range(related_number):
            explored_node_info: RelatedNodeInfo | None = (
                current_node.next_node if forward else current_node.prev_node
            )
            if explored_node_info is None:
                break

            explored_node = self.storage_context.docstore.get_node(
                explored_node_info.node_id
            )

            explored_nodes_texts.append(explored_node.get_content())
            current_node = explored_node

        return explored_nodes_texts

    def retrieve_relevant(
        self,
        text: str,
        context_docs: ContextDocs,
        limit: int = 10,
        context_size: int = 0,
    ) -> list[Chunk]:
        index = VectorStoreIndex.from_vector_store(
            self.vector_store_component.vector_store,
            storage_context=self.storage_context,
            service_context=self.query_service_context,
            show_progress=True,
        )
        vector_index_retriever = self.vector_store_component.get_retriever(
            index=index, context_docs=context_docs, similarity_top_k=limit
        )
        nodes = vector_index_retriever.retrieve(text)
        nodes.sort(key=lambda n: n.score or 0.0, reverse=True)

        retrieved_nodes = []
        for node in nodes:
            doc_id = node.node.ref_doc_id if node.node.ref_doc_id is not None else "-"
            retrieved_nodes.append(
                Chunk(
                    score=node.score or 0.0,
                    doc_id=doc_id,
                    doc_name=node.metadata["file_name"],
                    text=node.get_content(),
                    previous_texts=self._get_sibling_nodes_text(
                        node, context_size, False
                    ),
                    next_texts=self._get_sibling_nodes_text(node, context_size),
                )
            )

        return retrieved_nodes
