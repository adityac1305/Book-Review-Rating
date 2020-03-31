Book Review
Book review website using Python, Flask, SQL, and BootStrap where a user can signup, log into and search for books using a name, ISBN or author.
Check out reviews and add a review to a book(at most one).
Displays ratings and reviews from Goodreads for a broader audience.
Uses Goodreads API and Open Library covers API. The website also has its own API.


API Access: 
If users make a GET request to the website’s /api/<isbn> route, where <isbn> is an ISBN number,
the website returns a JSON response containing the book’s title, author, publication date, ISBN number, review count, and average score. 

models.py contains all the tables which are created by using SQLAlchemy 
import.py imports all the data of the models into the postgres database and also imports the data from books.csv into book


How to run 

import the following packages 

pip install Flask
pip install Flask-Session
pip install psycopg2
pip install SQLAlchemy
pip install requests

Start the postgres server on your machine 
Go to the path of the run.py file in terminal and type python run.py
to host the website locally.