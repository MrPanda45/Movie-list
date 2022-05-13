from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy, orm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

API_SEARCH_TITLE = "https://api.themoviedb.org/3/search/movie"
API_SEARCH_ID = "https://api.themoviedb.org/3/movie/"
API_KEY = "22487d4bf561df7d2057bfb63bbcdfe6"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies-list.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CREATE TABLE
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(500), nullable=True)
    img_url = db.Column(db.String(200), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed.
    def __repr__(self):
        return f'{self.id}'

# db.create_all()

# new_movie = Movie(
#     title="Phone Booth",
#     year=2002,
#     description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
#     rating=7.3,
#     ranking=10,
#     review="My favourite character was the caller.",
#     img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
# )
# db.session.add(new_movie)
# db.session.commit()

# CREATE RECORD

## Read all records
# all_books_db = session.query(Book).all()

## Read a particular record by query
# book = Book.query.filter_by(title='Harry Potter').first()

## Update a particular record by query
# book_to_update = Book.query.filter_by(title="Harry Potter").first()
# book_to_update.title = "Harry Potter and the Chamber of Secrets"
# db.session.commit()

## Update a record by primary key
# book_id = 1
# book_to_update = Book.query.get(book_id)
# book_to_update.title = "Harry Potter and the Goblet of Fire"
# db.session.commit()

## Delete a particular record by primary key
# book_id = 1
# book_to_delete = Book.query.get(book_id)
# db.session.delete(book_to_delete)
# db.session.commit()


class UpdateForm(FlaskForm):
    rating = StringField(label="Your rating out of 10 e.g. 7.5", validators=[DataRequired()])
    review = StringField(label="Your review", validators=[DataRequired()])
    submit = SubmitField(label="Done")


class AddForm(FlaskForm):
    title = StringField(label="Movie Title", validators=[DataRequired()])
    submit = SubmitField(label="Add movie")


@app.route("/")
def home():
    all_movies_db = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies_db)):
        all_movies_db[i].ranking = len(all_movies_db) - i

    db.session.commit()
    return render_template("index.html", movies=all_movies_db)


@app.route('/edit/<id>', methods=["GET", "POST"])
def edit(id):
    rating_form = UpdateForm()
    movie = Movie.query.filter_by(id=id).first()
    if rating_form.validate_on_submit():
        movie_id = id
        movie_to_update = Movie.query.get(movie_id)
        movie_to_update.rating = rating_form.rating.data
        movie_to_update.review = rating_form.review.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit.html", movie=movie, form=rating_form)


@app.route('/delete/<id>')
def delete(id):
    movie_id = id
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


@app.route('/add', methods=["GET", "POST"])
def add():
    add_form = AddForm()
    post = False
    if request.method == "POST":
        post = True
        movie_add_title = add_form.title.data
        params = {
            "api_key": API_KEY,
            "query": movie_add_title
        }

        response = requests.get(API_SEARCH_TITLE, params=params)
        response.raise_for_status()
        data = response.json()['results']
        return render_template("add.html", data=data, post=post)

    return render_template("add.html", form=add_form)


@app.route('/find/<id>')
def find(id):
    full_api_id = f"{API_SEARCH_ID}{id}"
    params = {
        "api_key": API_KEY
    }

    response = requests.get(full_api_id, params=params)
    response.raise_for_status()
    data = response.json()
    new_movie = Movie(
        title=data['original_title'],
        year=data['release_date'],
        description=data['overview'],
        img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
    )
    db.session.add(new_movie)
    db.session.commit()

    movie_id = Movie.query.filter_by(title=data['original_title']).first()

    return redirect(url_for("edit", id=movie_id))


if __name__ == '__main__':
    app.run()
