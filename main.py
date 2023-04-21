from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

# TMDB API
MOVIE_DB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
# API Key here
MOVIE_DB_API_KEY = "a0986ab45910f9d05a4a8e31a50c5b38" 
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

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

    ### Order the movie ###
    # Call all data from the all_movie.db by "class Movie"
    # This line creates a list of all the movies sorted by "rating"(It means 9.9, 8.6)
    # Movie.rating is get the rating data from the "class Movie"
    all_movies = Movie.query.order_by(Movie.rating).all()
	
    ### Show the big number of ranking ###
    #This line loops through all the movies
    for i in range(len(all_movies)):
        # This line gives each movie a new "ranking"(It means 1,2,3,4) reversed from their order in all_movies
        # And it will as a big number to show on the poster
        # It will start from 0, i=0, 
        # let say we have 10 movies, len(all_movies)=10
        # all_movies[0].ranking = 10 - 0
        all_movies[i].ranking = len(all_movies) - i
        # So, the Order 0 is the Ranking 10, the Order 9 is the Ranking 1, 
        # index.html will through {{ movie.ranking }} to get the Ranking number and display it on the poster
    db.session.commit()    

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



### Delete function ###
@app.route("/delete")
def delete_movie():
    # request will get the id from page that user clicked
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    # Delete it in DB with SQLAlchemy
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for("home"))



### Add function ###
class FindMovieForm(FlaskForm):
    # This is the input fields on the page
    title = StringField("Movie Title", validators=[DataRequired()])
    # This is the submit button on the page
    submit = SubmitField("Add Movie")


@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = FindMovieForm()
    # Get the Movie data from TMDB by API
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(MOVIE_DB_SEARCH_URL, params={"api_key": MOVIE_DB_API_KEY, "query": movie_title})
        data = response.json()["results"]
        # "option" is the variable that pass the data to the select.html
        return render_template("select.html", options=data)
      
    return render_template("add.html", form=form)



### Find function ###
@app.route("/find")
def find_movie():
    movie_api_id = request.args.get("id")
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience 
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            description=data["overview"]
        )
        db.session.add(new_movie)
        db.session.commit()
        # Redirect and pass the new_movie's id to rate_movie function
        return redirect(url_for("rate_movie", id=new_movie.id))




if __name__ == '__main__':
    app.run(debug=True)