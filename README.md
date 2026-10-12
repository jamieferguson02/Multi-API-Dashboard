# Multi-API Dashboard

A Python desktop application that brings data from four free public APIs together in one window. Enter a country to see its flag, key facts, a 24-hour temperature chart for its capital and a list of its public holidays. A separate search box lets you look up recipes.

Built for the **Advanced Cloud Development Technologies** module at Belfast Met.

## Features

- **Country lookup**: shows the flag, common and official name, capital, region and subregion, population, bordering countries and two-letter country code
- **Weather**: shows the current temperature and an hourly temperature line chart covering 24 hours, using the capital's coordinates
- **Public holidays**: lists up to 20 public holidays for the selected country (for 2025)
- **Recipe search**: search by meal name, then select a result to see its category, cuisine, ingredients with measurements and cooking instructions
- **Responsive interface**: API calls run in background threads so the window doesn't freeze while it waits for data, and a status bar shows progress
- **Error handling**: every request has an 8-second timeout, and failed requests are reported in a dialog or the status bar instead of crashing the app
- **Docker support**: includes a Dockerfile so the app can run in a container

## Tech stack

| Technology | Purpose |
|---|---|
| Python 3.11 | Core language |
| Tkinter / ttk | Desktop GUI |
| requests | HTTP calls to the APIs |
| matplotlib | Temperature chart embedded in the Tkinter window |
| Pillow | Loading and resizing flag images |
| pytest | Testing |
| Docker | Containerising the application |

## APIs used

None of these APIs need a private key or an account.

| API | Used for | Endpoint |
|---|---|---|
| [REST Countries](https://restcountries.com/) | Country details and flags | `https://restcountries.com/v3.1/name/{country}` |
| [Open-Meteo](https://open-meteo.com/) | Weather forecast | `https://api.open-meteo.com/v1/forecast` |
| [Nager.Date](https://date.nager.at/) | Public holidays | `https://date.nager.at/api/v3/PublicHolidays/{year}/{country_code}` |
| [TheMealDB](https://www.themealdb.com/) | Recipe search | `https://www.themealdb.com/api/json/v1/1/search.php?s={query}` |

The `1` in the TheMealDB URL is the free public test key that TheMealDB publishes.

## How it works

1. The user enters a country name and clicks **Search**.
2. The app requests the country's details from REST Countries and uses the first match.
3. It uses the capital's latitude and longitude to request an hourly forecast from Open-Meteo. If the country has no coordinates, it falls back to London's.
4. It uses the two-letter country code (for example `GB`) to request public holidays from Nager.Date.
5. Each result is shown in its own panel: country details and holidays on the left, the temperature chart in the middle and recipe results on the right.

The API functions (`fetch_country`, `fetch_weather`, `fetch_holidays` and `fetch_meals`) are kept separate from the GUI class (`DashboardApp`). This keeps the data-fetching logic independent of the interface.

## Getting started

### Prerequisites

- Python 3.11 or later, with Tkinter. Tkinter comes with the standard Windows and macOS installers. On some Linux distributions you need to install it separately, for example with `sudo apt install python3-tk`.
- An internet connection, as all data comes from live APIs
- Docker Desktop (only needed to run the app in a container)

### Clone the repository

```bash
git clone https://github.com/jamieferguson02/Multi-API-Dashboard.git
cd Multi-API-Dashboard
```

### Run locally

Create and activate a virtual environment.

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies and start the app:

```bash
python -m pip install -r requirements.txt
python dashboard.py
```

The country box opens with **United Kingdom** filled in, so you can click **Search** straight away. To try the recipe search, enter a meal name such as `chicken` or `pasta` and click **Find Meal**.

### Run the tests

From the project root:

```bash
python -m pytest
```

The tests in `tests/test_basic.py` are basic checks. They confirm that `dashboard.py` imports correctly, that the TheMealDB URL constant is set and that the `fetch_holidays` function exists. They do not call the live APIs.

### Run with Docker

Tkinter is a desktop GUI, so the container needs a display to draw its window on. On Windows, install and start an X server such as [VcXsrv](https://sourceforge.net/projects/vcxsrv/) before running the container. You may need to tick **Disable access control** when you start VcXsrv so the container can connect to it.

Build the image:

```bash
docker build -t multiapi-dashboard:latest .
```

Run the container:

```bash
docker run --rm -it multiapi-dashboard:latest
```

The Dockerfile already sets the start command (`python dashboard.py`) and points `DISPLAY` at `host.docker.internal:0.0`, so no extra options are needed when you use Docker Desktop.

For development, you can mount your local code into the container so changes are picked up without rebuilding the image (PowerShell syntax):

```powershell
docker run --rm -it -e DISPLAY=host.docker.internal:0.0 -v ${PWD}:/app -w /app multiapi-dashboard:latest python dashboard.py
```

## Project structure

```
Multi-API-Dashboard/
├── dashboard.py        # API functions and the Tkinter application
├── tests/
│   └── test_basic.py   # pytest tests
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image definition
├── .dockerignore
├── .gitignore
└── README.md
```

## Skills demonstrated

- **Working with REST APIs**: sending HTTP requests with query parameters, handling timeouts and HTTP errors, and parsing nested JSON responses
- **Combining data sources**: using the output of one API (coordinates and country code) as the input to others
- **GUI development**: building a multi-panel desktop interface with Tkinter and ttk, and embedding a matplotlib chart in it
- **Concurrency**: running network calls in background threads to keep the interface responsive
- **Containerisation**: writing a Dockerfile, installing system packages for a GUI app and running a GUI app from a container through an X server
- **Testing**: setting up pytest for a Python project
- **Code organisation**: keeping data-fetching functions separate from the user interface

## Known limitations

- The holiday year is fixed at 2025 in the code, rather than following the current year.
- Country search uses the first match REST Countries returns, so a partial name may pick an unexpected country.
- The tests only check that the code is set up correctly. They do not test the API parsing or the interface.
