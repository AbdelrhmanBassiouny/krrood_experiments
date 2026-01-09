# KRROOD Experiments

This repository contains the code to reproduce the experiments for the paper "Knowledge Representation and Reasoning with Object Oriented Design".
Everything has been tested on Ubuntu 24.04.3 with python3.12.3, GraphDB 11.1.2 and PostgreSQL 18.1 (Ubuntu 18.1-1.pgdg24.04+2).

## Prerequisites

- **Python**: Version 3.12 or higher is recommended.
- **GraphDB**: A GraphDB instance running locally with a repository named `KRROOD`.
- **Database**: A relational database (e.g., PostgreSQL) to be used by SQLAlchemy.
- Python requirements found in 

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd krrood_experiments
   ```

2. **Set up a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   This project depends on the `krrood` library. Ensure it is installed in your environment.
   ```bash
   pip install -r requirements.txt
   ```

4. **Install the project in editable mode**:
   ```bash
   pip install -e .
   ```

## Configuration

Set the following environment variable to point to your relational database:

```bash
export KRROOD_EXPERIMENTS_DATABASE_URI="postgresql://user:password@localhost/dbname"
```

## Usage

### Generating the ORM

The SQLAlchemy ORM is generated from the Python model using the `krrood` library:

```bash
python scripts/generate_orm.py
```

### Evaluating Performance

You can run the evaluation scripts for loading and query performance:

```bash
# Evaluate loading performance
python scripts/evaluate_loading_performance.py

# Evaluate query performance
python scripts/evaluate_query_performance.py
```

## Running Tests

Tests are executed using `pytest`:

```bash
pytest
```

