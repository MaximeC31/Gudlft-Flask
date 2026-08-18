import pytest
from datetime import datetime, timedelta

import server


@pytest.fixture
def club():
    return {
        "name": "Test Club",
        "email": "test@example.com",
        "points": "4",
    }


@pytest.fixture
def past_competition():
    return {
        "name": "Past Competition",
        "date": (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "numberOfPlaces": "10",
    }


@pytest.fixture
def future_competition():
    return {
        "name": "Future Competition",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "numberOfPlaces": "10",
    }


@pytest.fixture
def isolated_data(monkeypatch, club, past_competition, future_competition):
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [past_competition, future_competition])


@pytest.fixture
def client(isolated_data):
    server.app.config["TESTING"] = True

    with server.app.test_client() as test_client:
        yield test_client
