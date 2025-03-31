import io
import os
import traceback
from enum import Enum

from azure.identity.aio import (
    AzureDeveloperCliCredential,
)
from azure.search.documents.aio import SearchClient
from azure.search.documents.models import (
    QueryType,
)
from azure.storage.blob.aio import BlobServiceClient
from mcp.server.fastmcp import FastMCP

from load_azd_env import load_azd_env
from prepdocs import (
    clean_key_if_exists,
    setup_embeddings_service,
    setup_file_processors,
    setup_search_info,
)
from prepdocslib.filestrategy import UploadUserFileStrategy
from prepdocslib.listfilestrategy import File

load_azd_env()

mcp = FastMCP("Search my data")

AZURE_TENANT_ID = os.environ.get("AZURE_TENANT_ID")
azure_credential = AzureDeveloperCliCredential(tenant_id=AZURE_TENANT_ID, process_timeout=60)


class DocumentationTopic(str, Enum):
    """Enum for documentation topics."""

    MODELCONTEXTPROTOCOL = "Model Context Protocol"
    FLASK = "Flask"
    ESLINT = "ESLint"


search_indices = {
    DocumentationTopic.MODELCONTEXTPROTOCOL: "gptkbindex",
    DocumentationTopic.FLASK: "gptkbindex-flask",
    DocumentationTopic.ESLINT: "gptkbindex-eslint",
}


@mcp.tool()
async def search_my_documentation(search_query: str, search_topic: DocumentationTopic) -> str:
    """Search the Azure Search index for documentation about the given search_query.

    Args:
        search_query: The search query to use for the search
        search_topic: The topic to search for, which should be either "Model Context Protocol", "Flask", or "ESLint"

    Returns:
        The search results, formatted as a string
    """
    try:
        AZURE_SEARCH_SERVICE = os.environ["AZURE_SEARCH_SERVICE"]
        # search_topic: str = "Model Context Protocol"
        AZURE_SEARCH_INDEX = search_indices.get(search_topic)
        if not AZURE_SEARCH_INDEX:
            return "Error: Could not find appropriate search index for the given topic."

        search_client = SearchClient(
            endpoint=f"https://{AZURE_SEARCH_SERVICE}.search.windows.net",
            index_name=AZURE_SEARCH_INDEX,
            credential=azure_credential,
        )
        results = await search_client.search(
            search_text=search_query,
            top=10,
            query_type=QueryType.SEMANTIC,
            semantic_configuration_name="default",
            semantic_query=search_query,
        )
        sources = "\n\n".join([f"[{doc['sourcepage']}]: {doc['content']}\n" async for doc in results])
        return sources
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
async def upload_to_my_documentation(filepath: str, search_topic: DocumentationTopic) -> str:
    """
    Upload a file to the main storage account and ingest it into an Azure AI Search index.

    Args:
        filepath: The absolute path on the local filesystem to the file to upload
        search_topic: The most related topic for the file, which should be either "Model Context Protocol", "Flask", or "ESLint"

    Returns:
        A message indicating success or failure
    """
    try:
        file_data = None
        with open(filepath, "rb") as file:
            file_data = file.read()
        if not file_data:
            return "Error: File is empty."
        filename = os.path.basename(filepath)

        # Get environment variables
        AZURE_STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT")
        AZURE_STORAGE_CONTAINER = os.environ.get("AZURE_STORAGE_CONTAINER")
        USE_GPT4V = os.environ.get("USE_GPT4V", "").lower() == "true"

        if not AZURE_STORAGE_ACCOUNT or not AZURE_STORAGE_CONTAINER:
            return "Error: Storage account is not configured."

        # Set up storage client
        blob_service_client = BlobServiceClient(
            f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net",
            credential=azure_credential,
        )
        container_client = blob_service_client.get_container_client(AZURE_STORAGE_CONTAINER)

        # Upload the file
        blob_client = container_client.get_blob_client(filename)
        file_io = io.BytesIO(file_data)
        file_io.name = filename
        await blob_client.upload_blob(file_io, overwrite=True)

        # Reset file pointer for indexing
        file_io.seek(0)

        # Set up ingester components
        file_processors = setup_file_processors(
            azure_credential=azure_credential,
            document_intelligence_service=os.getenv("AZURE_DOCUMENTINTELLIGENCE_SERVICE"),
            local_pdf_parser=os.getenv("USE_LOCAL_PDF_PARSER", "").lower() == "true",
            local_html_parser=os.getenv("USE_LOCAL_HTML_PARSER", "").lower() == "true",
            search_images=USE_GPT4V,
        )

        search_topic = DocumentationTopic.MODELCONTEXTPROTOCOL
        search_index = search_indices.get(search_topic)
        if not search_index:
            return "Error: Could not find appropriate search index for the given topic."
        search_info = await setup_search_info(
            search_service=os.environ["AZURE_SEARCH_SERVICE"],
            index_name=search_index,
            azure_credential=azure_credential,
        )

        text_embeddings_service = setup_embeddings_service(
            azure_credential=azure_credential,
            openai_host=os.getenv("OPENAI_HOST"),
            openai_model_name=os.environ["AZURE_OPENAI_EMB_MODEL_NAME"],
            openai_service=os.getenv("AZURE_OPENAI_SERVICE", ""),
            openai_custom_url=os.getenv("AZURE_OPENAI_CUSTOM_URL", ""),
            openai_deployment=os.getenv("AZURE_OPENAI_EMB_DEPLOYMENT", ""),
            openai_dimensions=int(os.environ["AZURE_OPENAI_EMB_DIMENSIONS"]),
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", ""),
            openai_key=clean_key_if_exists(os.getenv("OPENAI_API_KEY", "")),
            openai_org=os.getenv("OPENAI_ORGANIZATION", ""),
            disable_vectors=os.getenv("USE_VECTORS", "").lower() == "false",
        )

        # Create the ingester and process the file
        ingester = UploadUserFileStrategy(
            search_info=search_info, embeddings=text_embeddings_service, file_processors=file_processors
        )

        # Add the file to the search index as a global document (no ACLs)
        await ingester.add_file(File(content=file_io, acls={}, url=blob_client.url))

        return f"File '{filename}' uploaded and processed successfully. It is now searchable in the index."

    except Exception as e:
        return f"Error uploading file: {str(e)}\nTraceback: {traceback.format_exc()}"


if __name__ == "__main__":
    mcp.run()
