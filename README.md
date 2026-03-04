# ChatMe

This repository contains a minimal chatbot built with **LangChain** and **FastAPI**, leveraging the **Qwen** language model via an OpenAI-compatible endpoint.

## Setup Instructions

1. **Install dependencies**

   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Configure your API key**

   Export an environment variable for the OpenAI-compatible API key (used to access Qwen):

   ```bash
   export OPENAI_API_KEY="your_api_key_here"
   ```

3. **Run the server**

   ```bash
   uvicorn main:app --reload
   ```

   The FastAPI application will be available at `http://localhost:8000`.

## Using the Chat Endpoint

Send a POST request to `/chat` with a JSON body containing a `message` field.

Example with `curl`:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

Response:

```json
{"response": "I'm doing well, thank you! How can I help you today?"}
```

## Notes

- The application uses `langchain.llms.OpenAI` with `model_name="qwen-1"`.
- Make sure your API key has access to the Qwen model.
