# Optional local AI model

AIMN runs without a model by default. In that mode, its agents use transparent deterministic local templates. To let the Writer use an actual open model without a paid API, enable the optional Ollama service.

## Requirements

- Docker Compose v2.
- Enough free disk space for the selected model (the suggested 3B model download is multiple GB).
- Adequate RAM/CPU. CPU-only generation can be slow; a GPU is optional.

## Enable Ollama

1. In the repository root, edit the private `.env` file and set:

```dotenv
AIMN_LLM_PROVIDER=ollama
AIMN_OLLAMA_URL=http://ollama:11434
AIMN_OLLAMA_MODEL=qwen2.5:3b
```

2. Start the stack with the local AI profile:

```bash
docker compose --profile local-ai up --build -d
```

3. Download the model once into Ollama's persistent Docker volume:

```bash
docker compose exec ollama ollama pull qwen2.5:3b
```

4. Check it is installed:

```bash
docker compose exec ollama ollama list
docker compose logs -f worker
```

Create a CEO task from the dashboard. Its Writer specialist will ask the local model for a draft. The result is still unverified and must be fact-checked and reviewed by the owner. If Ollama is unavailable or returns invalid output, the Writer task fails visibly rather than silently pretending a model ran.

To return to deterministic mode, set `AIMN_LLM_PROVIDER=none` and run `docker compose up -d`. The Ollama model data remains in its named volume until you explicitly remove it.

## Scope and privacy

- The Ollama service is optional and is not exposed on a public host port.
- Prompts and model inference stay inside the Docker network on the machine running AIMN.
- No hosted AI API, API key, or paid provider is used.
- This is inference with an existing model, not training or fine-tuning model weights.
- Only the Writer draft generation is connected today; research, fact-checking, analytics and publishing are not magically made autonomous by installing a model.
