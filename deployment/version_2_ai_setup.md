# Version 2.0 AI Setup

The Version 2.0 dashboard includes an optional API-based AI data assistant.

## Provider

The project uses OpenRouter's OpenAI-compatible chat completion endpoint. The default model is:

```text
openrouter/free
```

This can route to available free models, subject to OpenRouter account limits.

## Required Secret

Set this environment variable locally or in your hosting platform:

```text
OPENROUTER_API_KEY=your_private_key_here
```

Do not commit this value to GitHub.

## Optional Variables

```text
OPENROUTER_MODEL=openrouter/free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
AI_TIMEOUT_SECONDS=30
APP_SITE_URL=https://github.com/Monokayser/Data-Visualization
APP_SITE_NAME=Data Visualization Dashboard
```

## Local Setup

1. Copy `.env.example` to `.env`.
2. Add your real `OPENROUTER_API_KEY`.
3. Run:

```bash
streamlit run app.py
```

## Streamlit Cloud Setup

1. Open the deployed app settings.
2. Go to Secrets.
3. Add:

```toml
OPENROUTER_API_KEY = "your_private_key_here"
OPENROUTER_MODEL = "openrouter/free"
```

4. Reboot the app.

## Safety Notes

- The app does not send the full workbook to the AI provider.
- Only summarized filtered context, chart summaries, and active filters are sent.
- The assistant is instructed not to fabricate values or unsupported conclusions.

