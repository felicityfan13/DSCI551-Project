from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy data for movies and reviews
movies = {
    1: {"title": "The Shawshank Redemption", "year": 1994},
    2: {"title": "The Godfather", "year": 1972},
    3: {"title": "The Dark Knight", "year": 2008}
}

reviews = {
    1: ["Amazing movie!", "One of the best movies I've ever seen."],
    2: ["Classic!", "A must-watch for everyone."],
    3: ["Incredible performance by Heath Ledger."]
}

@app.route('/')
def index():
    return render_template('index.html', movies=movies)

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie_info = movies.get(movie_id)
    movie_reviews = reviews.get(movie_id, [])
    return render_template('movie.html', movie=movie_info, reviews=movie_reviews)

@app.route('/post_review/<int:movie_id>', methods=['POST'])
def post_review(movie_id):
    review = request.form['review']
    if review:
        if movie_id in reviews:
            reviews[movie_id].append(review)
        else:
            reviews[movie_id] = [review]
    return redirect(url_for('movie', movie_id=movie_id))

if __name__ == '__main__':
    app.run(debug=True)
