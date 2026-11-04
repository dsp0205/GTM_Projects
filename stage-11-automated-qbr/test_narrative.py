import pandas as pd
import pytest
import metrics
import narrative
from narrative import Summary

@pytest.fixture
def facts():
    acct = pd.read_csv("accounts.csv").iloc[0]
    return metrics.compute(acct, pd.read_csv("usage.csv"), pd.Period("2026Q3"))

def test_fallback_passes_its_own_check(facts):
    narrative.check(narrative.fallback(), facts)

def test_model_digits_are_rejected(facts):
    bad = Summary(headline="You saved 500 hours.", bullets=["{tasks}", "{roi}", "{cost}"])
    with pytest.raises(ValueError):
        narrative.check(bad, facts)

def test_unknown_fact_id_is_rejected(facts):
    bad = Summary(headline="{made_up} saved.", bullets=["{tasks}", "{roi}", "{cost}"])
    with pytest.raises(ValueError):
        narrative.check(bad, facts)

def test_malformed_placeholder_is_rejected(facts):
    bad = Summary(headline="{hours-saved} saved.", bullets=["{tasks}", "{roi}", "{cost}"])
    with pytest.raises(ValueError):
        narrative.check(bad, facts)
