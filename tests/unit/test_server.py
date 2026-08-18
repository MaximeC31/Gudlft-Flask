import pytest

import server


def test_show_summary_with_unknown_email_displays_error(client):
    response = client.post("/showSummary", data={"email": "unknown@example.com"})

    assert "Adresse électronique inconnue." in response.get_data(as_text=True)


@pytest.mark.parametrize("email", ["", "   "])
def test_show_summary_with_blank_email_displays_unknown_email_error(client, email):
    response = client.post("/showSummary", data={"email": email})

    assert "Adresse électronique inconnue." in response.get_data(as_text=True)


def test_show_summary_with_known_email_displays_club_email(client, club):
    response = client.post(
        "/showSummary",
        data={"email": club["email"]},
    )

    response_text = response.get_data(as_text=True)
    assert club["email"] in response_text


def test_book_past_competition_displays_error(client, club, past_competition):
    response = client.get(f"/book/{past_competition['name']}/{club['name']}")

    response_text = response.get_data(as_text=True)
    assert (
        f"La compétition {past_competition['name']} est passée et ne peut plus être réservée."
        in response_text
    )


def test_purchase_places_for_past_competition_displays_error(client, club, past_competition):
    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": past_competition["name"], "places": "1"},
    )

    response_text = response.get_data(as_text=True)
    assert (
        f"La compétition {past_competition['name']} est passée et ne peut plus être réservée."
        in response_text
    )


def test_book_future_competition_displays_booking_form(client, club, future_competition):
    response = client.get(f"/book/{future_competition['name']}/{club['name']}")

    response_text = response.get_data(as_text=True)
    assert club["name"] in response_text
    assert "<form" in response_text


def test_book_with_falsy_competition_displays_generic_error(client, monkeypatch, club, future_competition):
    class FalsyCompetition(dict):
        def __bool__(self):
            return False

    competition = FalsyCompetition(future_competition)
    monkeypatch.setattr(server, "competitions", [competition])

    response = client.get(f"/book/{competition['name']}/{club['name']}")

    assert "Une erreur est survenue. Veuillez réessayer." in response.get_data(as_text=True)


def test_purchase_places_exceeding_club_points_displays_error(client, club, future_competition):
    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": future_competition["name"], "places": "5"},
    )

    response_text = response.get_data(as_text=True)
    assert "pas assez de points" in response_text


def test_successful_purchase_deducts_club_points_and_competition_places(client, club, future_competition):
    initial_points = int(club["points"])
    initial_places = int(future_competition["numberOfPlaces"])

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": future_competition["name"], "places": "4"},
    )

    response_text = response.get_data(as_text=True)
    assert "Réservation effectuée avec succès." in response_text
    assert club["points"] == initial_points - 4
    assert future_competition["numberOfPlaces"] == initial_places - 4


def test_purchase_more_than_twelve_places_displays_limit_error(client, club, future_competition):
    club["points"] = "13"
    future_competition["numberOfPlaces"] = "13"

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": future_competition["name"], "places": "13"},
    )

    response_text = response.get_data(as_text=True)
    assert "Erreur : le nombre de places demandées dépasse la limite de 12 par réservation." in response_text


def test_purchase_twelve_places_succeeds(client, club, future_competition):
    club["points"] = "12"
    future_competition["numberOfPlaces"] = "12"

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": future_competition["name"], "places": "12"},
    )

    response_text = response.get_data(as_text=True)
    assert "Réservation effectuée avec succès." in response_text
    assert club["points"] == 0
    assert future_competition["numberOfPlaces"] == 0


def test_purchase_places_exceeding_competition_capacity_displays_error(client, club, future_competition):
    future_competition["numberOfPlaces"] = "1"

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": future_competition["name"], "places": "2"},
    )

    response_text = response.get_data(as_text=True)
    assert "Erreur : le nombre de places demandées dépasse la limite de places disponibles." in response_text


def test_purchase_all_remaining_competition_places_succeeds(client, club, future_competition):
    future_competition["numberOfPlaces"] = "4"

    response = client.post(
        "/purchasePlaces",
        data={"club": club["name"], "competition": future_competition["name"], "places": "4"},
    )

    response_text = response.get_data(as_text=True)
    assert "Réservation effectuée avec succès." in response_text
    assert club["points"] == 0
    assert future_competition["numberOfPlaces"] == 0
