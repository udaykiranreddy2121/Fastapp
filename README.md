# Rule Engine API

A Python and FastAPI project that parses eligibility expressions into an Abstract Syntax Tree (AST), combines saved rules with AND logic, and evaluates the resulting rules against JSON input.

## Features

- Parse comparison expressions such as `age >= 30` and `department = 'Sales'`.
- Support parentheses and logical `AND` / `OR` operators (`AND` has higher precedence).
- Create and store rules in memory.
- Combine two or more saved rules using AND.
- Evaluate a saved rule against supplied JSON data.
- Interactive API documentation through Swagger UI.

## Tech stack

Python, FastAPI, Pydantic, Uvicorn, recursive-descent parsing, Abstract Syntax Trees.

## Setup

```bash
git clone https://github.com/udaykiranreddy2121/Fastapp.git
cd Fastapp
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn my_fastapi_app_py:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for the interactive API.

## Example requests

Create a rule:

```json
POST /create_rule/
{"rule": "(age >= 30 AND department = 'Sales') OR salary > 50000"}
```

Evaluate the returned `rule_id`:

```json
POST /evaluate_rule/
{"rule_id": 1, "data": {"age": 35, "department": "Sales", "salary": 42000}}
```

Combine existing rules:

```json
POST /combine_rules/
{"rule_ids": [1, 2]}
```

The combined rule is stored as a new rule and can be evaluated using its returned ID.

## Limitations

- Rules are stored in memory and are cleared when the server restarts.
- This is a learning/demo project, not a production authorization engine.
- Supports scalar string and numeric comparisons; it does not execute arbitrary Python code.

## Future improvements

Persistent storage, authentication, rule versioning, richer validation, and automated test coverage.

## License

No license is specified yet. Add a license file if you want others to reuse the code.
