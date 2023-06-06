# Hydrogon stations along truck corridors

This repo contains code to determine where to place hydrogen stations along the highways on the corridor between Rotterdam and Greece.

The code includes:

- Scripts for ingesting raw data files into an SQL database;

## Installation

Update or get `poetry`, and then simply use `poetry install` from the repository root.

## Programs

The following programs are currently available:

- `fill_database`, the ingestion script.
  This script ingests raw data files into an SQL database.

These programs can be ran as `poetry run <script name>`, for example:
```shell
poetry run fill_database
```

Note that most programs depend on data available in the `/home/username/tmp/data/` directory.
This directory is not on GitHub.
