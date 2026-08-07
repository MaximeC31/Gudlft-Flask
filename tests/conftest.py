import pytest

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
