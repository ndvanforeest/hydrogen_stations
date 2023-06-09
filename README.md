# Hydrogon stations along truck corridors

This repo contains code to determine where to place hydrogen stations along the highways on the corridor between Rotterdam and Greece.

The code includes:

- Scripts for ingesting raw data files into an SQL database;

## Installation

Update or get `poetry`, and then simply use `poetry install` from the repository root. If this fails, which it did on my machine, run `poetry env use python3` first, to ensure that `poetry` does not think that the system environment is the active project environment.

## Programs

The following programs are currently available:

- `ingest`, the ingestion script.
  This script ingests raw data files into an SQL database.
- `plot`, the plotting script.
  This script plots fuel and charging stations near trunks and motorways

These programs can be ran as `poetry run <script name>`, for example:
```shell
poetry run ingest
```

Note that most programs depend on data available in the `/home/username/tmp/data/` directory.
This directory is not on GitHub.
