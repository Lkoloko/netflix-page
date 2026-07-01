from flask import Flask, render_template, request, redirect
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)


df = pd.read_csv("cleaned_netflix_data.csv")

@app.route("/")
def home():
    movies = df[df['type'] == 'Movie']
    shows = df[df['type'] == 'TV Show']

    num_movies = len(movies)
    num_shows = len(shows)

    common_rating = df['rating'].mode()[0]

    #total_movie_hours = movies['duration'].sum() / 60

    recent_movies = movies.sort_values(by='date_added', ascending=False).head(10)

    return render_template("home.html",
                           num_movies=num_movies,
                           num_shows=num_shows,
                           common_rating=common_rating,
                           #total_movie_hours=round(total_movie_hours, 2),
                           recent_movies=recent_movies.to_dict(orient='records'))


@app.route("/analytics")
def analytics():
    os.makedirs("static/charts", exist_ok=True)

    # Movies vs Shows
    df['type'].value_counts().plot(kind='bar')
    plt.savefig("static/charts/type.png")
    plt.clf()

    # Movies by rating
    df[df['type']=='Movie']['rating'].value_counts().plot(kind='bar')
    plt.savefig("static/charts/movie_rating.png")
    plt.clf()

    # TV Shows pie
    df[df['type']=='TV Show']['rating'].value_counts().plot(kind='pie')
    plt.savefig("static/charts/tv_rating.png")
    plt.clf()

    return render_template("analytics.html")

@app.route("/timing")
def timing():
    recent = df[df['release_year'] >= (df['release_year'].max() - 10)]

    # Movies last 10 years
    recent[recent['type']=='Movie']['release_year'].value_counts().plot(kind='bar')
    plt.savefig("static/charts/movies_10.png")
    plt.clf()

    # Shows last 10 years
    recent[recent['type']=='TV Show']['release_year'].value_counts().plot(kind='bar')
    plt.savefig("static/charts/shows_10.png")
    plt.clf()

    return render_template("timing.html")

@app.route("/movies", methods=['GET', 'POST'])
def movies():
    movies = df[df['type'] == 'Movie']

    search = request.form.get('search')
    if search:
        movies = movies[movies['title'].str.contains(search, case=False)]

    return render_template("movies.html",
                           movies=movies.to_dict(orient='records'))

@app.route("/shows", methods=['GET', 'POST'])
def shows():
    shows = df[df['type'] == 'TV Show']

    search = request.form.get('search')
    if search:
        shows = shows[shows['title'].str.contains(search, case=False)]

    return render_template("shows.html",
                           shows=shows.to_dict(orient='records'))


@app.route("/add", methods=['GET', 'POST'])
def add():
    global df
    if request.method == "POST":
        new_data = {
            "type": request.form['type'],
            "title": request.form['title'],
            "director": request.form['director'],
            "country": request.form['country'],
            "release_year": int(request.form['year']),
            "duration": int(request.form['duration']),
            "rating": request.form['rating']
        }

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        df.to_csv("cleaned_netflix.csv", index=False)

        return redirect("/")

    return render_template("add.html")


if __name__ == "__main__":
    app.run(debug=True)