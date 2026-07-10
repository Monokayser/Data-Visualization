# Hosting Notes

## Safe Credential Handling

- Never commit passwords or API keys.
- Keep local credentials in `.env`.
- Keep deployment credentials in Streamlit secrets or Render environment variables.
- `.env` is already listed in `.gitignore`.

## GitHub Upload Checklist

- Check that `data/raw/edu_institutes.xlsx` is included.
- Check that `.env` is not included.
- Check that `requirements.txt` is included.
- Check that `app.py` is in the repository root for easy Streamlit deployment.

## Python Compatibility

The project was prepared for modern Python versions. For the most reliable free hosting experience, use Python 3.11 or 3.12. If Python 3.14.2 is required locally, install the latest package versions listed in `requirements.txt`.

## Submission Tip

For academic submission, include:

- GitHub repository link
- Live deployment link
- PDF report
- Screenshot folder
- Dataset source note

