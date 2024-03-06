from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['movie_reviews']

user_id = 0
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
        # Default admin account to manage all comments
        {"_id": 1, "name": "Admin", "password": "0000"},
        {"name": "felicity", "password": "12345"}
    ]
    users_collection.insert_many(user_data)


@app.route('/')
def index():
    # Retrieve all movies from the database
    movies = list(movies_collection.find())
    return render_template('index.html', movies=movies)

@app.route('/login')
def render_login():
    return render_template('login.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Query MongoDB to find the user
        user = users_collection.find_one({'name': username, 'password': password})
        
        # Check if the user exists and the password matches
        if user:
            global user_id
            user_id = user['_id']
            return redirect(url_for('profile'))
        else:
            return 'Invalid username or password'
    return render_template('login.html')

@app.route('/register')
def render_register():
    return render_template('register.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check duplicate user name
        existing_user = users_collection.find_one({'name': username})
        if existing_user:
            return 'Username already exists!'
        
        users_collection.insert_one({'name': username, 'password': password})
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/profile')
def profile():
    global user_id
    user = users_collection.find_one({"_id": user_id})
    if user_id == 1:
        comments = comments_collection.find()
    else:
        comment_ids_cursor = users_comments.find({"user_id": user_id})

        comment_ids = [comment['comment_id'] for comment in comment_ids_cursor]
        comments = comments_collection.find({"_id": {"$in": comment_ids}}) 
    
    # To be optimized - update the value passed into template, or maybe change of data structure
    comments_movie_title = []
    for comment in comments:
        movie_id = movies_comments.find_one({"comment_id": comment['_id']})
        movie = movies_collection.find_one({"_id": movie_id['movie_id']})
        if movie:
            updated_comment = dict(comment)
            updated_comment["title"] = movie['title']
            comments_movie_title.append(updated_comment)
    for comment in comments_movie_title:
        print(comment['title'])
    return render_template('profile.html', user=user, comments = comments_movie_title)

@app.route('/movie/<int:movie_id>')
def movie(movie_id):
    comment_ids_cursor = movies_comments.find({"movie_id": movie_id})
    comment_ids = [comment['comment_id'] for comment in comment_ids_cursor]
    comments = comments_collection.find({"_id": {"$in": comment_ids}}) 
    movie_info = movies_collection.find_one({"_id": movie_id})
    return render_template('movie.html', movie=movie_info, comments=comments)


@app.route('/post_comment/<int:movie_id>', methods=['POST'])
def post_comment(movie_id):
    comment = request.form['comment']
    if comment:
        result = comments_collection.insert_one({"comment": comment})
        comment_id = result.inserted_id
        movies_comments.insert_one({"movie_id": movie_id, "comment_id": comment_id})

        users_comments.insert_one({"user_id": user_id, "comment_id": comment_id})
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
