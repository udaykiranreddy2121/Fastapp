# FastAPI Rule Evaluation System

A small rule-engine API that parses boolean business rules into an Abstract Syntax Tree (AST), combines rules, and evaluates them against input records.

## Project overview

This project demonstrates:
- Parsing comparison expressions with `pyparsing`
- Representing conditions and boolean operators with an AST
- Exposing rule creation, combination, and evaluation through FastAPI
- Validating API requests with Pydantic

## Technology stack

- Python
- FastAPI
- Pydantic
- pyparsing
- Uvicorn

## Repository structure

```text
Fastapp/
├── my_fastapi_app_py.py
└── README.md
```

## Setup

Use Python 3.10 or later.

```bash
git clone https://github.com/udaykiranreddy2121/Fastapp.git
cd Fastapp
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**
```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install fastapi uvicorn pyparsing
```

## Run the API

The original source file was developed in Google Colab and includes notebook-specific commands and an ngrok section. Run it in its original notebook environment unless you have converted those notebook commands into standard Python first.

For a local FastAPI deployment, the intended launch pattern is:

```bash
uvicorn my_fastapi_app_py:app --reload
```

If the module currently fails to import because of notebook-only syntax, remove notebook magics (such as `!pip install`) and keep package installation in the terminal. Do not put API tokens in source code.

When the server is running, open:
- API root: http://127.0.0.1:8000/
- Interactive Swagger docs: http://127.0.0.1:8000/docs

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/create_rule/` | Parse a rule and return its AST / rule identifier |
| POST | `/combine_rules/` | Combine stored rules using AND |
| POST | `/evaluate_rule/` | Evaluate an AST against a data record |

Example rule expressions supported by the parser include:

```text
age > 30
department = 'Sales'
(age > 30 AND department = 'Sales') OR salary >= 50000
```

The parser uses AND/OR precedence and comparison operators defined in the source. Check the implementation before relying on additional operators or data types.

## Example request shapes

Create a rule:

```json
{
  "rule": "age > 30"
}
```

Evaluate an AST using the structure returned by the create-rule endpoint:

```json
{
  "ast": {
    "type": "operand",
    "value": {
      "var": "age",
      "op": ">",
      "val": "30"
    }
  },
  "data": {
    "age": 35
  }
}
```

The exact AST response serialization depends on the current implementation. Use the live Swagger documentation to inspect request and response schemas.

## Current limitations

- Rules are stored in memory and are lost when the process restarts.
- The rule store is not persistent and is not designed for multi-worker deployment.
- Rule combination currently uses AND.
- The source was originally authored in a Colab notebook; notebook-specific commands and the ngrok setup should be separated before production deployment.
- Add automated tests for invalid rule syntax, missing fields, unknown rule IDs, numeric/string comparisons, and nested AND/OR expressions before treating the API as production-ready.

## Security

- Never commit ngrok tokens, API keys, passwords, or other credentials.
- If a credential has ever been committed, revoke/rotate it at the provider immediately. Removing it from the latest file does not remove it from Git history.
- Use environment variables or a secrets manager for local development and deployment.

## Future improvements

- Persist rules in SQLite or PostgreSQL
- Add rule retrieval and deletion endpoints
- Add stronger request validation and typed AST models
- Add unit and API tests
- Add Docker configuration and CI checks

## License

No license file was present when this README was prepared. Add a license only after choosing the terms under which you want others to use the project.
