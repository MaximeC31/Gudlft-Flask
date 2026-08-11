import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime


def valideDate(competition):
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    competitionDate = datetime.strptime(competition["date"], "%Y-%m-%d %H:%M:%S").replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return competitionDate > today


def loadClubs():
    with open("clubs.json") as c:
        listOfClubs = json.load(c)["clubs"]
        return listOfClubs


def loadCompetitions():
    with open("competitions.json") as comps:
        listOfCompetitions = json.load(comps)["competitions"]
        return listOfCompetitions


app = Flask(__name__)
app.secret_key = "something_special"

competitions = loadCompetitions()
clubs = loadClubs()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/showSummary", methods=["POST"])
def showSummary():
    email = request.form.get("email", "").strip()
    club = next((club for club in clubs if club["email"] == email), None)
    if club is None:
        flash("Adresse électronique inconnue.")
        return render_template("index.html"), 200
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/book/<competition>/<club>")
def book(competition, club):
    foundClub = [c for c in clubs if c["name"] == club][0]
    foundCompetition = [c for c in competitions if c["name"] == competition][0]

    if foundCompetition and not valideDate(foundCompetition):
        flash(
            f"La compétition {foundCompetition['name']} est passée "
            "et ne peut plus être réservée."
        )
        return render_template("welcome.html", club=foundClub, competitions=competitions)

    if foundClub and foundCompetition and valideDate(foundCompetition):
        return render_template("booking.html", club=foundClub, competition=foundCompetition)
    else:
        flash("Une erreur est survenue. Veuillez réessayer.")
        return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/purchasePlaces", methods=["POST"])
def purchasePlaces():
    competition = [c for c in competitions if c["name"] == request.form["competition"]][0]
    club = [c for c in clubs if c["name"] == request.form["club"]][0]
    if competition and not valideDate(competition):
        flash(
            f"La compétition {competition['name']} est passée "
            "et ne peut plus être réservée."
        )
        return render_template("welcome.html", club=club, competitions=competitions)

    placesRequired = int(request.form["places"])
    competition["numberOfPlaces"] = int(competition["numberOfPlaces"]) - placesRequired

    flash("Réservation effectuée avec succès.")
    return render_template("welcome.html", club=club, competitions=competitions)


@app.route("/logout")
def logout():
    return redirect(url_for("index"))
