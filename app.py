from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_reviews']

# Create collections
movies_collection = db['movies']
comments_collection = db['comments']

# Check if the movies collection is empty
if movies_collection.count_documents({}) == 0:
    # If empty, insert the dummy movie data into the movies collection
    movies_data = [
        {"_id": 1, "title": "The Shawshank Redemption", "year": 1994},
        {"_id": 2, "title": "The Godfather", "year": 1972},
        {"_id": 3, "title": "The Dark Knight", "year": 2008}
    ]
    movies_collection.insert_many(movies_data)

@app.route('/')
def index():
    # Retrieve all movies from the database
    movies = list(movies_collection.find())
    return render_template('index.html', movies=movies)

@app.route('/profile')
def profile():
    return render_template('login.html')

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    movie_info = movies_collection.find_one({"_id": movie_id})
    comments = comments_collection.find({"movie_id": movie_id})
    return render_template('movie.html', movie=movie_info, comments=comments)

@app.route('/post_comment/<int:movie_id>', methods=['POST'])
def post_comment(movie_id):
    print("success or not_______________________")
    comment = request.form['comment']
    if comment:
        comments_collection.insert_one({"movie_id": movie_id, "comment": comment})
    return redirect(url_for('movie', movie_id=movie_id))

if __name__ == '__main__':
    app.run(debug=True)
