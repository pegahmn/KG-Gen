from langchain_google_genai import ChatGoogleGenerativeAI

def get_gemini_llm(api_key: str, model_name: str, temperature: float):
    """Initializes and returns a ChatGoogleGenerativeAI LLM instance."""
    if not api_key:
        raise ValueError("Google API key not found. Please set the GOOGLE_API_KEY environment variable.")
    return ChatGoogleGenerativeAI(temperature=temperature, model=model_name, google_api_key=api_key)