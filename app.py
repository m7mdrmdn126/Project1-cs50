from flask import Flask, render_template, session, request, redirect, url_for, jsonify
import json
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import os
import requests



app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


engine = create_engine(os.getenv("Database_URL", "postgres://ibrkvdfxbrmzoh:3d677fc83707eb93538fdd3c90ef3630bf2ab21703152a75effe69da8bbd9e96@ec2-184-73-209-230.compute-1.amazonaws.com:5432/db49hf6n6t475m"))
db = scoped_session(sessionmaker(bind = engine))


@app.route("/", methods = ["POST","GET"])
def index():
    if session.get('user') is not None:
        return redirect(url_for('books'))

    return render_template("index.html")




@app.route("/login", methods = ["POST","GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = db.execute("select * from login")
        for user in users :
            if user.username == username and user.password == password:
                session['user'] = username
                return redirect(url_for("books"))

        return "username or password invalid"
    return render_template("login.html")



@app.route("/sign_up", methods = ["POST", "GET"])
def sign_up():
    if request.method == "POST":
        usernames = db.execute("select * from login").fetchall()
        username = request.form.get("username")
        password = request.form.get("password")
        for user in usernames:
            if user.username == username:
                return render_template("error.html", message = "the username isn't avilable")
        db.execute("INSERT INTO login (username, password) VALUES(:user, :passw)",
                    {"user": username, "passw": password})
        db.commit()
        return redirect("/")
    return render_template("sign up.html")








@app.route("/books", methods = ["POST","GET"])
def books():

    return render_template("books.html")





@app.route("/book", methods = ["POST", "GET"])
def book():
    if request.method == "POST":
        sw = request.form.get("sw")
        useri = request.form.get("useri")
        if useri  is None :
            return render_template("error.html", message = "please enter data to seaech")

        if sw == "isbn":
            isbng = "%{}%".format(useri)
            books = db.execute("select * from books where isbn like :isbn",
                    {'isbn':isbng}).fetchall()

            if books is None:
                return render_template("error.html", message = "the isbn is invalid")

            return render_template("book.html", books = books)

        if sw == "title":
            title = "%{}%".format(useri)
            books = db.execute("select * from books where title like :title",
                    {'title':title}).fetchall()

            if books is None:
                return render_template("error.html", message = "the isbn is invalid")

            return render_template("book.html", books = books)

        if sw == "author":
            author = "%{}%".format(useri)
            books = db.execute("select * from books where author like :author",
                    {'author':author}).fetchall()

            if books is None:
                return render_template("error.html", message = "the isbn is invalid")

            return render_template("book.html", books = books)

        if sw == "year":
            books = db.execute("select * from books where year = :year",
                    {'year':useri}).fetchall()

            if books is None:
                return render_template("error.html", message = "the isbn is invalid")

            return render_template("book.html", books = books)


    return "it's get"



@app.route("/book/<int:book_id>", methods = ["GET", "POST"])
def bookinfo(book_id):
    if request.method == "POST":
        review = request.form.get("review")
        userr = session.get('user')

        try:
            myrate = int(request.form.get("rate"))
        except ValueError:
            return render_template("error.html", message = "please enter an integer")

        if myrate > 5:
            return render_template("error.html", message = "please enter rate from 1 to 5")


        reviewucheck = db.execute("select * from reviews where book_id = :id", {"id":book_id}).fetchall()

        for us in reviewucheck:
            if userr == us.userr :
                return render_template("error.html", message = "you can't submit more than one review.")

        db.execute("insert into reviews (review, userr, rate, book_id) values(:review, :userr, :rate, :book_id)",
                   {"review": review, "userr": userr, "rate": myrate, "book_id": book_id})
        db.commit()
        return redirect(url_for('bookinfo', book_id = book_id))

    book = db.execute("select * from books where id = :id",
            {"id":book_id}).fetchone()

    if book is None :
        return render_template("error.html", message = "invalid input")

    reviews = db.execute("select * from reviews where book_id = :id", {"id":book_id}).fetchall()


    isbn = book.isbn
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "UxHkEd0M6od9hTwb0nA", "isbns": isbn})

    data = res.json()
    rating = data["books"][0]["average_rating"]
    counts = data["books"][0]["ratings_count"]


    return render_template("bookinfo.html", book = book, rating = rating, counts = counts, reviews = reviews)



@app.route("/api/book/<int:book_id>", methods = ["GET", "POST"])
def book_api(book_id):
    booki = db.execute("select * from books where id = :id", {"id":book_id}).fetchone()
    avgrate = db.execute("select avg(rate) from reviews")
    rcount = db.execute("select count(*) from reviews")

    if booki is None:
        return jsonify({"error" : "invalid book id."}), 404








    return jsonify({
        "book_title": booki.title,
        "book_author": booki.author,
        "book_isbn": booki.isbn,
        "book_year": booki.year,
        "review_count": [dict(row) for row in rcount],

        })







@app.route("/logout")
def logout():
    session['user'] = None
    return redirect(url_for("index"))
