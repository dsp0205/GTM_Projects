# AI Sales Enablement & Objection Battle Cards

An AI-assisted workflow that turns lost-call feedback and sales conversations into structured objection themes and practical battle-card guidance.

The system connects what buyers say, how sales representatives respond, and the product facts that can credibly support an answer.

## Workflow

1. Extract and structure objection examples from call data.
2. Cluster similar objections into recurring themes.
3. Retrieve relevant product facts from a ChromaDB knowledge collection.
4. Generate battle-card entries with structured model output.
5. Restrict proof points to known fact IDs and call references.
6. Produce a Markdown battle card for sales enablement.

## Architecture

```text
Lost-call transcripts + objection examples
                  |
                  v
           Theme extraction
                  |
                  v
            Objection clusters
                  |
                  v
         ChromaDB fact retrieval
                  |
                  v
       Structured LLM generation
                  |
                  v
       Fact + call reference checks
                  |
                  v
          Markdown battle card
```

## Included components

- `extract.py` – transcript and objection extraction.
- `cluster.py` – objection theme clustering.
- `card.py` – retrieval-assisted battle-card generation.
- `facts.md` – product fact source material.
- `lost_calls.json` and `objections.json` – working datasets.
- `battle_card.md` – generated battle-card output.

## Tech stack

Python · Anthropic API · ChromaDB · Embeddings · Structured outputs · RAG

## Design focus

The goal is to make sales guidance useful and defensible. Recommendations are tied back to source call examples and product facts, rather than allowing a language model to invent product claims.
