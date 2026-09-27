# Weather Prediction (local run)

## Quick local run with Docker

1. Set your OpenWeather API key in the environment:

```powershell
$env:OPENWEATHER_API_KEY = 'your_openweather_key'
```

2. Build and run with Docker Compose:

```bash
docker compose up --build
```

The API will be available at http://localhost:5000.

Endpoints:
- `/weather?city=London`
- `/weather/extended?city=London`

## Expose to the web (quick)

If you want a temporary public URL, run the app locally and then use `ngrok`:

```bash
# after starting the server locally
ngrok http 5000
```

Copy the generated `https://...` URL and append the endpoints above.

## Notes
- Replace the API key or set the `OPENWEATHER_API_KEY` environment variable before running.
- To run without Docker, install Python 3.11+, create a virtualenv and run `python backend/app.py`.

## One-click deploy to Render

I've added a `render.yaml` file so you can deploy this project to Render with a couple clicks.

Steps:
1. Push this repository to GitHub (create a repo and push all files).
2. Go to Render (https://render.com) and connect your GitHub account.
3. Click "New" → "Web Service" and choose "Import from render.yaml" or connect the repo and select `render.yaml`.
4. In Render's dashboard set `OPENWEATHER_API_KEY` in Environment > Environment Variables.
5. Deploy — Render will give you a public HTTPS URL (the final link).

If you prefer, I can generate a small `git` push script or walk you through pushing to GitHub and connecting to Render step-by-step.
