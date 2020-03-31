'''
Aditya Chaudhari, ac3959@drexel.edu
CS530: DUI project
'''

import csv
import os
from flask import Flask, render_template, send_file
from models import *
from application import DATABASE_URL


app = Flask(__name__, static_folder='public', static_url_path='')
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():
    db.create_all()
    f = open("C:/Users/Aditya Chaudhari/Desktop/cs530/Project/books.csv")
    reader = csv.reader(f, delimiter=',')
    next(reader)              # skips the top line
    for ISBN, title, author, date in reader:
        book = Book(isbn = ISBN, title = title, author = author, publicationyear = int(date))
        db.session.add(book)
        #print(f"Added book with {ISBN}, title : {title}, author: {author}, publication year: {date}.")
    print("commiting")
    db.session.commit()
    print("committed all data")

if __name__ == "__main__":
    with app.app_context():
        main()
