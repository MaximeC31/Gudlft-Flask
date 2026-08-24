# Güdlft - Gestion de réservations de compétitions

Application Web Flask permettant aux secrétaires de clubs de réserver des places en compétition avec les points de leur club. Le projet met l'accent sur la validation des règles métier, les tests automatisés et la mesure des performances.

## Fonctionnalités

- Connexion d'un club avec une adresse électronique connue
- Affichage des compétitions, de leurs dates et des places restantes
- Réservation uniquement pour les compétitions futures
- Limite de 12 places par réservation
- Refus des réservations dépassant les points du club ou la capacité disponible
- Mise à jour conjointe des points du club et des places de la compétition
- Tableau public en lecture seule des clubs et de leurs points
- Messages d'erreur sans mutation des données pour les refus métier

## Stack

- Python 3.14
- Flask 3.1
- Jinja2
- pytest et pytest-cov
- Locust 2
- Fichiers JSON en mémoire

## Installation

Prérequis : Python 3.14 et `pip`.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Lancement

Depuis la racine du projet :

```bash
.venv/bin/python -m flask --app server run
```

L'application est accessible sur `http://127.0.0.1:5000/`.

Si le port est déjà utilisé :

```bash
.venv/bin/python -m flask --app server run --port 5001
```

## Routes principales

- `GET /` : page d'accueil et formulaire de connexion
- `POST /showSummary` : connexion d'un club par adresse électronique
- `GET /points` : tableau public des points des clubs
- `GET /book/<competition>/<club>` : formulaire de réservation d'une compétition
- `POST /purchasePlaces` : validation et enregistrement d'une réservation
- `GET /logout` : retour à l'accueil

## Tests

Exécuter la suite complète et le rapport de couverture :

```bash
.venv/bin/python -m pytest
```

La configuration exige au moins 60 % de couverture sur `server.py`.

Exécuter un test d'intégration ciblé sans contrôle de couverture :

```bash
.venv/bin/python -m pytest --no-cov tests/integration/test_routes.py::test_show_summary_with_unknown_email_displays_error
```

## Test de performance

Démarrer l'application dans un nouveau processus, puis lancer Locust :

```bash
.venv/bin/locust -f performance/locust/locustfile.py --host=http://127.0.0.1:5000 --headless -u 6 -r 6 -t 10s
```

Le scénario exécute six réservations en mémoire. Il doit produire zéro échec, un p95 inférieur à 5 secondes pour `GET /points` et inférieur à 2 secondes pour `POST /purchasePlaces`.

## Parcours principal

1. Le secrétaire saisit l'adresse électronique de son club.
2. Il consulte son solde de points et les compétitions disponibles.
3. Il ouvre le formulaire d'une compétition future.
4. Il demande un nombre de places dans la limite de 12, des points disponibles et de la capacité restante.
5. Une réservation valide déduit les points et les places, puis affiche les nouveaux soldes.
6. Tout refus métier laisse les données inchangées.

## Structure

- `server.py` : application Flask, routes et règles métier
- `templates/` : pages Jinja2
- `clubs.json` : données initiales des clubs
- `competitions.json` : données initiales des compétitions
- `tests/unit/` : tests unitaires
- `tests/integration/` : tests des routes Flask
- `performance/locust/` : scénario de test de performance

## Limites actuelles

- Les réservations sont conservées uniquement en mémoire et sont annulées au redémarrage.
- Les ressources absentes, les dates mal formées et les quantités non entières ne sont pas gérées de façon contrôlée.
- Les tests fonctionnels Selenium ne sont pas encore implémentés.
