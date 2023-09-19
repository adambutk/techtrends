import sqlite3
import logging

from flask import Flask, json, render_template, request, url_for, redirect, flash


# Counter for db connections
db_connection_count = 0


# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global db_connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    # add one new connection to the counter
    db_connection_count += 1
    return connection


# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                              (post_id,)).fetchone()
    connection.close()
    return post


# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Healthcheck endpoint
@app.route('/healthz')
def health():
    # Connect to db
    connection = get_db_connection()
    # Respond with error if the connection to the database fails or if the required posts table does not exist.
    try:
        connection.execute('SELECT * FROM posts').fetchall()
    except sqlite3.OperationalError:
        connection.close()
        return app.response_class(
            response=json.dumps({"result": "ERROR - unhealthy"}),
            status=500,
            mimetype='application/json'
        )
    connection.close()
    # A JSON response containing the result: OK - healthy message
    # with a status code of 200
    response = app.response_class(
        response=json.dumps({"result": "OK - healthy"}),
        status=200,
        mimetype='application/json'
    )
    return response


# Metrics endpoint
@app.route('/metrics')
def metrics():
    # JSON response containing the database connection count
    # and the post count
    global db_connection_count
    connection = get_db_connection()
    post_count = connection.execute('SELECT COUNT(*) FROM posts').fetchone()[0]
    connection.close()
    response = app.response_class(
        response=json.dumps({"db_connection_count": db_connection_count, "post_count": post_count}),
        status=200,
        mimetype='application/json'
    )
    return response


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)


# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        app.logger.warning(f'Post ID "{post_id}" not found (404)')
        return render_template('404.html'), 404
    else:
        app.logger.info(f'Article "{post["title"]}" retrieved!')
        return render_template('post.html', post=post)


# Define the About Us page
@app.route('/about')
def about():
    app.logger.info(f'"About Us" page retrieved!')
    return render_template('about.html')


# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                               (title, content))
            connection.commit()
            connection.close()
            app.logger.info(f'Article "{title}" created!')
            return redirect(url_for('index'))

    return render_template('create.html')


# start the application on port 3111
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s:%(name)s:%(asctime)s, %(message)s',
                        datefmt='%m/%d/%Y, %H:%M:%S')
    app.run(host='0.0.0.0', port='3111')
