"""Global LLM client initialization for Vertex AI Gemini."""

import os
from types import SimpleNamespace
from google import genai
from google.genai.types import HttpOptions
from google.auth import default
from langchain_google_genai import ChatGoogleGenerativeAI


# Initialize once at module load time
def _initialize_client():
    """Initialize the Vertex AI Gemini client and return a small wrapper.

    Returns a SimpleNamespace with attributes:
      - client: the raw genai.Client
      - langchain_llm: the LangChain-compatible LLM wrapper
      - project, location: configuration values
    """
    try:
        credentials, project = default()
        location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

        genai_client = genai.Client(
            enterprise=True,
            project=project,
            location=location,
            credentials=credentials,
            http_options=HttpOptions(api_version="v1"),
        )

        langchain_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            project=project,
            location=location,
            credentials=credentials,
        )

        return SimpleNamespace(client=genai_client, langchain_llm=langchain_llm, project=project, location=location)

    except Exception as e:
        print(f"Failed to initialize LLM client: {e}")
        raise


# Global wrapper instance
client = _initialize_client()


def get_google_client():
    return client.client


def get_langchain_client():
    return client.langchain_llm


def get_client():
    """Return the wrapper object (has .client and .langchain_llm)."""
    return client


def generate_content(prompt: str, model: str = "gemini-2.5-flash") -> str:
    """Generate content using the raw genai client."""
    response = client.client.models.generate_content(
        model=model,
        contents=prompt,
    )
    return response.text
