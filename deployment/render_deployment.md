# Render Deployment Guide

Render can host Streamlit apps using a free web service plan, subject to current platform limits.

## Build Command

```bash
pip install -r requirements.txt
```

## Start Command

```bash
streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

## Steps

1. Push the project to GitHub.
2. Create a new Render Web Service.
3. Connect the GitHub repository.
4. Select Python environment.
5. Add the build and start commands above.
6. Deploy.

## Environment Variables

No private credentials are required for the current app. If future credentials are needed, add them through Render Environment Variables. Do not commit `.env`.

## Notes

Render free services may sleep after inactivity. Streamlit Community Cloud is usually simpler for academic dashboard submissions.

