#! /bin/bash 
docker rm pidibot_dev
docker rmi pidibot
docker build . -t pidibot
docker compose up
