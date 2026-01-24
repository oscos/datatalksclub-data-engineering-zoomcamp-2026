#!/usr/bin/env python
# coding: utf-8

import click
import pandas as pd
from sqlalchemy import create_engine
from tqdm.auto import tqdm


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64",
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime",
]


@click.command()
@click.option(
    "--pg-user",
    envvar="POSTGRES_USER",
    required=True,
    help="PostgreSQL user",
)
@click.option(
    "--pg-pass",
    envvar="POSTGRES_PASSWORD",
    required=True,
    help="PostgreSQL password",
)
@click.option(
    "--pg-host",
    envvar="POSTGRES_HOST",
    default="postgres",
    show_default=True,
    help="PostgreSQL host",
)
@click.option(
    "--pg-db",
    envvar="POSTGRES_DB",
    required=True,
    help="PostgreSQL database name",
)
@click.option(
    "--pg-port",
    default=5432,
    show_default=True,
    help="PostgreSQL port",
)
@click.option(
    "--year",
    default=2021,
    show_default=True,
    type=int,
    help="Year of the data",
)
@click.option(
    "--month",
    default=1,
    show_default=True,
    type=int,
    help="Month of the data",
)
@click.option(
    "--target-table",
    default="yellow_taxi_data",
    show_default=True,
    help="Target table name",
)
@click.option(
    "--chunksize",
    default=100_000,
    show_default=True,
    type=int,
    help="Chunk size for reading CSV",
)
def run(
    pg_user,
    pg_pass,
    pg_host,
    pg_port,
    pg_db,
    year,
    month,
    target_table,
    chunksize,
):
    """Ingest NYC Taxi data into PostgreSQL."""

    prefix = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow"
    url = f"{prefix}/yellow_tripdata_{year}-{month:02d}.csv.gz"

    engine = create_engine(
        f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
    )

    df_iter = pd.read_csv(
        url,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunksize,
    )

    first = True

    for df_chunk in tqdm(df_iter):
        if first:
            df_chunk.head(0).to_sql(
                name=target_table,
                con=engine,
                if_exists="replace",
            )
            first = False

        df_chunk.to_sql(
            name=target_table,
            con=engine,
            if_exists="append",
        )


if __name__ == "__main__":
    run()
