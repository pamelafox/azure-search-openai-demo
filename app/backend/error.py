import logging
from typing import Any, cast

from azure.core.exceptions import HttpResponseError
from openai import APIError
from quart import jsonify

ERROR_MESSAGE = """The app encountered an error processing your request.
If you are an administrator of the app, check the application logs for a full traceback.
Error type: {error_type}
"""
ERROR_MESSAGE_FILTER = """Your message contains content that was flagged by the OpenAI content filter."""

ERROR_MESSAGE_LENGTH = """Your message exceeded the context length limit for this OpenAI model. Please shorten your message or change your settings to retrieve fewer search results."""


def get_openai_error_code(error: APIError) -> str | None:
    """Extract the error code from an OpenAI API error body."""
    if error.body and isinstance(error.body, dict):
        body = cast(dict[str, Any], error.body)
        return body.get("code")
    return None


def is_content_filter_error(error: Exception) -> bool:
    """Check if an error is a content filter error from OpenAI or Azure Search."""
    if isinstance(error, APIError) and get_openai_error_code(error) == "content_filter":
        return True
    # AI Search Agentic KB returns "The response was filtered due to the prompt triggering Azure OpenAI's content management policy."
    if isinstance(error, HttpResponseError) and "content management policy" in str(error):
        return True
    return False


def error_dict(error: Exception) -> dict:
    if is_content_filter_error(error):
        return {"error": ERROR_MESSAGE_FILTER}
    if isinstance(error, APIError) and get_openai_error_code(error) == "context_length_exceeded":
        return {"error": ERROR_MESSAGE_LENGTH}
    return {"error": ERROR_MESSAGE.format(error_type=type(error))}


def error_response(error: Exception, route: str, status_code: int = 500):
    logging.exception("Exception in %s: %s", route, error)
    if is_content_filter_error(error):
        status_code = 400
    return jsonify(error_dict(error)), status_code
