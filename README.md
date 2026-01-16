# KRROOD Experiments

This repository contains the code to reproduce the experiments for the paper "Knowledge Representation and Reasoning with Object Oriented Design".
Everything has been tested on Ubuntu 24.04.3 with python3.12.3, GraphDB 11.1.2 and PostgreSQL 18.1 (Ubuntu 18.1-1.pgdg24.04+2).

## Prerequisites

- **Python**: Version 3.12 or higher is recommended.
- **GraphDB**: A GraphDB instance running locally with a repository named `KRROOD`.
- **Database**: A relational database (e.g., PostgreSQL) to be used by SQLAlchemy.
- **Generated Ontology**: The generated Ontology file which should be used for the experiment
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
## Generating the Ontology File

- Instructions on how to generate the ontology can be found here: https://github.com/kracr/owl2bench?tab=readme-ov-file#usage
- (ToDo, check that!) For this experiment, we use the **OWL2-RL** profile with **1** as the number of universities and seed:  
  `java -jar OWL2Bench.jar 1 RL`

## Changes made to the Ontology 

- ToDo Bass
- To make **Query 5** from the benchmark work, we had to modify an axiom. In its original form, the query returned **0 answers**, which was inconsistent with the other benchmark results, as all other measured queries produced answers.
- To address this, we followed the definition pattern used for the **BasketBallFan** class and added a corresponding general class axiom for **T20CricketFan**.
- Specifically, we introduced the axiom  
  **`Person and (isCrazyAbout some Cricket) ⊑ T20CricketFan`**.
- This change is included in the OWL file and is shown below:

```xml
<owl:Class>
    <owl:intersectionOf rdf:parseType="Collection">
        <rdf:Description rdf:about="http://benchmark/OWL2Bench#Person"/>
        <owl:Restriction>
            <owl:onProperty rdf:resource="http://benchmark/OWL2Bench#isCrazyAbout"/>
            <owl:someValuesFrom rdf:resource="http://benchmark/OWL2Bench#Cricket"/>
        </owl:Restriction>
    </owl:intersectionOf>
    <rdfs:subClassOf rdf:resource="http://benchmark/OWL2Bench#T20CricketFan"/>
</owl:Class>
```
  
## Executing Experiments in Protégé

### Setup

- Download and install Protégé: https://protege.stanford.edu/
- When you start Protégé, you will be greeted by an automatic update pop-up. From there, install the **Pellet Reasoner Plug-In** and **Snap SPARQL Query**.  
  You can also install these via **File → Check for Plugins**.
- After installing the plugins, restart Protégé and open the `.owl` file located at `resources/owl2bench_clean.owl`.
- Run the Pellet reasoner by clicking **Reasoner** in the top menu, selecting **Pellet**, and then clicking **Start Reasoner**.
- To view measurements for loading, reasoning, and querying, open the log by clicking the rightmost button in the footer, next to **Show Inferences**.
- You can open the query interface via **Window → Views → Query Views → Snap SPARQL Query**, then click in the workspace to place the query interface.
- Be aware that the built-in SPARQL Query interface may not work properly and can cause Protégé to freeze.

## Executing Experiments in GraphDB

### Setup
- Download and install GraphDB: https://graphdb.ontotext.com/
- Launch GraphDB and, in the user interface, create a new repository by navigating to **Setup → Repositories → Create new Repository → GraphDB Repository**.
- You can leave all settings as default, except for the ruleset, which should be set to **OWL2-RL**. Then create the repository.
- Add the ontology to GraphDB by navigating to **Import → Upload RDF Files** and selecting the file `resources/owl2bench_clean.owl`.
- Since GraphDB performs reasoning during loading, this process may take some time. Once it is finished, you can execute SPARQL queries using the SPARQL Query Interface in GraphDB.

