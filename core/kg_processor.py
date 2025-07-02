from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI # Keep for type hinting

class KnowledgeGraphProcessor:
    def __init__(self, llm_model: ChatGoogleGenerativeAI):
        self.llm = llm_model
        # self.graph_transformer = LLMGraphTransformer(llm=self.llm) # Removed, as it's created per call if filtering changes

    async def extract_graph(self, text: str, allowed_nodes: list = None, allowed_relationships: list = None):
        """Extracts knowledge graph documents from text with optional filtering."""
        transformer_params = {"llm": self.llm}
        if allowed_nodes:
            transformer_params["allowed_nodes"] = allowed_nodes
        if allowed_relationships:
            transformer_params["allowed_relationships"] = allowed_relationships

        current_graph_transformer = LLMGraphTransformer(**transformer_params)
        documents = [Document(page_content=text)]
        graph_documents = await current_graph_transformer.aconvert_to_graph_documents(documents)
        return graph_documents

    # Removed print_graph_details and visualize methods from here
    # as they are specific to how the output is presented (print vs Streamlit)
    # The app.py will handle printing/displaying the output from extract_graph.