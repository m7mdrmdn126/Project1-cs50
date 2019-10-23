import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker



engine = create_engine(os.getenv("DATABASE_URL" ,"postgres://ibrkvdfxbrmzoh:3d677fc83707eb93538fdd3c90ef3630bf2ab21703152a75effe69da8bbd9e96@ec2-184-73-209-230.compute-1.amazonaws.com:5432/db49hf6n6t475m"))
db = scoped_session(sessionmaker(bind = engine))


def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn":isbn, "title": title, "author": author, "year": year})
        print(f" Added book with isbn: {isbn} title: {title} author: {author} in year: {year}")
    db.commit()



if __name__ == "__main__":
    main()
