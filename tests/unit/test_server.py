import io
from datetime import datetime

import server


def test_valide_date_rejects_past_competition(past_competition):
    assert server.valideDate(past_competition) is False


def test_valide_date_accepts_future_competition(future_competition):
    assert server.valideDate(future_competition) is True


def test_valide_date_rejects_today_competition():
    competition = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    assert server.valideDate(competition) is False


def test_load_clubs_reads_content_clubs(monkeypatch):
    content = '{"clubs": [{"name": "Club 1"}]}'
    opened_files = []

    def fake_open(filename):
        opened_files.append(filename)
        return io.StringIO(content)

    monkeypatch.setattr("builtins.open", fake_open)

    clubs = server.loadClubs()

    assert opened_files == ["clubs.json"]
    assert clubs == [{"name": "Club 1"}]


def test_load_competitions_reads_content_competitions(monkeypatch):
    content = '{"competitions": [{"name": "Competition 1"}]}'
    opened_files = []

    def fake_open(filename):
        opened_files.append(filename)
        return io.StringIO(content)

    monkeypatch.setattr("builtins.open", fake_open)

    competitions = server.loadCompetitions()

    assert opened_files == ["competitions.json"]
    assert competitions == [{"name": "Competition 1"}]
