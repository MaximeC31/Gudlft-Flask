import pytest

import server


def test_initial_data_is_loaded():
    assert len(server.clubs) == 3
    assert len(server.competitions) == 2
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"


def test_unknown_email_displays_error(client):
    initial_clubs = [club.copy() for club in server.clubs]
    initial_competitions = [competition.copy() for competition in server.competitions]

    response = client.post("/showSummary", data={"email": "unknown@example.com"})

    assert response.status_code == 200
    assert "Adresse électronique inconnue." in response.get_data(as_text=True)
    assert server.clubs == initial_clubs
    assert server.competitions == initial_competitions


@pytest.mark.parametrize("email", ["", "   "])
def test_empty_email_is_treated_as_unknown(client, email):
    response = client.post("/showSummary", data={"email": email})

    assert response.status_code == 200
    assert "Adresse électronique inconnue." in response.get_data(as_text=True)


def test_known_email_displays_club_summary(client):
    response = client.post(
        "/showSummary",
        data={"email": "john@simplylift.co"},
    )

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "john@simplylift.co" in response_text
    assert "Points available: 13" in response_text


def test_past_competition_is_not_bookable(client):
    response = client.get("/book/Spring Festival/Simply Lift")

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "La compétition Spring Festival est passée et ne peut plus être réservée." in response_text
    assert "<form" not in response_text


def test_purchase_places_without_mutation(client):
    initial_clubs = [club.copy() for club in server.clubs]
    initial_competitions = [competition.copy() for competition in server.competitions]

    response = client.post(
        "/purchasePlaces",
        data={"club": "Simply Lift", "competition": "Spring Festival", "places": "1"},
    )

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "La compétition Spring Festival est passée et ne peut plus être réservée." in response_text
    assert "<form" not in response_text
    assert server.clubs == initial_clubs
    assert server.competitions == initial_competitions


def test_future_competition_is_bookable(client):
    from datetime import datetime, timedelta

    spring_festival = server.competitions[0]
    spring_festival["date"] = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")

    response = client.get("/book/Spring Festival/Simply Lift")

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Simply Lift" in response_text
    assert "<form" in response_text


def test_purchase_places_with_insufficient_points(client, booking_data):
    club, competition = booking_data
    initial_clubs = [club.copy() for club in server.clubs]
    initial_competitions = [competition.copy() for competition in server.competitions]

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "5"},
    )

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "pas assez de points" in response_text
    assert server.clubs == initial_clubs
    assert server.competitions == initial_competitions


def test_purchase_reservation_with_same_points(client, booking_data):
    club, competition = booking_data
    initial_points = club["points"]
    initial_places = int(competition["numberOfPlaces"])

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "4"},
    )

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Réservation effectuée avec succès." in response_text
    assert club["points"] == initial_points
    assert competition["numberOfPlaces"] == initial_places - 4


def test_purchase_places_exceeding_limit(client, booking_data):
    club, competition = booking_data
    club["points"] = "13"
    competition["numberOfPlaces"] = "13"
    initial_clubs = [club.copy() for club in server.clubs]
    initial_competitions = [competition.copy() for competition in server.competitions]

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "13"},
    )

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Erreur : le nombre de places demandées dépasse la limite de 12 par réservation." in response_text
    assert server.clubs == initial_clubs
    assert server.competitions == initial_competitions


def test_purchase_places_at_limit(client, booking_data):
    club, competition = booking_data
    club["points"] = "12"
    competition["numberOfPlaces"] = "12"
    initial_clubs = [club.copy() for club in server.clubs]

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": competition["name"], "places": "12"},
    )

    response_text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Réservation effectuée avec succès." in response_text
    assert server.clubs == initial_clubs
    assert competition["numberOfPlaces"] == 0
