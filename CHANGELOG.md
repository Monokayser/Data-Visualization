# Changelog

## v2.0.0 - Update 2

### Added

- AI Data Assistant tab powered by OpenRouter-compatible chat completions.
- Secure environment-variable configuration for AI API access.
- Dedicated system prompt and dashboard context builder.
- Example AI questions, chat history, loading states, clear-chat option, and graceful missing-key messages.
- Test suite for data loading, missing values, filtering, visualization generation, AI context construction, and missing API key handling.
- Version 2.0 label in the dashboard hero section.

### Improved

- README updated with Version 2.0 AI configuration instructions.
- Requirements updated with API client dependency.
- `.env.example` expanded with safe AI configuration placeholders.
- `.gitignore` updated to ignore logs and local environment files.

### Security

- No API key, token, password, or secret is committed.
- The AI assistant sends summarized dashboard context only, not the full dataset.
- The app continues to work when the AI API key is unavailable.

### Known Limitation

- API-based AI responses require a valid `OPENROUTER_API_KEY` configured locally or in deployment secrets.

