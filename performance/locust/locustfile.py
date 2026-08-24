from locust import HttpUser, between, task


class GudlftUser(HttpUser):
    wait_time = between(1, 2)

    club_name = "Simply Lift"
    club_email = "john@simplylift.co"
    competition_name = "Open Challenge"

    def _expect(self, response, expected_content):
        if response.status_code != 200 or expected_content not in response.text:
            response.failure(f"Expected {expected_content!r} in an HTTP 200 response")
        else:
            response.success()

    def on_start(self):
        with self.client.post(
            "/showSummary",
            data={"email": self.club_email},
            name="POST /showSummary",
            catch_response=True,
        ) as response:
            self._expect(response, self.club_email)

        with self.client.get(
            f"/book/{self.competition_name}/{self.club_name}",
            name="GET /book/[competition]/[club]",
            catch_response=True,
        ) as response:
            self._expect(response, "How many places?")

        with self.client.post(
            "/purchasePlaces",
            data={
                "competition": self.competition_name,
                "club": self.club_name,
                "places": "1",
            },
            name="POST /purchasePlaces",
            catch_response=True,
        ) as response:
            self._expect(response, "Réservation effectuée avec succès.")

    @task
    def consult_public_points_board(self):
        with self.client.get("/points", name="GET /points", catch_response=True) as response:
            self._expect(response, "Points Board")
