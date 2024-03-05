from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_reviews']

# Create collections
movies_collection = db['movies']
comments_collection = db['comments']
users_collection = db['users']
movies_comments = db['movies_comments']
users_comments = db['users_comments']

if movies_collection.count_documents({}) == 0:
    # If empty, insert the dummy movie data into the movies collection
    movies_data = [
        {"_id": 1, "title": "The Shawshank Redemption", "year": 1994},
        {"_id": 2, "title": "The Godfather", "year": 1972},
        {"_id": 3, "title": "The Dark Knight", "year": 2008}
    ]
    movies_collection.insert_many(movies_data)

if users_collection.count_documents({}) == 0:
    # If empty, insert the dummy movie data into the movies collection
    user_data = [
        {"_id": 1, "name": "Guest 1"}
    ]
    users_collection.insert_many(user_data)


@app.route('/')
def index():
    # Retrieve all movies from the database
    movies = list(movies_collection.find())
    return render_template('index.html', movies=movies)

@app.route('/profile')
def profile():
    # Update the user_id by login information in the future
    user = users_collection.find_one({"_id": 1})
    comment_ids_cursor = users_comments.find({"user_id": 1})

    comment_ids = [comment['comment_id'] for comment in comment_ids_cursor]
    comments = comments_collection.find({"_id": {"$in": comment_ids}}) 

    return render_template('profile.html', user=user, comments = comments)

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    comment_ids_cursor = movies_comments.find({"movie_id": movie_id})
    comment_ids = [comment['comment_id'] for comment in comment_ids_cursor]
    comments = comments_collection.find({"_id": {"$in": comment_ids}}) 
    movie_info = movies_collection.find_one({"_id": movie_id})
    
    # update in the future: Retrieve the user id that posted each comment and add it to comments
    user = users_collection[0]

    return render_template('movie.html', movie=movie_info, comments=comments)


@app.route('/post_comment/<int:movie_id>', methods=['POST'])
def post_comment(movie_id):
    comment = request.form['comment']
    if comment:
        result = comments_collection.insert_one({"comment": comment})
        comment_id = result.inserted_id
        movies_comments.insert_one({"movie_id": movie_id, "comment_id": comment_id})

        # update in the future: Retrieve the user id that post each comment
        users_comments.insert_one({"user_id": 1, "comment_id": comment_id})
    return redirect(url_for('movie', movie_id=movie_id))

@app.route('/delete_comment/<string:comment_id>', methods=['POST'])
def delete_comment(comment_id):
    comment_id = ObjectId(comment_id)
    comments_collection.delete_one({"_id": comment_id})
    users_collection.delete_one({"comment_id": comment_id})
    movies_comments.delete_one({"comment_id": comment_id})
    return redirect(url_for('profile'))

@app.route('/edit_comment/<string:comment_id>', methods=['POST'])
def edit_comment(comment_id):
    comment_id = ObjectId(comment_id)
    edited_comment = request.form['edited_comment']
    comments_collection.update_one({"_id": comment_id}, {"$set": {"comment": edited_comment}})
    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)
