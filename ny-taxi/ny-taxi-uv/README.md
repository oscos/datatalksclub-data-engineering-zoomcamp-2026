# NY Taxi - uv version

## Why uv?
  I chose `uv` to understand the modern Python packaging workflow that combines dependency resolution, locking, and virtual environments into a single tool. Although I've always used `pip` in the past, compared to `pip`, `uv` emphasizes reproducibility and speed, which aligns well with Docker-based workflows.

  While `uv` ultimately worked well, it introduced additional mental overhead during the initial setup, especially around `.venv` behavior inside Docker. This project documents those friction points and how they were solved.

## Project Layout
```bash
ny-taxi-uv/
├── app/                 # Python ingestion scripts (non-notebook code)
│   └── ingest_data.py
├── docker-compose.yml   # Orchestrates PostgresSQL, pgAdmin, app tasks
├── Dockerfile           App image: Python + uv + dependencies
├── .dockerignore        # text file listing which files to exclude when creating the docker container
├── .env                 # Local-only environment variables which shouldn't be committed (i.e db_user, db_password, etc)
├── notebooks/           # Jupyter notebooks for exploration / querying
│   └── query-ny-taxi-table.ipynb
├── pyproject.toml       # Python dependencies (uv-managed)
├── README.md
├── uv.lock              # Locked dependency versions for reproducibility
└── .venv                # auto-generated when first executing `docker compose up --build` command
```

>Some directories and files (i.e `.ipynb_checkpoints`, `.venv`) are auto-generated.

## How to Run Ingestion

```bash
docker compose run --rm app \
  python app/ingest_data.py \
  --target-table=yellow_taxi_trips_2021_03 \
  --year=2021 \
  --month=3 \
  --chunksize=100000
```


In order to run this script,


## Why docker compose run (not exec)


## Jupyter + Docker gotchas


## PostgreSQL volumes explained


## Things that confused me (and what I learned)


