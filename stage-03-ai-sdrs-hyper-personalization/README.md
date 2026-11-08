# AI SDR & Evidence-Led Prospect Personalization

An AI-assisted prospect research workflow that turns public activity into relevant, evidence-backed outbound email drafts.

The goal is not to generate more generic emails. It is to identify a specific signal, verify that the signal is supported by its source, and only then use it as context for a draft.

## Workflow

1. **Load prospects** from a CSV file.
2. **Gather public activity** from GitHub, or load local fixtures for a predictable mock run.
3. **Extract potential hooks** using a structured LLM response.
4. **Verify evidence** by checking that the quoted text exists in the supplied source content and that the source URL is known.
5. **Generate a draft** using the verified hook and a defined offer.
6. **Apply checks** for length, banned phrases and source consistency.
7. **Send for human review**. The workflow does not send emails automatically.

## Architecture

```text
Prospect CSV
    |
    v
Public GitHub activity ---- Local fixture mode
    |                              |
    +--------------+---------------+
                   v
            Evidence collection
                   |
                   v
          Structured hook extraction
                   |
                   v
        Quote + source verification
                   |
             Verified hook
                   |
                   v
          Personalized email draft
                   |
                   v
          Rule-based quality checks
                   |
                   v
             Human review
                   |
             JSON draft output
```

## What makes the workflow useful

- **Evidence before personalization:** a hook must be traceable to supplied source content.
- **Structured model output:** hook extraction and email writing use JSON schemas.
- **Quote-or-drop logic:** unsupported quotes or source URLs are discarded.
- **Guardrails:** drafts are checked for length, unwanted phrases and source mismatches.
- **Human-in-the-loop:** outputs are marked `needs_review`; the workflow does not trigger outbound sending.

## Run locally

Install the Python dependencies used by the project:

```bash
pip install anthropic python-dotenv requests
```

Set your Anthropic API key in the environment:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

Run using the supplied mock evidence fixtures:

```bash
python run.py prospects.csv --mock
```

Generated draft JSON files are written to the `drafts/` directory.

For live public GitHub activity, run without `--mock`. Set `GITHUB_TOKEN` if you want to use an authenticated GitHub API request, and make sure the prospect CSV contains the expected fields: `name`, `title`, `company`, `email` and `github_login`.

## Tech stack

Python · Anthropic API · GitHub REST API · JSON Schema · Requests

## Design focus

The central design choice is to make personalization accountable. The model can suggest a useful angle, but the workflow checks the supporting quote and source before allowing that angle into an outbound draft.
