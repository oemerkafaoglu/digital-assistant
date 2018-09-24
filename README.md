# digital-assistant
Bachelor-Thesis: Digital Assistant for building an database using a Flask-Application

## Beschreibung des Digital Assistant

Der digitale Assistent nimmt Befehle des Anwenders entgegen um daraus eine Datenbank zu bauen. In einem Dialogflow werden die Anforderungen an die Datenbank abgefragt und basierend auf den Antworten werden im Hintergrund Tabellen/Objekte in einer MySQL Datenbank erstellt. Die Entitäten und Attribute werden in einer Flask-Applikation angezeigt, in der der Anwender seine Einträge vornehmen kann.

Hierbei handelt es sich um ein erstes Konzept, welche für meine Bachelor-Thesis angefertigt wurde.

## Technische Beschreibung des Digital Assistant
Genutzt wurden:
1. Python 3.6 mit Flask-Framework
2. MySQL Datenbank
3. Docker
4. Recast.ai als Chatbot

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

6. Web Channel erstellen

https://recast.ai/oemerkafaoglu/digital-assistant/connect

Bei Recast.ai, den Digitalen-Assitenten wählen, den man soeben geforked hat. Dann auf dein Reiter 'Connect' und dann "Webchat" wählen. Hier die gewünschten Einstellungen vornehmen und den Webchannel erstellen. Die
```bash
ChannelId und Token
```
aus dem Snippet kopieren/merken/aufschreiben.

7. Flask-Anwendung über die ngrok-URL aufrufen (Bei localhost:5000 reagiert der Chatbot nicht auf Eingaben)
8. Auf der Startseite ChannelID und Token vom Webchannel eintragen.
9. Der Chatbot erscheint, nachdem "Submit" betätigt wurde

## Nutzung

### Objekte/Tabellen erstellen
Ich: Hallo<br />
Chatbot: Hallo<br />
Ich: Bau mir eine Datenbank<br />
Chatbot: Wie lautet die Entität?<br />
Ich: Projekte<br />
Chatbot: Wie lautet das erste Attribut?<br />
Ich: Projektname<br />
Chatbot: Wie lautet das zweite Attribut?<br />
Ich: Projektbeschreibung<br />
Chatbot: Handelt es sich hierbei um ein Stammdatum?<br />
Ich: Ja<br />
Chatbot: Du hast ein neues Objekt mit der Bezeichnung Projekte erstellt. Das Objekt hat die Attribute Projektname und Projektbeschreibung<br />

Ich: Neuer Eintrag<br />
Chatbot: Wie lautet die Entität?<br />
Ich: Ressource<br />
Chatbot: Wie lautet das erste Attribut?<br />
Ich: Vorname<br />
Chatbot: Wie lautet das zweite Attribut?<br />
Ich: Nachname<br />
Chatbot: Handelt es sich hierbei um ein Stammdatum?<br />
Ich: Ja<br />
Chatbot: Du hast ein neues Objekt mit der Bezeichnung Ressource erstellt. Das Objekt hat die Attribute Vorname und Nachname<br />

Ich: Neuer Eintrag<br />
Chatbot: Wie lautet die Entität?<br />
Ich: Planung<br />
Chatbot: Wie lautet das erste Attribut?<br />
Ich: Jahr<br />
Chatbot: Wie lautet das zweite Attribut?<br />
Ich: alle Monate<br />
Chatbot: Handelt es sich hierbei um ein Stammdatum?<br />
Ich: Nein<br />
Chatbot: Du hast ein neues Objekt mit der Bezeichnung Planung erstellt. Das Objekt hat die Attribute Jahr und alle Monate<br />

### Objekte in Relation setzen
Ich: Relation setzen<br />
Chatbot: Wähle das erste Objekt aus<br />
Ich: Projekte<br />
Chatbot: Wähle das zweite Objekt aus<br />
Ich: Planung<br />
Chatbot: 1 zu n oder 1 zu 1, oder n zu 1, oder m zu n Beziehung setzen?<br />
Ich: 1 zu n
Chatbot: Projekte wurde mit Planung in eine 1 zu n Relation gesetzt

### Hinweise zur Nutzung
1. Um neue Entitäten oder Attribute zu setzen auf Recast.ai gehen und in den Intents "Entität" und "Attributes" die Bezeichnungen hinzufügen. Die eingefügten Intents müssen auch als "Entität" oder "Attribute" deklariert werden.
2. Aktuell sind die Attribute auf 2 Stück beschränkt
3. Das Planungsobjekt wird im Code gesondert behandelt (z.B. wird aus dem Intent "alle Monate", zwölf Monatsattribute generiert)
4. Aktuelle Entitäten: Professor, Student, Baureihen, Ressource, Projekte, Planung
5. Aktuelle Attribute: Vorname, Nachname, Matrikelnummer, Projektname, Projektbeschreibung, alle Monate

