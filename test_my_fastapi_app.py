from fastapi.testclient import TestClient
from my_fastapi_app_py import app, rules_store

client = TestClient(app)


def setup_function():
    rules_store.clear()


def test_create_and_evaluate_rule():
    created = client.post('/create_rule/', json={'rule': "age >= 30 AND department = 'Sales'"})
    assert created.status_code == 200
    rule_id = created.json()['rule_id']
    evaluated = client.post('/evaluate_rule/', json={
        'rule_id': rule_id,
        'data': {'age': 35, 'department': 'Sales'}
    })
    assert evaluated.status_code == 200
    assert evaluated.json()['result'] is True


def test_parentheses_and_or_precedence():
    created = client.post('/create_rule/', json={
        'rule': "(age < 25 OR age >= 65) AND department = 'Sales'"
    })
    response = client.post('/evaluate_rule/', json={
        'rule_id': created.json()['rule_id'],
        'data': {'age': 70, 'department': 'Sales'}
    })
    assert response.status_code == 200
    assert response.json()['result'] is True


def test_missing_field_returns_400():
    created = client.post('/create_rule/', json={'rule': 'age > 30'})
    response = client.post('/evaluate_rule/', json={
        'rule_id': created.json()['rule_id'], 'data': {}
    })
    assert response.status_code == 400


def test_invalid_rule_returns_400():
    response = client.post('/create_rule/', json={'rule': 'age >> 30'})
    assert response.status_code == 400
