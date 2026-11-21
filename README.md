# Cyber Attack Simulator

A full-stack training application for running safe, simulated cyber-attack scenarios, viewing generated logs, and reviewing outcomes. The project has a FastAPI backend and a React/Vite frontend.

> The default configuration uses the **mock** attack engine. Do not enable a Docker-based lab against systems you do not own or have explicit permission to test.

## Run from a GitHub ZIP download

1. On GitHub, select **Code** > **Download ZIP**, then extract the archive.
2. Open a terminal in the extracted `Cyber-Attack-Simulator` folder.
3. Start the backend, then start the frontend in a second terminal.

### Requirements

- Python 3.11 or later
- Node.js 20 or later (includes npm)
- Docker Desktop only if you prefer the Docker option below
- Ollama is optional; install it only if you want local AI-generated content

### 1. Start the backend

PowerShell (Windows):

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
Copy-Item .env.example .env
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

macOS/Linux:

```bash
cd backend
python3.11 -m venv .venv
source .venv/bin/activate
cp .env.example .env
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at `http://127.0.0.1:8000`. Leave this terminal running.

### 2. Start the frontend

Open a **new** terminal in the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints in the terminal—normally `http://localhost:5173`. Requests to `/api` are proxied to the local backend.

## Configuration

`backend/.env` is intentionally excluded from Git because it contains local configuration and may contain secrets. Create it from `backend/.env.example` before running the project.

For local use, the example defaults are ready to use. Before deploying anywhere, replace `SECRET_KEY` with a strong, unique value and use an appropriate production database.

## Run with Docker

Docker Desktop can run both services. First create the backend environment file, then build and start the containers:

```powershell
Copy-Item backend/.env.example backend/.env
docker compose up --build
```

Then open:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

Stop the containers with `docker compose down`.

## Project layout

```text
backend/             FastAPI application and Python requirements
frontend/            React/Vite user interface
docker/              Docker and lab configuration
scenarios/           Scenario data
datasets/            Dataset files
logs/                Runtime output (generated locally; not committed)
```

## Development notes

- Install Python dependencies with `pip install -r backend/requirements.txt`.
- Install frontend dependencies with `npm install` from `frontend/`.
- Do not commit `.env`, virtual environments, generated logs, or `__pycache__` files. The included `.gitignore` excludes these files.
