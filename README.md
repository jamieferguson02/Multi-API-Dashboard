# Multi-API Dashboard

A Python desktop app that pulls live data from four public APIs into a single dashboard. Enter a country to see its flag, key details, a 24-hour temperature forecast and its public holidays, or use the separate search box to find recipes.

Built as coursework for TODO: module name at Belfast Met (TODO: year).

## Screenshots

TODO: add screenshots

## Features

- Country lookup showing the flag and key country details
- 24-hour temperature chart for the selected country
- Public holidays for the selected country
- Recipe search
- Runs locally or in a Docker container

## Tech stack

- Python 3.11
- Tkinter / ttk (GUI)
- matplotlib (charts)
- Pillow (flag images)
- requests (API calls)
- pytest (testing)
- Docker

## APIs used

None of these APIs require a private key.

| API | Used for | Endpoint |
|---|---|---|
| REST Countries | Country details and flags | `https://restcountries.com/v3.1/name/{country}` |
| Open-Meteo | Weather forecast | `https://api.open-meteo.com/v1/forecast` |
| Nager.Date | Public holidays | `https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}` |
| TheMealDB | Recipe search | `https://www.themealdb.com/api/json/v1/1/search.php?s={query}` |

The `1` in the TheMealDB URL is their published public test key.

## Getting started

### Prerequisites

- Python 3.11 or later
- Docker Desktop (only needed to run in a container)

### Clone the repository

```bash
git clone https://github.com/jamieferguson02/TODO-repo-name.git
cd TODO-repo-name
```

### Run locally

Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate it with `source .venv/bin/activate` instead.

Install the dependencies and start the app:

```powershell
python -m pip install -r requirements.txt
python dashboard.py
```

### Run the tests

```powershell
python -m pytest
```

### Run with Docker

Tkinter is a desktop GUI, so the container needs a display to draw its window on. On Windows, install and start an X server such as VcXsrv before running the container.

Build the image:

```powershell
docker build -t multiapi-dashboard:latest .
```

Run the container:

```powershell
docker run --rm -it multiapi-dashboard:latest
```

The Dockerfile already sets the start command (`python dashboard.py`) and the display settings, so no extra options are needed.

For development, you can mount your local code into the container so changes are picked up without rebuilding the image:

```powershell
docker run --rm -it -e DISPLAY=host.docker.internal:0.0 -v ${PWD}:/app -w /app multiapi-dashboard:latest python dashboard.py
```

## Project structure

```
├── dashboard.py        # Main application
├── tests/
│   └── test_basic.py   # pytest tests
├── requirements.txt
├── Dockerfile
└── .dockerignore
```
