@echo off
git init
git add .
git commit -m 'Changes'
git push -u https://github.com/AlexWanted/PupsikBot
git push heroku master
heroku ps:scale bot=1
