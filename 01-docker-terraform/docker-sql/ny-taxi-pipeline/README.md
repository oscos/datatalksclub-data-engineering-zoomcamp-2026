# NY Taxi - uv version

## Why uv?
  I chose `uv` to understand the modern Python packaging workflow that combines dependency resolution, locking, and virtual environments into a single tool. Although I've always used `pip` in the past, compared to `pip`, `uv` emphasizes reproducibility and speed, which aligns well with Docker-based workflows.

  While `uv` ultimately worked well, it introduced additional mental overhead during the initial setup, especially around `.venv` behavior inside Docker. This project documents those friction points and how they were solved.

## Project Layout
```bash
ny-taxi-uv/
  ├── app
  │   └── ingest_data.py   # Python ingestion script (non-notebook code)
  ├── data                 # Files used for ingestion
  │   ├── green_tripdata_2025-11.parquet
  │   └── taxi_zone_lookup.csv
  ├── docker-compose.yml   # Orchestrates PostgresSQL, pgAdmin, app tasks
  ├── Dockerfile           # App image: Python + uv + dependencies
  ├── .dockerignore        # text file listing which files to exclude when creating the docker container
  ├── .env                 # Local-only environment variables which shouldn't be committed (i.e db_user, db_password, etc)
  ├── .env.example         # Sample reminder file which can be used to copy as `.env` file and edited as needed
  ├── notebooks            # Jupyter notebooks for exploration / querying
  │   └── query-ny-taxi-table.ipynb
  ├── pyproject.toml       # Python dependencies (uv-managed)
  ├── README.md
  ├── uv.lock              # Locked dependency versions for reproducibility
  └── .venv                # auto-generated when first executing `docker compose up --build` command
```

>Some directories and files (i.e `.ipynb_checkpoints`, `.venv`) are auto-generated.

## How to Run Ingestion

In order to run this script within the terminal inside of the directory where docker-compose.yml is located:

```bash
docker compose run --rm app \
  python app/ingest_data.py \
  --target-table=yellow_taxi_trips_2021_03 \
  --year=2021 \
  --month=3 \
  --chunksize=100000
```

## Why docker compose run (not exec)
`docker compose run` was used instead of `docker compose exec`

At first, this was confusing. 

My instict was:
>"Why spin up a brand new container when we already have a running network of containers? That feels wasteful."

After digging deeper, I realized this is actually the intended and more efficient pattern for batch jobs like ingestion.

`docker compose run`: 
> Used for one-off tasks (ETL, migrations, scripts)

What it does:
- Starts a new container from the `app` service definition
- Connects it to the same Docker Compose network
- Injects the same environment variables
- Mounts the same volumes
- Runs the command once
- Removes the container with `--rm`

This makes ingestion:
- repeatable
- isolated
- disposable
- predictable

Since ingestion is repeatable and stateless, `run` keeps the workflow predictable and avoids leaving around idle containers.

`docker compose exec`:
> Used for interacting with an already running container

Best for:
- debugging 
- manual inspection
- interactive commands

It assumes a long-lived container is already running.

## Jupyter + Docker gotchas


## PostgreSQL volumes explained


## Things that confused me (and what I learned)

> Isn't creating a new container wasteful?

I originally thought that spinning p a new container for each ingestion run was inefficient compared to using an existing container.

In reality:

- Containers are designed to be `ephemeral`, that is temporary and just long enough to complete the task at hand.
- Starting a container is cheap (seconds, minimal resources)
- Idle containers are actually worse:
  - easy to forget about
  - may drift in state
  - may require restarts anyway
  - consume memory/CPU over time

Rather than keeping utility containers running indefinitely, modern container workflows prefer:
- start -> run -> destroy

> How does the new container automatically know about Postgres and pgAdmin?

This part was not obvious at first. 

The reason is:

When you run: 

```bash
docker compose runn app ...
```

Docker Compose does not create a random container. Instead it creates a container using the `service definition` from `docker-compose.yml` which includes:
- the same network
- the same environment variables
- the same volumes
- the same DNS/service discovery

So the new container automatically:
- joins the project network (i.e `ny-taxi-default`)
- can resolve services by name:
  - `postgres`
  - `pgadmin`
- receives variables like:
  - `POSTGRES_HOST`
  - `POSTGRES_USER`
- mounts any shared volumes

In practice, this means the ingestion container behaves like it has always been part of the system, even though it only exists temporarily.

This is why code like this works without extra configuration:

```python
host="postgres"
```

Docker's internal DNS resolves `postgres` to the running Postgres container on the same Compose network

> Mental model shift

Before:
- Containers felt like long-running "mini servers"

After:
- Containers are `disposable execution environments`
- Docker Compose defines the system
- `docker compose run` creates temporary workers inside that system

That realization made the ingestion workflow make much more sense:
- posgres = long-lived service
- pgadmin = long-lived service
- ingestion = short-lived job container that joins the same ecosystem when needed.