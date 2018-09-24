# digital-assistant
Bachelor-Thesis: Digital Assistant for building an database using a Flask-Application

## Beschreibung des Digital Assistant

## Technische Beschreibung des Digital Assistant

## Voraussetzungen
1. Docker https://www.docker.com/get-started
2. ngrok https://ngrok.com/download
3. Recast.ai Account https://recast.ai/signup

## Installationsanleitung (für MacOS)
1. MySQL Docker image ziehen und starten
```bash
sudo docker pull mysql
```
```bash
sudo docker run --name digital_assistant_mysql -e MYSQL_ROOT_PASSWORD=admin -e MYSQL_DATABASE=demo -p 3306:3306 -d mysql
```
2. Digital-Assistent Docker image ziehen, mit MySQL Dockercontainer verlinken und starten
```bash
sudo docker build -t digital-assistant:latest github.com/oemerkafaoglu/digital-assistant
```
```bash
sudo docker run --name digital-assistant --link digital_assistant_mysql:mysql -d -p 5000:5000 digital-assistant
```
3. Mit ngrok lokale Adresse an eine öffentliche URL freigeben
```bash
./ngrok http 5000
```
4. In Recast.ai den Chatbot "digital-assistant-1" forken

https://recast.ai/oemerkafaoglu/digital-assistant-1

5. Die ngrok HTTPS URL dem "digital-assistant-1" mitteilen

https://recast.ai/kafaoglu_oemer/digital-assistant/settings/options

Unter "Bot webhook base URL"

## Nutzung

