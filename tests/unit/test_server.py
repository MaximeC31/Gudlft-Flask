import server


def test_initial_data_is_loaded():
    assert len(server.clubs) == 3
    assert len(server.competitions) == 2
    assert server.clubs[0]["points"] == "13"
    assert server.competitions[0]["numberOfPlaces"] == "25"
