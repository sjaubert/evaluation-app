@echo off
title Serveur d'Evaluation des Apprentis

echo.
echo ==========================================================
echo    Lancement de l'application d'evaluation d'apprentis
echo ==========================================================
echo.

REM La commande ci-dessous garantit que le script s'execute
REM depuis le dossier ou il est place, peu importe d'ou vous le lancez.
cd /d "%~dp0"

echo Le serveur va demarrer et votre navigateur va s'ouvrir automatiquement.
echo.
echo ATTENTION: Ne fermez pas cette fenetre noire.
echo Elle est necessaire au fonctionnement de l'application.
echo.
echo Pour arreter l'application, vous pouvez :
echo   1. Appuyer sur les touches CTRL + C dans cette fenetre.
echo   2. Fermer simplement cette fenetre.
echo.

REM Ouvre le navigateur sur la bonne adresse
start http://127.0.0.1:5000

REM Lance le serveur Python. Le script attendra ici jusqu'a ce que le serveur soit arrete.
python app.py
