# Streamlit Community Cloud Deployment

## Recommended Free Hosting Option

Streamlit Community Cloud is the preferred free hosting option for this project because the app is built with Streamlit.

## Steps

1. Create a GitHub repository.
2. Upload the complete `Data Visualization` project folder contents to the repository root.
3. Make sure these files are present:
   - `app.py`
   - `requirements.txt`
   - `data/raw/edu_institutes.xlsx`
   - `src/`
   - `assets/`
4. Go to Streamlit Community Cloud.
5. Connect your GitHub account.
6. Select the repository.
7. Set the main file path to:

```text
app.py
```

8. Deploy the app.

## Secrets and Credentials

Do not upload passwords or private credentials. If secrets are ever needed, add them in Streamlit Cloud under:

```text
App settings > Secrets
```

The local `.env` file is ignored by Git and should not be committed.

## Version 2.0 AI Assistant Secrets

To enable the AI Data Assistant, add:

```toml
OPENROUTER_API_KEY = "your_private_openrouter_key"
OPENROUTER_MODEL = "openrouter/free"
APP_SITE_NAME = "Data Visualization Dashboard"
```

If these values are not configured, the visualization dashboard still works and the AI tab shows a setup message.

## Python Version Note

Python 3.11 or 3.12 is recommended for Streamlit Community Cloud. Python 3.14.2 may not be available on all free hosts yet.

## Common Fixes

- If the app cannot find the dataset, confirm that `data/raw/edu_institutes.xlsx` exists in GitHub.
- If package installation fails, use Python 3.11/3.12 and redeploy.
- If the app is slow on first load, wait for the Excel workbook cache to finish building.

## Live Link Placeholder

```text
Public static preview: https://bd-edu-institutes-explorer-6565.netlify.app
Add final deployed Streamlit app link here after configuring Python hosting.
```
