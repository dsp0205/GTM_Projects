# Predictive Churn & Expansion

A customer-health modelling workflow that uses product-usage patterns to identify accounts showing signs of churn risk ahead of renewal.

The project compares a rules-based score with supervised machine-learning models and evaluates how well each approach prioritizes accounts for review.

## Modelling approach

- Generate account and daily product-usage histories.
- Build behavioural features from usage trends, recent activity and changes in consumption.
- Evaluate accounts at a fixed point before renewal.
- Compare a transparent rules-based score with logistic regression and histogram-based gradient boosting.
- Report ranking and classification metrics, including precision at a fixed review capacity, ROC-AUC, PR-AUC and calibration.
- Save the trained boosting model for downstream use.

## Architecture

```text
Account + usage history
          |
          v
    Feature engineering
          |
          v
  Pre-renewal evaluation point
          |
          v
  +-------+---------+
  |                 |
  v                 v
Rules-based      ML models
score            Logistic regression
                 Gradient boosting
  |                 |
  +--------+--------+
           |
           v
     Model comparison
           |
           v
   Prioritized churn-risk
       account list
```

## Files

- `make_data.py` – generates account and usage datasets.
- `features.py` – builds model features.
- `train.py` – trains and evaluates the models.
- `verify_retention.py` – supporting retention verification.

## Tech stack

Python · Pandas · NumPy · scikit-learn · HistGradientBoosting · Joblib

## Design focus

The objective is to give customer teams an earlier and more structured view of renewal risk. The evaluation is designed around a pre-renewal decision point, rather than relying on usage data collected after the outcome is already known.
