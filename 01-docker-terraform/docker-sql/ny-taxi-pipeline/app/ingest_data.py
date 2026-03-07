#!/usr/bin/env python3
# coding: utf-8

from urllib.parse import urlparse

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


def is_url(path_or_url: str) -> bool:
    parsed = urlparse(path_or_url)
    return parsed.scheme in ("http", "https")


def infer_file_type(path_or_url: str) -> str:
    p = path_or_url.lower()

    if p.endswith(".parquet"):
        return "parquet"

    if p.endswith(".csv") or p.endswith(".csv.gz"):
        return "csv"

    raise click.ClickException(
        f"Could not infer file type from: {path_or_url}. "
        "Please pass --file-type csv|parquet."
    )


@click.command()
@click.option("--pg-user", envvar="POSTGRES_USER", required=True, help="PostgreSQL user")
@click.option(
    "--pg-pass", envvar="POSTGRES_PASSWORD", required=True, help="PostgreSQL password"
)
@click.option(
    "--pg-host",
    envvar="POSTGRES_HOST",
    default="postgres",
    show_default=True,
    help="PostgreSQL host (docker-compose service name)",
)
@click.option(
    "--pg-port",
    envvar="POSTGRES_PORT",
    default=5432,
    show_default=True,
    type=int,
    help="PostgreSQL port",
)
@click.option("--pg-db", envvar="POSTGRES_DB", required=True, help="PostgreSQL database")
@click.option(
    "--file",
    "file_",
    required=True,
    help="Local file path OR URL (csv/csv.gz/parquet)",
)
@click.option(
    "--file-type",
    type=click.Choice(["csv", "parquet"], case_sensitive=False),
    default=None,
    help="Optional: csv or parquet. If omitted, inferred from extension.",
)
@click.option(
    "--target-table",
    required=True,
    help="Target table name in Postgres (e.g. green_tripdata_2025_11)",
)
@click.option(
    "--datetime-cols",
    default="",
    show_default=False,
    help=(
        "Comma-separated datetime columns to parse (CSV only). "
        "Example: lpep_pickup_datetime,lpep_dropoff_datetime"
    ),
)
@click.option(
    "--chunksize",
    default=100_000,
    show_default=True,
    type=int,
    help="Chunk size for CSV ingestion",
)
def run(
    pg_user,
    pg_pass,
    pg_host,
    pg_port,
    pg_db,
    file_,
    file_type,
    target_table,
    datetime_cols,
    chunksize,
):
    """
    Ingest NYC Taxi data into PostgreSQL from CSV (optionally .gz) or Parquet.
    """

    if file_type is None:
        file_type = infer_file_type(file_)

    file_type = file_type.lower()

    # Normalize datetime cols
    parse_dates = [c.strip() for c in datetime_cols.split(",") if c.strip()]

    engine = create_engine(
        f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )

    click.echo("============================================")
    click.echo(" Ingestion job starting")
    click.echo("============================================")
    click.echo(f"Source      : {file_}")
    click.echo(f"File type   : {file_type}")
    click.echo(f"Target table: {target_table}")
    click.echo(f"Postgres    : {pg_host}:{pg_port}/{pg_db}")
    click.echo("============================================")

    if file_type == "csv":
        df_iter = pd.read_csv(
            file_,
            iterator=True,
            chunksize=chunksize,
            parse_dates=parse_dates if parse_dates else None,
            low_memory=False,
        )

        first = True
        for df_chunk in tqdm(df_iter, desc="CSV chunks"):
            if first:
                df_chunk.head(0).to_sql(
                    name=target_table,
                    con=engine,
                    if_exists="replace",
                    index=False,
                )
                first = False

            df_chunk.to_sql(
                name=target_table,
                con=engine,
                if_exists="append",
                index=False,
            )

    elif file_type == "parquet":
        # 1 file (1 month) is typically OK to load fully
        df = pd.read_parquet(file_)
        df.to_sql(
            name=target_table,
            con=engine,
            if_exists="replace",
            index=False,
        )

    else:
        raise click.ClickException(f"Unsupported file type: {file_type}")

    click.echo("✅ Done.")


if __name__ == "__main__":
    run()
