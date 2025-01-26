from app import app
from flask import render_template, request, session, redirect
from db import db

import users

@app.route("/")
def index():
    result  = db.session.execute("SELECT name, id FROM areas ORDER BY id ASC")
    areas = result.fetchall()
    result = db.session.execute("SELECT id, topic, area_id FROM topics ORDER BY id ASC")
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


@app.route("/logout")
def logout():
    users.logout()
    return redirect("/")

@app.route("/new")
def new():
    result = db.session.execute("SELECT name FROM areas")
    areas = result.fetchall()
    return render_template("new.html", areas=areas)

@app.route("/create", methods=["POST"])
def create():
    topic = request.form["topic"]
    message = request.form["message"]
    name = request.form["area"]
    sql = "SELECT id FROM areas WHERE name=:name"
    result = db.session.execute(sql, {"name":name})
    area_id = result.fetchone()[0]
    starter_id = users.user_id()
    sql = "INSERT INTO topics(topic, starter_id, area_id, created_at) VALUES (:topic, :starter_id, :area_id, NOW()) RETURNING id"
    result = db.session.execute(sql, {"topic":topic, "area":name, "starter_id":starter_id, "area_id":area_id})
    topic_id = result.fetchone()[0]
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
