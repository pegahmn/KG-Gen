import streamlit as st
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from core.llm_utils import get_gemini_llm
from core.kg_processor import KnowledgeGraphProcessor
from utils.visualization import visualize_graph # This will be adjusted for Streamlit in the next step
from utils.file_parser import extract_text_from_file # Will be added in the next step

nest_asyncio.apply()

# --- Configuration and Constants ---
GEMINI_MODEL_NAME = "gemini-2.0-flash"
LLM_TEMPERATURE = 0.0 # Use 0 for deterministic extraction

LONG_TEXT = """Albert Einstein[a] (14 March 1879 – 18 April 1955) was a German-born theoretical physicist who is best known for developing the theory of relativity. Einstein also made important contributions to quantum mechanics.[1][5] His mass–energy equivalence formula E = mc2, which arises from special relativity, has been called "the world's most famous equation".[6] He received the 1921 Nobel Prize in Physics for his services to theoretical physics, and especially for his discovery of the law of the photoelectric effect.[7]

Born in the German Empire, Einstein moved to Switzerland in 1895, forsaking his German citizenship (as a subject of the Kingdom of Württemberg)[note 1] the following year. In 1897, at the age of seventeen, he enrolled in the mathematics and physics teaching diploma program at the Swiss federal polytechnic school in Zurich, graduating in 1900. He acquired Swiss citizenship a year later, which he kept for the rest of his life, and afterwards secured a permanent position at the Swiss Patent Office in Bern. In 1905, he submitted a successful PhD dissertation to the University of Zurich. In 1914, he moved to Berlin to join the Prussian Academy of Sciences and the Humboldt University of Berlin, becoming director of the Kaiser Wilhelm Institute for Physics in 1917; he also became a German citizen again, this time as a subject of the Kingdom of Prussia.[note 1] In 1933, while Einstein was visiting the United States, Adolf Hitler came to power in Germany. Horrified by the Nazi persecution of his fellow Jews,[8] he decided to remain in the US, and was granted American citizenship in 1940.[9] On the eve of World War II, he endorsed a letter to President Franklin D. Roosevelt alerting him to the potential German nuclear weapons program and recommending that the US begin similar research.

In 1905, sometimes described as his annus mirabilis (miracle year), he published four groundbreaking papers.[10] In them, he outlined a theory of the photoelectric effect, explained Brownian motion, introduced his special theory of relativity, and demonstrated that if the special theory is correct, mass and energy are equivalent to each other. In 1915, he proposed a general theory of relativity that extended his system of mechanics to incorporate gravitation. A cosmological paper that he published the following year laid out the implications of general relativity for the modeling of the structure and evolution of the universe as a whole.[11][12] In 1917, Einstein wrote a paper which introduced the concepts of spontaneous emission and stimulated emission, the latter of which is the core mechanism behind the laser and maser, and which contained a trove of information that would be beneficial to developments in physics later on, such as quantum electrodynamics and quantum optics.[13]

In the middle part of his career, Einstein made important contributions to statistical mechanics and quantum theory. Especially notable was his work on the quantum physics of radiation, in which light consists of particles, subsequently called photons. With physicist Satyendra Nath Bose, he laid the groundwork for Bose–Einstein statistics. For much of the last phase of his academic life, Einstein worked on two endeavors that ultimately proved unsuccessful. First, he advocated against quantum theory's introduction of fundamental randomness into science's picture of the world, objecting that God does not play dice.[14] Second, he attempted to devise a unified field theory by generalizing his geometric theory of gravitation to include electromagnetism. As a result, he became increasingly isolated from mainstream modern physics.
"""

# Define allowed nodes/relationships as constants
# ALLOWED_PERSON_AWARD_FIELDS = ["Person", "Award", "Theory", "Field"]
# ALLOWED_PERSON_AWARD_RELATIONSHIPS = [("Person", "CORRESPONDENT", "Award")] 


# --- Streamlit UI and Logic ---

async def run_kg_gen_app():
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")

    st.set_page_config(layout="wide") # Use wide layout for better visualization
    st.title("KG-Gen: Knowledge Graph Generator (Alpha)")

    if not google_api_key:
        st.warning("Please set your GOOGLE_API_KEY in the .env file.")
        st.markdown("[Get your Gemini API Key from Google AI Studio](https://makersuite.google.com/app/apikey)")
        return

    # Initialize LLM and KG Processor once
    llm = get_gemini_llm(
    api_key=google_api_key,
    model_name=GEMINI_MODEL_NAME, # Use the constant defined in app.py
    temperature=LLM_TEMPERATURE # Use the constant defined in app.py
    )
    kg_processor = KnowledgeGraphProcessor(llm)

    st.sidebar.header("Input Data")
    input_option = st.sidebar.radio(
        "Choose input method:",
        ("Paste Text", "Upload File (.txt only for now)")
    )

    text_input = ""
    uploaded_file = None

    if input_option == "Paste Text":
        st.sidebar.subheader("Paste Text Below")
        text_input = st.sidebar.text_area("Enter text here:", height=300,
                                        value=LONG_TEXT) # Use LONG_TEXT as default
    elif input_option == "Upload File (.txt only for now)":
        st.sidebar.subheader("Upload File")
        # For now, restrict to .txt
        uploaded_file = st.sidebar.file_uploader(
            "Choose a .txt file",
            type=["txt"]
        )
        if uploaded_file is not None:
            # The extract_text_from_file function will be in utils/file_parser.py
            text_input = extract_text_from_file(uploaded_file, uploaded_file.type)
            if not text_input:
                st.error("Failed to extract text from the uploaded file. Please check the file format or content.")
                return

    st.sidebar.header("Graph Filtering (Optional)")
    use_filtering = st.sidebar.checkbox("Enable Filtering", value=False)
    allowed_nodes = []
    allowed_relationships = []

    if use_filtering:
        node_input = st.sidebar.text_input("Allowed Node Types (comma-separated, e.g., Person,Organization)", "Person,Award,Theory")
        allowed_nodes = [n.strip() for n in node_input.split(',') if n.strip()]

        rel_input = st.sidebar.text_area("Allowed Relationships (format: SourceType,RELATIONSHIP_TYPE,TargetType - one per line)",
                                        "Person,HAS_NATIONALITY,Country\nPerson,RECEIVED_AWARD,Award")
        allowed_relationships = []
        for line in rel_input.split('\n'):
            parts = [p.strip() for p in line.split(',') if p.strip()]
            if len(parts) == 3:
                allowed_relationships.append(tuple(parts))
            elif parts:
                st.sidebar.warning(f"Invalid relationship format: '{line}'. Expected 'SourceType,RELATIONSHIP_TYPE,TargetType'.")

    st.sidebar.markdown("---")
    if st.sidebar.button("Extract Knowledge Graph"):
        if not text_input:
            st.warning("Please provide text input to extract the knowledge graph.")
            return

        with st.spinner("Extracting knowledge graph... This might take a moment."):
            graph_docs = await kg_processor.extract_graph(
                text=text_input,
                allowed_nodes=allowed_nodes if use_filtering else None,
                allowed_relationships=allowed_relationships if use_filtering else None
            )

        if graph_docs:
            st.success("Knowledge graph extracted successfully!")
            st.subheader("Extracted Nodes:")
            st.json([node.dict() for node in graph_docs[0].nodes]) # Display as JSON for clarity
            st.subheader("Extracted Relationships:")
            st.json([rel.dict() for rel in graph_docs[0].relationships])
            visualize_graph(graph_docs)
        else:
            st.error("Failed to extract any graph data. Please check the input text and API key.")


if __name__ == "__main__":
    asyncio.run(run_kg_gen_app())