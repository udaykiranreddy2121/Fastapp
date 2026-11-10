"""FastAPI rule evaluation API.

Run locally with: uvicorn my_fastapi_app_py:app --reload
"""
from __future__ import annotations

import re
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(
    title="Rule Engine API",
    description="Create, combine, and evaluate eligibility rules using an AST.",
    version="1.0.0",
)

rules_store: dict[int, dict[str, Any]] = {}
_next_rule_id = 1

TOKEN_RE = re.compile(
    r"""\s*(?:(AND|OR)\b|(>=|<=|!=|==|=|>|<)|([A-Za-z_][A-Za-z0-9_.]*)|(-?\d+(?:\.\d+)?)|('(?:[^'\\]|\\.)*'|"(?:[^"\\]|\\.)*")|(\()|(\)))""",
    re.IGNORECASE,
)


def tokenize(expression: str) -> list[str]:
    tokens: list[str] = []
    pos = 0
    while pos < len(expression):
        match = TOKEN_RE.match(expression, pos)
        if not match:
            if expression[pos:].strip() == "":
                break
            raise ValueError(f"Invalid syntax near: {expression[pos:pos + 20]!r}")
        tokens.append(match.group(0).strip())
        pos = match.end()
    if not tokens:
        raise ValueError("Rule cannot be empty")
    return tokens


class Parser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise ValueError("Unexpected end of rule")
        self.pos += 1
        return token

    def parse(self) -> dict[str, Any]:
        node = self.parse_or()
        if self.peek() is not None:
            raise ValueError(f"Unexpected token: {self.peek()}")
        return node

    def parse_or(self) -> dict[str, Any]:
        node = self.parse_and()
        while (self.peek() or "").upper() == "OR":
            self.take()
            node = {"type": "operator", "operator": "OR", "left": node, "right": self.parse_and()}
        return node

    def parse_and(self) -> dict[str, Any]:
        node = self.parse_atom()
        while (self.peek() or "").upper() == "AND":
            self.take()
            node = {"type": "operator", "operator": "AND", "left": node, "right": self.parse_atom()}
        return node

    def parse_atom(self) -> dict[str, Any]:
        if self.peek() == "(":
            self.take()
            node = self.parse_or()
            if self.take() != ")":
                raise ValueError("Missing closing parenthesis")
            return node
        field = self.take()
        if field in {"AND", "OR", ")", "("}:
            raise ValueError("Expected a field name")
        operator = self.take()
        if operator not in {">", "<", ">=", "<=", "=", "==", "!="}:
            raise ValueError(f"Unsupported comparison operator: {operator}")
        raw = self.take()
        if raw.startswith(("'", '"')):
            value: Any = bytes(raw[1:-1], "utf-8").decode("unicode_escape")
        elif re.fullmatch(r"-?\d+", raw):
            value = int(raw)
        elif re.fullmatch(r"-?\d+\.\d+", raw):
            value = float(raw)
        else:
            raise ValueError(f"Invalid comparison value: {raw}")
        return {"type": "condition", "field": field, "operator": operator, "value": value}


def parse_rule(rule: str) -> dict[str, Any]:
    return Parser(tokenize(rule)).parse()


def evaluate(node: dict[str, Any], data: dict[str, Any]) -> bool:
    if node["type"] == "operator":
        if node["operator"] == "AND":
            return evaluate(node["left"], data) and evaluate(node["right"], data)
        return evaluate(node["left"], data) or evaluate(node["right"], data)

    field = node["field"]
    if field not in data:
        raise KeyError(f"Missing field in input data: {field}")
    actual, expected, op = data[field], node["value"], node["operator"]
    try:
        if op in {">", "<", ">=", "<="}:
            if isinstance(actual, bool) or isinstance(expected, bool):
                raise TypeError("Boolean values cannot be ordered")
            if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
                pass
            elif isinstance(actual, str) and isinstance(expected, str):
                pass
            else:
                raise TypeError(f"Incompatible types for field: {field}")
        return {
            ">": lambda: actual > expected,
            "<": lambda: actual < expected,
            ">=": lambda: actual >= expected,
            "<=": lambda: actual <= expected,
            "=": lambda: actual == expected,
            "==": lambda: actual == expected,
            "!=": lambda: actual != expected,
        }[op]()
    except TypeError as exc:
        raise ValueError(str(exc)) from exc


class RuleRequest(BaseModel):
    rule: str = Field(min_length=1)


class CombineRequest(BaseModel):
    rule_ids: list[int] = Field(min_length=2)


class EvaluateRequest(BaseModel):
    rule_id: int
    data: dict[str, Any]


@app.get("/")
def health():
    return {"status": "ok", "service": "Rule Engine API"}


@app.post("/create_rule/")
def create_rule(request: RuleRequest):
    global _next_rule_id
    try:
        ast = parse_rule(request.rule)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    rule_id = _next_rule_id
    _next_rule_id += 1
    rules_store[rule_id] = ast
    return {"rule_id": rule_id, "ast": ast}


@app.post("/combine_rules/")
def combine_rules(request: CombineRequest):
    missing = [rule_id for rule_id in request.rule_ids if rule_id not in rules_store]
    if missing:
        raise HTTPException(status_code=404, detail=f"Unknown rule IDs: {missing}")
    combined = rules_store[request.rule_ids[0]]
    for rule_id in request.rule_ids[1:]:
        combined = {"type": "operator", "operator": "AND", "left": combined, "right": rules_store[rule_id]}
    global _next_rule_id
    rule_id = _next_rule_id
    _next_rule_id += 1
    rules_store[rule_id] = combined
    return {"rule_id": rule_id, "ast": combined}


@app.post("/evaluate_rule/")
def evaluate_rule(request: EvaluateRequest):
    ast = rules_store.get(request.rule_id)
    if ast is None:
        raise HTTPException(status_code=404, detail="Rule ID not found")
    try:
        return {"rule_id": request.rule_id, "result": evaluate(ast, request.data)}
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
