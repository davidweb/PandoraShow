import random
import string
import time
from datetime import datetime
import json  # Import the json library

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config["SECRET_KEY"] = "UNE_CLE_SECRETE_LONGUE"
socketio = SocketIO(app)

# ===============================
#   Données en mémoire
# ===============================
# Liste des joueurs : { "user_id": {"username": "...", "team": 1 ou 2} }
players = {}
# Scores des deux équipes
scores = {1: 0, 2: 0}
# Thème en cours
current_theme = "Aucun thème sélectionné"
# Countdown global (secondes restantes)
countdown_seconds = 0
# État du countdown
countdown_running = False
# Questions pour le quiz (question, réponse)
quiz_questions = [] # Initialize as an empty list, will be loaded from JSON
current_quiz_question_index = -1 # Index de la question actuelle, -1 = pas de question en cours

# Pour la gestion admin (mot de passe = 123456)
ADMIN_PASSWORD = "123456"

# ===============================
#   Fonctions utilitaires
# ===============================
def generate_user_id():
    """Génère un ID unique (genre 'ABC123') pour identifier un joueur."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

def auto_assign_teams():
    """Répartit automatiquement les joueurs en 2 équipes (1 et 2).
    Logique simplifiée : on compte combien il y a de joueurs, on en met la moitié dans la team 1, l'autre dans la 2."""
    all_player_ids = list(players.keys())
    random.shuffle(all_player_ids)
    half = len(all_player_ids) // 2
    for i, pid in enumerate(all_player_ids):
        if i < half:
            players[pid]["team"] = 1
        else:
            players[pid]["team"] = 2

def get_current_quiz_question():
    """Récupère la question actuelle ou None si plus de questions."""
    global quiz_questions, current_quiz_question_index
    if 0 <= current_quiz_question_index < len(quiz_questions):
        return quiz_questions[current_quiz_question_index]
    return None

def set_next_quiz_question():
    """Passe à la question de quiz suivante."""
    global current_quiz_question_index
    current_quiz_question_index += 1
    return get_current_quiz_question()


# ===============================
#   Routes Flask
# ===============================
@app.route("/")
def index():
    """Page d'accueil : si l'utilisateur n'est pas logué, on lui demande son pseudo,
    sinon on lui montre la page index avec scoreboard, etc."""
    user_id = session.get("user_id")
    if not user_id or user_id not in players:
        return redirect(url_for("login"))
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Page de login/inscription pour joueur."""
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            # Création d'un user_id et stockage en session.
            user_id = generate_user_id()
            players[user_id] = {"username": username, "team": None}
            session["user_id"] = user_id
            return redirect(url_for("index"))
    return render_template("login.html")

@app.route("/logout")
def logout():
    """Déconnexion joueur."""
    user_id = session.get("user_id")
    if user_id and user_id in players:
        del players[user_id]
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    """Page d'administration (score, countdown, etc.)
    Protégée par un mot de passe (123456)."""
    is_admin = session.get("is_admin", False)
    if not is_admin:
        # Vérifier mot de passe.
        if request.method == "POST":
            pwd = request.form.get("password")
            if pwd == ADMIN_PASSWORD:
                session["is_admin"] = True
                return redirect(url_for("admin"))
            else:
                return render_template("admin.html", error="Mot de passe incorrect.")
        else:
            return render_template("admin.html", error=None)
    else:
        # On est déjà admin, on affiche l'interface.
        return render_template("admin.html", error=None)

@app.route("/admin_logout")
def admin_logout():
    """Quitter le mode admin."""
    session["is_admin"] = False
    return redirect(url_for("index"))

@app.route("/auto_teams", methods=["POST"])
def route_auto_teams():
    """Bouton "Constituer équipes" depuis la page admin."""
    auto_assign_teams()
    # Remet les scores à zéro.
    scores[1] = 0
    scores[2] = 0
    socketio.emit("teams_updated", {"players": players, "scores": scores})
    return redirect(url_for("admin"))

@app.route("/update_score", methods=["POST"])
def update_score():
    """Mise à jour manuelle d'un score via l'admin (team=1 ou 2, points=valeur)."""
    team = int(request.form.get("team", 0))
    points = int(request.form.get("points", 0))
    if team in scores:
        scores[team] += points
        socketio.emit("teams_updated", {"players": players, "scores": scores})
    return redirect(url_for("admin"))

@app.route("/start_countdown", methods=["POST"])
def start_countdown():
    """Démarre un compte à rebours (seconds dans form)."""
    global countdown_seconds, countdown_running
    seconds = int(request.form.get("seconds", 30))
    countdown_seconds = seconds
    countdown_running = True
    print(f"Countdown started on server for {seconds} seconds") # DEBUG PRINT
    socketio.emit("countdown_started", {"seconds": countdown_seconds})
    return redirect(url_for("admin"))

@app.route("/stop_countdown", methods=["POST"])
def stop_countdown():
    """Arrête le countdown."""
    global countdown_running
    countdown_running = False
    print("Countdown stopped on server") # DEBUG PRINT
    socketio.emit("countdown_stopped")
    return redirect(url_for("admin"))

@app.route("/spin_roulette", methods=["POST"])
def spin_roulette():
    """Lance la roulette pour choisir un thème.
    Simplifié : on a une liste de thèmes fixée ici en dur."""
    global current_theme
    theme_list = ["Culture Générale", "Cinéma", "Sport", "Musique", "Histoire", "Géographie", "Sciences", "Informatique"]
    chosen = random.choice(theme_list)
    current_theme = chosen
    socketio.emit("roulette_result", {"theme": chosen})
    return redirect(url_for("admin"))

@app.route("/roll_dice", methods=["POST"])
def roll_dice():
    """Lance un dé (1 à 6) et envoie le résultat à tous les joueurs."""
    result = random.randint(1, 6)
    socketio.emit("dice_result", {"value": result})
    return redirect(url_for("admin"))

@app.route("/next_question", methods=["POST"])
def next_question():
    """
    Passe à la question suivante du quiz et l'envoie à tous les joueurs.
    """
    next_question_data = set_next_quiz_question()
    if next_question_data:
        socketio.emit("quiz_question", {"question": next_question_data["question"]})
        session['current_quiz_answer'] = next_question_data["answer"] # Stocker la réponse pour affichage admin ultérieur
    else:
        socketio.emit("quiz_question", {"question": "Fin des questions."})
        session['current_quiz_answer'] = None # Plus de réponse à afficher

    return redirect(url_for("admin"))

@app.route("/reveal_answer", methods=["POST"])
def reveal_answer():
    """
    Récupère la réponse de la session et l'envoie à tous les joueurs.
    """
    answer = session.get('current_quiz_answer')
    if answer:
        socketio.emit("quiz_answer", {"answer": answer})
    return redirect(url_for("admin"))

@app.route("/reset_game", methods=["POST"])
def reset_game():
    """Resets the game state (scores, players, quiz question)."""
    global scores, players, current_quiz_question_index, countdown_running, countdown_seconds, current_theme
    scores = {1: 0, 2: 0}
    players = {}
    current_quiz_question_index = -1
    countdown_running = False
    countdown_seconds = 0
    current_theme = "Aucun thème sélectionné"
    session.pop('current_quiz_answer', None) # Clear stored quiz answer
    socketio.emit("teams_updated", {"players": players, "scores": scores}) # Update scores and players for clients
    socketio.emit("roulette_result", {"theme": current_theme}) # Reset theme display
    socketio.emit("quiz_question", {"question": ""}) # Clear quiz question display
    socketio.emit("countdown_stopped") # Stop countdown if running
    print("Game state reset by admin") # Optional log
    return redirect(url_for("admin")) # Redirect back to admin page


# ===============================
#   Événements SocketIO
# ===============================
@socketio.on("connect")
def on_connect():
    """À la connexion d'un client, on envoie l'état actuel des équipes, scores, thème, etc."""
    emit("teams_updated", {"players": players, "scores": scores})
    emit("roulette_result", {"theme": current_theme})
    if countdown_running:
        emit("countdown_started", {"seconds": countdown_seconds})
    # Envoie la question de quiz actuelle (si il y en a une)
    current_question_data = get_current_quiz_question()
    if current_question_data:
        emit("quiz_question", {"question": current_question_data["question"]})


# ===============================
#   Tâche de fond pour le countdown
# ===============================
def countdown_task():
    global countdown_seconds, countdown_running
    while True:
        socketio.sleep(1)  # Attendre 1 seconde
        if countdown_running and countdown_seconds > 0:
            countdown_seconds -= 1
            if countdown_seconds <= 0:
                countdown_running = False
                print("Countdown finished on server, emitting countdown_finished") # DEBUG PRINT
                socketio.emit("countdown_finished")
            else:
                print(f"Countdown tick on server, emitting countdown_tick with {countdown_seconds} seconds") # DEBUG PRINT
                socketio.emit("countdown_tick", {"seconds": countdown_seconds})


# ===============================
#   Chargement des questions depuis JSON au démarrage de l'app
# ===============================
def load_quiz_questions():
    global quiz_questions
    try:
        with open("questions.json", "r", encoding='utf-8') as f: # Specify encoding
            quiz_questions = json.load(f)
        print(f"Questions chargées depuis questions.json: {len(quiz_questions)} questions") # Optional: Print to confirm loading
    except FileNotFoundError:
        print("questions.json non trouvé. Quiz démarrera sans questions.")
    except json.JSONDecodeError:
        print("Erreur de décodage JSON dans questions.json. Vérifiez le format du fichier.")

# Lancement de la tâche de fond
socketio.start_background_task(countdown_task)

# Charger les questions au démarrage de l'app
load_quiz_questions()

# ===============================
#   Lancement de l'app
# ===============================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)