import pytest
from datetime import datetime, timedelta

import server


@pytest.fixture(autouse=True)
def isolated_data(monkeypatch):
    monkeypatch.setattr(server, "clubs", server.loadClubs())
    monkeypatch.setattr(server, "competitions", server.loadCompetitions())


@pytest.fixture
def client(isolated_data):
    server.app.config["TESTING"] = True

    with server.app.test_client() as test_client:
        yield test_client


@pytest.fixture
def booking_data(monkeypatch):
    club = {"name": "Test Club", "email": "test@example.com", "points": "4"}
    competition = {
        "name": "Future Competition",
        "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S"),
        "numberOfPlaces": "10",
    }
    monkeypatch.setattr(server, "clubs", [club])
    monkeypatch.setattr(server, "competitions", [competition])
    return club, competition
