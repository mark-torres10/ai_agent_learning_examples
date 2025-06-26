import re

from lib.utils import get_client


DEFAULT_MODEL = "gpt-4o-mini"

def llm_call(
    prompt: str,
    system_prompt: str,
    model: str = DEFAULT_MODEL,
    provider: str = "openai"
):
    client = get_client(provider)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=4096,
        top_p=1.0,
    )
    return response.choices[0].message.content

def extract_xml(text: str, tag: str) -> str:
    """
    Extracts the content of the specified XML tag from the given text. Used for parsing structured responses 

    Args:
        text (str): The text containing the XML.
        tag (str): The XML tag to extract content from.

    Returns:
        str: The content of the specified XML tag, or an empty string if the tag is not found.
    """
    match = re.search(f'<{tag}>(.*?)</{tag}>', text, re.DOTALL)
    return match.group(1) if match else ""
