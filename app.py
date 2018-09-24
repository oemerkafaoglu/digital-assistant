from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flaskext.mysql import MySQL
import json

app = Flask(__name__)
mysql = MySQL()

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'admin'
app.config['MYSQL_DATABASE_DB'] = 'demo'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route('/')
def index():
    tables = get_data()
    if not tables:
        connection = "Es existieren noch keine Objekte"
        return render_template("index.html", connection=connection, chatbot=chatbot_channelid_token())
    else:
        return render_template("index.html", tables=tables, chatbot=chatbot_channelid_token())

@app.route("/navigate/<entity>")
def navigate(entity):
    tables = get_data()
    masterdata = check_if_mdm(entity)
    attributes = get_attributes_of(entity, noid=True, noFK=True)
    content = get_content_of(entity, attributes)
    foreignkeys = get_foreignkeys_of(entity)
    foreign_tables = []
    foreign_attributes_table = []
    foreign_entity_table = []
    inner_join = ""
    foreign_att_syntax = ""

    foreign_tables1 = []


    if foreignkeys:
        for no, foreignkey in enumerate(foreignkeys):
            foreign_entity = get_entity_of(foreignkey)
            foreign_attributes = get_attributes_of(foreign_entity, noid=True, noFK=True)
            foreign_content = get_content_of(foreign_entity, foreign_attributes)

            foreign_attributes1 = get_attributes_of(foreign_entity, noid=False, noFK=True)
            foreign_content1 = get_content_of(foreign_entity, foreign_attributes1)
            foreign_strucutred1 = structure_tables(foreign_attributes1, foreign_content1)
            foreign_tables1.append({foreign_entity: foreign_strucutred1})

            foreign_structered = structure_tables(foreign_attributes, foreign_content)
            foreign_entity_table.append(foreign_entity)
            foreign_attributes_table.append(foreign_attributes)
            foreign_tables.append({foreign_entity: foreign_structered})
            inner_join += "INNER JOIN {} ON {}.id{}={}.id{} ".format(foreign_entity, entity, foreign_entity, foreign_entity, foreign_entity)
            if no == 0:
                foreign_att_syntax = create_syntax(foreign_attributes)
            else:
                foreign_att_syntax = "{}, {}".format(foreign_att_syntax, create_syntax(foreign_attributes))

        conn = mysql.connect()
        cursor = conn.cursor()
        query = "SELECT {}, {} FROM {} {}".format(create_syntax(attributes), foreign_att_syntax, entity, inner_join)
        cursor.execute(query)
        planung = cursor.fetchall()
        conn.close()
        return render_template("content.html", entity=entity, attributes=attributes, tables=tables,
                               foreign_tables=foreign_tables1, foreign_attributes_table=foreign_attributes_table,
                               foreign_entity_table=foreign_entity_table, planung=planung,
                               chatbot=chatbot_channelid_token())

    return render_template("content.html", entity=entity, attributes=attributes, tables=tables, content=content,
                           chatbot=chatbot_channelid_token())


@app.route("/add_data/<entity>", methods=['POST'])
def add_data(entity):
    attributes = get_attributes_of(entity, noid=True, noFK=False)
    syntax = create_syntax(attributes)
    values = ()
    for attribute in attributes:
        values = values + (request.form[attribute],)
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "INSERT INTO {} ({}) VALUES {}".format(entity, syntax, values)
    cursor.execute(query)
    conn.commit()
    conn.close()
    return redirect(url_for('navigate', entity=entity))

@app.route("/init_chatbot", methods=['POST'])
def init_chatbot():
    channelid = request.form["channelId"]
    token = request.form["token"]
    session["chatbot"] = {"channelid": channelid, "token": token}
    return redirect(url_for("index"))

@app.route('/digital-assistant/greetings', methods=['POST'])
def greetings():
    return jsonify(
        status=200,
        replies=[{
            'type': 'text',
            'content': 'Roger that',
        }],
        conversation={
            'memory': {'key': 'value'}
        }
    )

@app.route('/digital-assistant/entity', methods=['POST'])
def entity():
    return jsonify(
        status=200,
        replies=[{
            'type': 'text',
            'content': 'Wie lautet die Entität?',
        }]
    )

@app.route('/digital-assistant/attribute', methods=['POST'])
def attribute():
    data = json.loads(request.get_data())
    entity = data["conversation"]["memory"]["entity"]["raw"]
    if entity == "Planung" or entity == "planung":
        try:
            attribute = data["conversation"]["memory"]["attribute"]["raw"]
        except:
            return jsonify(
                status=200,
                replies=[{
                    'type': 'text',
                    'content': 'Wie lautet das erste Attribut?',
                }]
            )
        return jsonify(
            status=200,
            replies=[{
                'type': 'text',
                'content': 'Für welche Monate?',
            }]
        )
    else:
        try:
            attribute = data["conversation"]["memory"]["attribute"]["raw"]
        except:
            return jsonify(
                status=200,
                replies=[{
                    'type': 'text',
                    'content': 'Wie lautet das erste Attribut?',
                }]
            )
        return jsonify(
            status=200,
            replies=[{
                'type': 'text',
                'content': 'Wie lautet das zweite Attribut?',
            }]
        )

@app.route('/digital-assistant/mdm', methods=['POST'])
def mdm():
    return jsonify(
        status=200,
        replies=[{
            'type': 'text',
            'content': 'Handelt es sich hierbei um ein Stammdatum?',
        }]
    )

@app.route('/digital-assistant/new_object', methods=['POST'])
def new_objekt():
    data = json.loads(request.get_data())
    entity = data["conversation"]["memory"]["entity"]["raw"]
    attribute = data["conversation"]["memory"]["attribute"]["raw"]
    attribute2 = data["conversation"]["memory"]["attribute2"]["raw"]
    mdm = data["conversation"]["memory"]["mdm"]["raw"]
    if mdm == "Ja" or "ja":
        mdm = "Stammdatum"
    else:
        mdm = "Kein Stammdatum"
    objekt = {"entity": entity, "attribute": attribute, "attribute2": attribute2, "mdm": mdm}
    new_entry(objekt)
    return jsonify(
        status=200,
        replies=[{
            'type': 'text',
            'content': 'Du hast ein neues Objekt mit der Bezeichnung {} erstellt. Das Objekt hat die Attribute '
                       '{} und {}'.format(entity, attribute, attribute2),
        }]
    )

@app.route('/digital-assistant/relation_object', methods=['POST'])
def relation_object():
    tables = get_data()
    data = json.loads(request.get_data())
    objekte = []
    try:
        objekt1 = data["conversation"]["memory"]["objekt1"]["raw"]
        title = "Wähle das zweite Objekt aus"
        for table in tables:
            if objekt1 == table["entity"]:
                pass
            else:
                objekte.append({"title": table["entity"], "value": table["entity"]})
    except:
        title = "Wähle das erste Objekt aus"
        for table in tables:
            objekte.append({"title": table["entity"], "value": table["entity"]})
    return jsonify(
        status=200,
        replies=[{
            'type': 'quickReplies',
            'content': {
              "title": title,
              "buttons": objekte
            }
        }]
    )

@app.route('/digital-assistant/relation', methods=['POST'])
def relation():
    data = json.loads(request.get_data())
    objekt1 = data["conversation"]["memory"]["objekt1"]["raw"]
    objekt2 = data["conversation"]["memory"]["objekt2"]["raw"]
    buttons = [{"title": "Beziehung setzen", "type": "postback", "value": "1 zu n"},
                 {"title": "Beziehung setzen", "type": "postback", "value": "n zu 1"},
                 {"title": "Beziehung setzen", "type": "postback", "value": "1 zu 1"},
                 {"title": "Beziehung setzen", "type": "postback", "value": "n zu n"}]
    elements = [{"title": "1 zu n", "imageUrl": "", "subtitle": "Ein {} zu n {}".format(objekt1, objekt2),
                 "buttons": [buttons[0]]},
                {"title": "n zu 1", "imageUrl": "", "subtitle": "n {} zu ein {}".format(objekt1, objekt2),
                 "buttons": [buttons[1]]},
                {"title": "1 zu 1", "imageUrl": "", "subtitle": "Ein {} zu ein {}".format(objekt1, objekt2),
                 "buttons": [buttons[2]]},
                {"title": "n zu n", "imageUrl": "", "subtitle": "n {} zu n {}".format(objekt1, objekt2),
                 "buttons": [buttons[3]]}]
    return jsonify(
        status=200,
        replies=[{
            'type': 'list',
            'content': {
                "elements": elements
            }
        }]
    )

@app.route("/digital-assistant/set_relation", methods=['POST'])
def set_relation():
    data = json.loads(request.get_data())
    objekt1 = data["conversation"]["memory"]["objekt1"]["raw"]
    objekt2 = data["conversation"]["memory"]["objekt2"]["raw"]
    relation = data["conversation"]["memory"]["relation"]["raw"]
    if relation == "1 zu n":
        set_relation(objekt2, objekt1)

    return jsonify(
        status=200,
        replies=[{
            'type': 'text',
            'content': '{} wurde mit {} in eine {} Relation gesetzt'.format(objekt1, objekt2, relation),
        }]
    )




@app.route('/errors', methods=['POST'])
def errors():
    print(json.loads(request.get_data()))
    return jsonify(status=200)

def new_entry(objekt):
    conn = mysql.connect()
    cursor = conn.cursor()
    if objekt["entity"] == "Planung" or objekt["entity"] == "planung":
        query = "CREATE TABLE {} (id{} INT NOT NULL AUTO_INCREMENT, {} varchar(40), Januar integer, Februar integer, " \
                "März integer, April integer, Mai integer, Juni integer, Juli integer, August integer, " \
                "September integer, Oktober integer,November integer, Dezember integer, " \
                "PRIMARY KEY (id{}))".format(objekt["entity"], objekt["entity"], objekt["attribute"], objekt["entity"])
    else:
        query = "CREATE TABLE {} (id{} INT NOT NULL AUTO_INCREMENT, {} varchar(40), {} varchar(100), {} varchar(10), " \
                "PRIMARY KEY (id{}))".format(objekt["entity"], objekt["entity"], objekt["attribute"],
                                             objekt["attribute2"], objekt["mdm"], objekt["entity"])
    cursor.execute(query)
    conn.commit()
    conn.close()

def get_data():
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SELECT table_name FROM information_schema.tables where table_schema='demo';"
    cursor.execute(query)
    tables = cursor.fetchall()
    data = []
    entry = {}
    for table in tables:
        entry.update({"entity": table[0]})
        query = "SHOW COLUMNS FROM {};".format(table[0])
        cursor.execute(query)
        columns = cursor.fetchall()
        for no, column in enumerate(columns):
            if no == 0:
                entry.update({"attribute": column[0]})
            else:
                entry.update({"attribute{}".format(no): column[0]})
        d = entry.copy()
        entry = {}
        data.append(d)
    return data

def get_attributes_of(entity, noid, noFK):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SHOW COLUMNS FROM {};".format(entity)
    cursor.execute(query)
    columns = cursor.fetchall()
    attributes = []
    foreignkeys = get_foreignkeys_of(entity)
    for column in columns:
        if column[0] == "Stammdatum":
            pass
        elif noid and column[0] == "id{}".format(entity):
            pass
        elif noFK and column[0] in foreignkeys:
            pass
        else:
            attributes.append(column[0])
    conn.close()
    return attributes

def get_foreignkeys_of(entity):
    tables = get_data()
    entities = get_entites()
    entities.remove(entity)
    foreignkeys = []
    for table in tables:
        if table["entity"] == entity:
            for attribute in table:
                for item in entities:
                    if table[attribute] == "id{}".format(item):
                        foreignkeys.append(table[attribute])
    return foreignkeys

def get_entites():
    tables = get_data()
    entities = []
    for table in tables:
        entities.append(table["entity"])
    return entities

def get_content_of(entity, attributes):
    conn = mysql.connect()
    cursor = conn.cursor()
    syntax = create_syntax(attributes)
    query = "SELECT {} COLUMNS FROM {};".format(syntax, entity)
    cursor.execute(query)
    data = cursor.fetchall()
    content = []
    for entry in data:
        content.append(entry)
    conn.close()
    return content

def get_entity_of(foreignkey):
    entities = get_entites()
    for entity in entities:
        if foreignkey == "id{}".format(entity):
            return (entity)

def create_syntax(attributes):
    syntax = ""
    for key, attribute in enumerate(attributes):
        if key == 0:
            syntax += attribute
        else:
            syntax = "{}, {}".format(syntax, attribute)
    return syntax

def check_if_mdm(entity):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "SHOW COLUMNS FROM {} LIKE 'Stammdatum';".format(entity)
    cursor.execute(query)
    stammdatum = cursor.fetchall()
    conn.close()
    if not stammdatum:
        return False
    else:
        return True

def set_relation(objekt1, objekt2):
    conn = mysql.connect()
    cursor = conn.cursor()
    query = "ALTER TABLE {} ADD COLUMN id{} INTEGER".format(objekt1, objekt2)
    cursor.execute(query)
    conn.commit()
    query = "ALTER TABLE {} ADD CONSTRAINT id{} FOREIGN KEY (id{}) " \
            "REFERENCES {} (id{})".format(objekt1, objekt2, objekt2, objekt2, objekt2)
    cursor.execute(query)
    conn.commit()
    conn.close()

def structure_tables(attributes, content):
    structured_table = []
    structured_dict = {}
    for entry in content:
        for no, attribute in enumerate(attributes):
            structured_dict[attribute] = entry[no]
        d = structured_dict.copy()
        structured_dict = {}
        structured_table.append(d)
    return structured_table

def chatbot_channelid_token():
    if "chatbot" in session:
        return session["chatbot"]


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')