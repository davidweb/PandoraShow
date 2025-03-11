$(function () {
  // Connexion à Socket.IO
  var socket = io();

  // Initialiser les animations
  initAnimations();

  socket.on("connect", function () {
    console.log("Connecté à Pandora Show via Socket.IO");
    showToast("Connecté au serveur de jeu !");
  });

  // Mise à jour des scores et de la liste des joueurs
  socket.on("teams_updated", function (data) {
    console.log("teams_updated", data);
    animateScoreChange($("#scoreTeam1"), data.scores[1]);
    animateScoreChange($("#scoreTeam2"), data.scores[2]);
    updatePlayersList(data.players);
  });

  // Roulette : mise à jour du thème
  socket.on("roulette_result", function (data) {
    animateThemeChange(data.theme);
  });

  // Gestion du compte à rebours
  socket.on("countdown_started", function (data) {
    console.log("Countdown démarré pour " + data.seconds + "s");
    $("#countdownFinished").hide();
    animateCountdownStart(data.seconds);
  });

  socket.on("countdown_tick", function (data) {
    updateCountdown(data.seconds);
  });

  socket.on("countdown_stopped", function () {
    resetCountdown();
    showToast("Compte à rebours arrêté !");
  });

  socket.on("countdown_finished", function () {
    finishCountdown();
    playSound("countdown-end");
  });

  // Gestion du quiz
  socket.on("quiz_question", function (data) {
    animateNewQuestion(data.question);
  });

  socket.on("quiz_answer", function (data) {
    revealAnswer(data.answer);
    playSound("answer-reveal");
  });

  // Gestion du dé
  socket.on("dice_result", function (data) {
    animateDiceRoll(data.value);
    playSound("dice-roll");
  });

  // Fonctions d'animation et utilitaires
  function initAnimations() {
    preloadSounds();
    $(".game-card").addClass("animate__animated animate__fadeIn");
  }

  function animateScoreChange(element, newScore) {
    const currentScore = parseInt(element.text());
    if (newScore > currentScore) {
      element.addClass("animate__animated animate__heartBeat");
      element.css("color", "#4caf50"); // Vert pour augmentation
      setTimeout(function () {
        element.removeClass("animate__animated animate__heartBeat");
        element.css("color", "white");
      }, 1000);
      playSound("score-up");
    } else if (newScore < currentScore) {
      element.addClass("animate__animated animate__shakeX");
      element.css("color", "#f44336"); // Rouge pour diminution
      setTimeout(function () {
        element.removeClass("animate__animated animate__shakeX");
        element.css("color", "white");
      }, 1000);
      playSound("score-down");
    }
    $({ score: currentScore }).animate(
      { score: newScore },
      {
        duration: 1000,
        easing: "swing",
        step: function () {
          element.text(Math.floor(this.score));
        },
        complete: function () {
          element.text(newScore);
        },
      }
    );
  }

  function updatePlayersList(players) {
    var playersList = $("#playersList");
    playersList.empty();
    var orderedPlayers = [];
    $.each(players, function (pid, info) {
      orderedPlayers.push({
        id: pid,
        username: info.username,
        team: info.team || 0,
      });
    });
    orderedPlayers.sort(function (a, b) {
      if (a.team === b.team) {
        return a.username.localeCompare(b.username);
      }
      return (a.team || 999) - (b.team || 999);
    });
    $.each(orderedPlayers, function (index, player) {
      let teamClass = player.team ? `team-${player.team}` : "team-none";
      let teamLabel = player.team ? `Équipe ${player.team}` : "Non assigné";
      let initials = player.username.charAt(0).toUpperCase();
      let playerCard = $("<div>").addClass(
        "player-card animate__animated animate__fadeIn"
      );
      playerCard.html(`
          <div class="player-avatar">${initials}</div>
          <div class="player-name">${player.username}</div>
          <span class="team-badge ${teamClass}">${teamLabel}</span>
        `);
      playersList.append(playerCard);
    });
  }

  function animateThemeChange(theme) {
    const themeElement = $("#currentTheme");
    themeElement.fadeOut(400, function () {
      $(this).text(theme).fadeIn(400);
      $(this).addClass("animate__animated animate__pulse");
      setTimeout(function () {
        themeElement.removeClass("animate__animated animate__pulse");
      }, 1000);
    });
    playSound("theme-change");
  }

  function animateCountdownStart(seconds) {
    $("#countdownDisplay").text(seconds);
    $(".countdown-circle circle").css({
      "stroke-dasharray": "283",
      "stroke-dashoffset": "0",
    });
    $(".countdown-circle").addClass("animate__animated animate__bounceIn");
    setTimeout(function () {
      $(".countdown-circle").removeClass("animate__animated animate__bounceIn");
    }, 1000);
    playSound("countdown-start");
  }

  function updateCountdown(seconds) {
    $("#countdownDisplay").text(seconds);
    const circumference = 283;
    const percentage = seconds / 30;
    const offset = circumference - percentage * circumference;
    $(".countdown-circle circle").css("stroke-dashoffset", offset);
    if (seconds <= 5) {
      $(".countdown-circle circle").css("stroke", "#f44336");
      $("#countdownDisplay").addClass("animate__animated animate__heartBeat");
      playSound("tick");
    } else if (seconds <= 10) {
      $(".countdown-circle circle").css("stroke", "#ff9800");
      $("#countdownDisplay").removeClass(
        "animate__animated animate__heartBeat"
      );
    }
  }

  function resetCountdown() {
    $("#countdownDisplay").text("--");
    $("#countdownFinished").hide();
    $(".countdown-circle circle").css({
      stroke: "#ff9800",
      "stroke-dashoffset": "0",
    });
    $("#countdownDisplay").removeClass("animate__animated animate__heartBeat");
  }

  function finishCountdown() {
    $("#countdownDisplay").text("0");
    $("#countdownFinished").show();
    $(".countdown-circle circle").css({
      stroke: "#f44336",
      "stroke-dashoffset": "283",
    });
    $("#countdownFinished").addClass("animate__animated animate__flash");
    setTimeout(function () {
      $("#countdownFinished").removeClass("animate__animated animate__flash");
    }, 2000);
  }

  function animateNewQuestion(question) {
    const questionElement = $("#quizQuestionDisplay");
    $("#quizAnswerContainer").hide();
    questionElement.addClass("animate__animated animate__fadeOut");
    setTimeout(function () {
      questionElement.text(question);
      questionElement.removeClass("animate__animated animate__fadeOut");
      questionElement.addClass("animate__animated animate__fadeIn");
      setTimeout(function () {
        questionElement.removeClass("animate__animated animate__fadeIn");
      }, 500);
    }, 500);
    playSound("new-question");
  }

  function revealAnswer(answer) {
    $("#quizAnswerDisplay").text(answer);
    $("#quizAnswerContainer").hide().fadeIn(800);
    $("#quizAnswerDisplay").addClass("animate__animated animate__bounceIn");
    setTimeout(function () {
      $("#quizAnswerDisplay").removeClass(
        "animate__animated animate__bounceIn"
      );
    }, 1000);
  }

  function animateDiceRoll(value) {
    const diceElement = $("#diceValue");
    diceElement.addClass("roll-animation");
    let rollCount = 0;
    const maxRolls = 10;
    const rollInterval = setInterval(function () {
      if (rollCount < maxRolls) {
        diceElement.text(Math.floor(Math.random() * 6) + 1);
        rollCount++;
      } else {
        clearInterval(rollInterval);
        diceElement.removeClass("roll-animation");
        diceElement.addClass("animate__animated animate__bounceIn");
        diceElement.text(value);
        setTimeout(function () {
          diceElement.removeClass("animate__animated animate__bounceIn");
        }, 1000);
      }
    }, 100);
  }

  function preloadSounds() {
    const sounds = [
      "countdown-start",
      "countdown-end",
      "tick",
      "score-up",
      "score-down",
      "theme-change",
      "new-question",
      "answer-reveal",
      "dice-roll",
    ];
    // Implémentation future pour précharger les fichiers audio
  }

  function playSound(soundId) {
    console.log("Playing sound: " + soundId);
    // Exemple : $("#sound-" + soundId)[0].play();
  }

  function showToast(message) {
    if ($("#toast-container").length === 0) {
      $("body").append(`
          <div id="toast-container" style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;"></div>
        `);
    }
    const toastId = "toast-" + Date.now();
    const toast = $(`
        <div id="${toastId}" class="animate__animated animate__fadeInUp" 
             style="background: #333; color: white; padding: 10px 20px; border-radius: 5px; 
                    margin-top: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);">
          ${message}
        </div>
      `);
    $("#toast-container").append(toast);
    setTimeout(function () {
      toast.removeClass("animate__fadeInUp").addClass("animate__fadeOutDown");
      setTimeout(function () {
        toast.remove();
      }, 1000);
    }, 3000);
  }
});
