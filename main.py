from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests


app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)


## CREATE DATABASE
### A "all-movie.db" file appear in the root folder after run the db.create_all()
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///all_movie.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



## CREATE TABLE
### Attention data type
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()



## If this part has not to be commented, Flask app Server will not Start
## After adding the new_movie the code needs to be commented out/deleted.
## So you are not trying to add the same movie twice.
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



@app.route("/")
def home():
	# Pass the data to the index.html
    # Call the all data from the all_movie.db
    all_movies = Movie.query.all()
    # Loop through all data and pass the data to index.html
    # "movies" is the variable that pass the data to the index.html
    return render_template("index.html", movies=all_movies)



### Edit function ###
class RateMovieForm(FlaskForm):
    # This is the input fields on the page
    rating = StringField('Your rating out of 10 e.g. 7.5')
    review = StringField('Your review:')
    # This is the submit button on the page
    submit = SubmitField('Done')
    

@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    # Get the value form page
    form = RateMovieForm()
    # request will get the id from page that user clicked
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete")
def delete_movie():
    # request will get the id from page that user clicked
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    # Delete it in DB with SQLAlchemy
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))










if __name__ == '__main__':
    app.run(debug=True)