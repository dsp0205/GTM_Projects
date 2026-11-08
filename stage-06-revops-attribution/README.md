# Multi-Touch Revenue Attribution & RevOps Analytics

A revenue analytics project that compares rule-based and data-driven approaches to assigning credit across marketing and sales touchpoints.

It combines SQL models, Python analysis and a locally generated HTML report to explore how different attribution methods tell different stories about the same customer journeys.

## What it includes

### Rule-based attribution

Five SQL models provide different views of sourced revenue:

- First touch
- Last touch
- Linear
- U-shaped
- Time decay

The models use won opportunities and associated touchpoints within the defined attribution window.

### Data-driven approaches

- **Markov removal effect:** estimates how the model's conversion probability changes when a channel is removed from the journey.
- **Shapley value:** distributes conversion credit across channel combinations using marginal contributions.

### Supporting analysis

- Synthetic account, contact, touchpoint and opportunity data.
- Funnel analysis to examine progression and leakage.
- Cohort analysis based on account creation timing.
- A holdout simulation for exploring incremental-lift comparisons.
- A local HTML dashboard to review the outputs together.

## Architecture

```text
Synthetic data generator
          |
          v
       DuckDB
          |
     +----+------------------+
     |                       |
     v                       v
 SQL attribution         Funnel + cohort
     models                analysis
     |                       |
     v                       |
 Sourced revenue             |
 by channel                  |
     |                       |
     +-----------+-----------+
                 |
                 v
       HTML reporting layer

DuckDB journeys --> Markov removal effect
                --> Shapley attribution
```

## Run locally

Install the dependencies:

```bash
pip install duckdb numpy pandas
```

Generate the sample dataset:

```bash
python gen_data.py
```

Run the rule-based attribution and generate the HTML dashboard:

```bash
python dashboard.py
```

Open `dashboard.html` in a browser.

Run the data-driven attribution analysis:

```bash
python data_driven.py
```

The scripts use `revops.duckdb` as their local database.

## Understanding the data

The dataset is generated for analysis rather than sourced from a live CRM or marketing platform. The channel mix, account journeys and opportunity outcomes are simulated so that the different methods can be explored under controlled assumptions.

The output should therefore be read as a comparison of modelling approaches, not as measured campaign performance or a claim about real-world channel lift.

## Tech stack

Python · SQL · DuckDB · Pandas · NumPy · HTML

## Design focus

Attribution is a modelling choice, not an objective fact. This project makes it possible to compare several approaches, inspect how they distribute credit, and understand why a revenue team should be careful about treating any single attribution view as the full story.
