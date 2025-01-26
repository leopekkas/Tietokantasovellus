from app import app
from flask import render_template, request, session, redirect
from db import db
from sqlalchemy import text

import users

@app.route("/")
def index():
    result  = db.session.execute(text("SELECT name, id FROM areas ORDER BY id ASC"))
    areas = result.fetchall()
    result = db.session.execute(text("SELECT id, topic, area_id FROM topics ORDER BY id ASC"))
    topics = result.fetchall()
    
    return render_template("index.html", areas=areas, topics=topics)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method== "GET":
        return render_template("login.html")
    if request.method=="POST":
        user= request.form["username"]
        pwd= request.form["password"]
        if users.login(user, pwd):
            return redirect("/")
        else:
            return render_template("error.html", message="Wrong username or password")

@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="GET":
        return render_template("register.html")
    if request.method== "POST":
        user = request.form["username"]
        pwd = request.form["password"]
        admin = request.form.get("admin")
        if users.register(user, pwd, admin):
            return redirect("/")
        else:
            return render_template("error.html", message="Error showing the registration page.")


@app.route("/new/<int:id>")
def new(id):
    result = db.session.execute(text("SELECT name FROM areas WHERE id=:id"))
    area = result.fetchone()[0]
    return render_template("new.html", if=if, area=area)

@app.route("/create", methods=["POST"])
def create():
    topic = request.form["topic"]
    if (topic == ""):
        return render_template("error.html", message="Please mark a topic for your new conversation")
    message = request.form["message"]
    area_id = request.form["id"]
    starter_id = users.user_id()
    sql = "INSERT INTO topics(topic, starter_id, area_id, created_at) VALUES (:topic, :starter_id, :area_id, NOW()) RETURNING id"
    result = db.session.execute(sql, {"topic":topic, "starter_id":starter_id, "area_id":area_id})
    topic_id = result.fetchone()[0]
    db.session.commit()
    if message != "":
        sql = "INSERT INTO messages(message, sender_id, topic_id, visibility, sent_at) VALUES (:message, :sender_id, :topic_id, :visibility, NOW())"
        db.session.execute(sql, {"message":message, "sender_id":starter_id, "topic_id":topic_id, "visibility":1})
    	db.session.commit()
    return redirect("/")

@app.route("/convo/<int:id>")
def convo(id):
    sql ="SELECT id, topic FROM topics WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic = result.fetchone()
    if topic == None:
	return render_template("error.html", message="No conversations in this topic")
    visibility=1
    sql = "SELECT messages.id, messages.message, users.username, users.id FROM messages, users WHERE messages.topic_id=:id AND visibility=:visibility AND messages.sender_id=users.id ORDER BY sent_at ASC"
    result = db.session.execute(sql, {"id":id, "visibility":visibility})
    messages = result.fetchall()
    return render_template("convo.html", topic=topic, messages=messages)

@app.route("/send", methods=["POST"])
def send():
    topic_id = request.form["id"]
    user_id = users.user_id()
    message = request.form["message"]

    if message != "":
        visibility=1
        sql = "INSERT INTO messages (message, sender_id, topic_id, visibility, sent_at) VALUES (:message, :sender_id, :topic_id, :visibility, NOW())"
        db.session.execute(sql, {"message":message, "sender_id":user_id, "topic_id":topic_id, "visibility":1 })
        db.session.commit()
    else:
        return render_template("error.html", message="Couldn't post the message")

    return redirect("/convo/"+str(topic_id))

@app.route("/delete", methods=["POST"])
def delete():
    id = request.form["id"]
    message_id = request.form["message_id"]
    sql = "UPDATE messages SET visibility=0 WHERE id=:id"
    result = db.session.execute(sql, {"id":message_id})
    db.session.commit()
    return redirect("/convo/"+str(id))

@app.route("/search")
def search():
    word = request.args["word"]
    visibility=1
    if word == "":
        return redirect("/")
    sql = "SELECT messages.message, users.username, topics.id FROM messages, users, topics WHERE visibility=:visibility AND messages.sender_id=users.id AND topics.id=messages.topic_id AND messages.message LIKE :word ORDER BY sent_at ASC"
    result = db.session.execute(sql, {"visibility":visibility, "word":"%"+word+"%"})
    messages = result.fetchall()
    if len(messages)==0:
        return render_template("error.html", message = "No messages found with this search")
    return render_template("search.html", messages=messages)

@app.route("/edit/<int:id>", methods=["POST"])
def update(id):
    sql = "SELECT message FROM messages WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    message = result.fetchone()[0]
    return render_template("update.html", id=id, message=message)>

@app.route("/update_message", methods=["POST"])
def update_message():
    message = request.form["message"]
    id = request.form["id"]
    sql = "UPDATE messages SET message=:message WHERE id=:id"
    db.session.execute(sql, {"message":message, "id":id})
    db.session.commit()
    sql = "SELECT topic_id FROM messages WHERE id=:id"
    result = db.session.execute(sql, {"id":id})
    topic_id = result.fetchone()[0]
    return redirect("/convo/"+str(topic_id))

@app.route("/create_area")
def create_area():
    return render_template("create_area.html")

@app.route("/create_private_area", methods=["POST"])
def create_private():
    name = request.form["theme"]
    user_id = users.user_id()
    sql = "INSERT INTO areas(name, user_id) VALUES (:name, :user_id) RETURNING id"
    result = db.session.execute(sql, {"name":name, "user_id":user_id})
    area_id = result.fetchone()[0]
    db.session.commit()
    sql = "INSERT INTO accessrights(area_id, user_id) VALUES (:area_id, :user_id)"
    db.session.execute(sql, {"area_id":area_id, "user_id":user_id}) 
    db.session.commit()
    return redirect("add_users/"+str(area_id))

@app.route("/add_users/<int:id>")
def add_users(id):
    return render_template("add_users.html", id=id)

@app.route("/add", methods=["POST"])
def add():
    username = request.form["username"]
    if username == "" or username == None:
        return render_template("error.html", message = "You have to write a username")
    sql = "SELECT username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    name = result.fetchone()
    if name == None or name == "":
        return render_template("error.html", message = "There is no user with that username")
    area_id = request.form["id"]
    sql = "SELECT id FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username":username})
    user_id = result.fetchone()[0]
    if users.check_rights(user_id, area_id):
        return render_template("add_users.html", id=area_id, message="That user already has accessrights")
    sql = "INSERT INTO accessrights(area_id, user_id) VALUES (:area_id, :user_id)"
    db.session.execute(sql, {"area_id":area_id ,"user_id":user_id})
    db.session.commit()
    return render_template("add_users.html", id=area_id)
