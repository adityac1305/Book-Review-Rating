'''
Aditya Chaudhari, ac3959@drexel.edu
CS530: DUI project
'''
import os, requests
from flask import Flask, session, render_template, jsonify, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

#Goodreads API Key
GOODREADS_API_KEY = "vblp6JmsLMf9SehrZSbqQ"
#postgres url
DATABASE_URL = "postgres://postgres:12345678@localhost:5432/postgres"


app = Flask(__name__, static_folder='public', static_url_path='')

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(DATABASE_URL)
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=['GET','POST'])
def index():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        user = db.execute("SELECT * FROM users WHERE username = :username and password = :password",
        {"username": username, "password": password} ).fetchone()
        #check if user exist in the database
        if user is None or username is None or password is None:
            return render_template("error.html", message = "username and password does not match")
        else:
            #log the user in
            session["user_id"] = user.username
            return render_template("search.html", username = username)
    #if user has not logged out
    elif session.get("user_id") is not None:
        return render_template("search.html", username = session.get("user_id"))
    # GET request
    else:
        return render_template("index.html")

@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        f = request.form.get("fname")
        l = request.form.get("lname")
        u = request.form.get("username")
        p = request.form.get("password")
        cp = request.form.get("confirmpassword")
        e = request.form.get("email")
        # if a field is left empty by the user(tested)
        if u is "" or p is "" or e is "" or cp is "" or f is "" or l is "":
            return render_template("signup.html", message = "Please fill all fields to sign up")
        # if passwords don't match(tested)
        if p != cp:
            return render_template("signup.html", message = "Passwords don't match")
        # if username already exists in database(tested)
        if db.execute("SELECT username FROM users WHERE username = :username",
            {"username": u}).rowcount > 0:
            return render_template("signup.html", message = "Username already exists")
        # unique email check(tested)
        if db.execute("SELECT email FROM users WHERE email = :email",
            {"email": e}).rowcount > 0:
            return render_template("signup.html", message = "Email already exists please use another email")
        # register user into database(tested)
        else:
            db.execute("INSERT into users(username, password, email, fname, lname) VALUES (:username,:password,:email,:fname,:lname)",
            {"username": u, "password": p,"email": e, "fname": f, "lname": l})
            db.commit()
            return render_template("signup.html", text = "Registeration successfully!")

    # Get Request
    return render_template("signup.html")

# logout feature
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return render_template("index.html")

# Search page functionality
@app.route("/search", methods=['GET','POST'])
def search():
    if session.get("user_id") is None:
        render_template("error.html", message = "Login Required")
    if request.method == 'POST':
        user_search = request.form.get("search")
        # user is searching by title
        if request.form.get("inlineRadioOptions") == "option1":
            book_search = db.execute("SELECT * FROM books WHERE LOWER(title) LIKE LOWER(:s)", { "s": '%' + user_search + '%'}).fetchall()
            return render_template("search.html", username = session["user_id"], result = book_search)
        # user is searching by ISBN
        elif request.form.get("inlineRadioOptions") == "option2":
            book_search = db.execute("SELECT * FROM books WHERE isbn LIKE LOWER(:s)", { "s": '%' + user_search + '%'}).fetchall()
            return render_template("search.html", username = session["user_id"], result = book_search)
        # user is searching by author name
        else:
            book_search = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:s)", { "s": '%' + user_search + '%'}).fetchall()
            return render_template("search.html", username = session["user_id"], result = book_search)
    return render_template("search.html", username = session["user_id"])

#book page functionality
@app.route("/book/<string:isbn>", methods=['GET','POST'])
def book(isbn):
    # is user logged in or not
    if session.get("user_id") is None:
        return render_template("error.html", message="Login Required")
    # check if book is in database
    if db.execute('SELECT * FROM books WHERE isbn = :isbn' , {"isbn": isbn}).rowcount == 0:
        return render_template("error.html", message="Error 404: Page not found")

    book = db.execute('SELECT * FROM books WHERE isbn = :isbn', {"isbn": isbn}).fetchone()

    # From Goodreads getting average rating and number of ratings
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_API_KEY, "isbns": isbn})
    avg_rating_Goodreads = res.json()['books'][0]['average_rating']
    number_rating_Goodreads = res.json()['books'][0]['work_ratings_count']

    # trying to collect votes
    #poll_vote_Goodreads = res.json()['books'][0]['total_votes']

    if request.method == 'POST':
        u_id = db.execute('SELECT * FROM users WHERE username = :u', {"u": session["user_id"]}).fetchone()
        u_id = u_id.id

        rating = request.form.get("rating")
        review = request.form.get("review")
        db.execute("INSERT into reviews (userid, bookid, rating, text) VALUES (:u_id,:b_id,:rating,:review)",
        {"u_id": u_id, "b_id": book.id,"rating": rating, "review": review})
        db.commit()
        reviews = db.execute('SELECT * FROM reviews WHERE bookid = :b_id', {"b_id": book.id}).fetchall()
        text = "Review submitted"
        return render_template("book.html", book = book, username = session["user_id"], isbn = isbn, reviews = reviews,
        avg_rating_Goodreads = avg_rating_Goodreads,number_rating_Goodreads = number_rating_Goodreads, text = text)

    reviews = db.execute('SELECT * FROM reviews WHERE bookid = :b_id', {"b_id": book.id}).fetchall()
    return render_template("book.html", book = book, username = session["user_id"], isbn = isbn, reviews = reviews,
    avg_rating_Goodreads = avg_rating_Goodreads,number_rating_Goodreads = number_rating_Goodreads)

# api design that returns a json object
@app.route("/api/<string:isbn>")
def api(isbn):
    if db.execute('SELECT * FROM books WHERE isbn = :isbn', {"isbn": isbn}).rowcount == 0:
        return jsonify({"error":"Invalid ISBN"}), 404

    jsonobj = {"title": "",
                "author": "",
                "year": 0,
                "isbn": isbn,
                "review_count": 0,
                "average_score": 0.0,
                "votes":0
            }

    
    #requesting data from goodreads
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": GOODREADS_API_KEY, "isbns": isbn})

    jsonobj["average_score"] = res.json()['books'][0]['average_rating']
    jsonobj["review_count"] = res.json()['books'][0]['work_ratings_count']
    #trying to collect votes

    #jsonobj["votes"] = res.json()[books][0]['total_votes']

    data = db.execute("SELECT title, author, publicationyear FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    jsonobj["title"] = data.title
    jsonobj["author"] = data.author
    jsonobj["year"] = data.publicationyear


    return jsonify(jsonobj)

# about feature
@app.route("/about")
def about():
    return render_template("about.html")

# books feature which displays author and his books
@app.route("/books", methods=['GET','POST'])
def books():
    books_search = ""
    user1_search = ""
    if request.method == 'POST':
        user_search1 = request.form.get("books")
        books_search = db.execute("SELECT * FROM books WHERE LOWER(author) LIKE LOWER(:s)", { "s": '%' + user_search1 + '%'}).fetchall()
    return render_template("books.html", result = books_search)


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080, debug=True)