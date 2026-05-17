import json
import logging
import ollama

logger = logging.getLogger(__name__)

MODEL = "llama3.2:3b"

client = ollama.Client()


def call_ollama_json(prompt: str):
    logger.info("Calling Ollama model: %s", MODEL)

    response = client.generate(
        model=MODEL,
        prompt=prompt,
        format="json",
        stream=False,
    )

    raw_response = response["response"]
    logger.info("Raw Ollama response: %s", raw_response)

    return json.loads(raw_response)