from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'secret-key'

users = {}  # username: hashed_password
posts = []  # list of post dicts

@app.route('/')
def home():
    sorted_posts = sorted(posts, key=lambda x: x['date'], reverse=True)
    return render_template('home.html', posts=sorted_posts)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        if username in users:
            return "Username already exists!"
        
        users[username] = password
        session['user'] = username
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users and check_password_hash(users[username], password):
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            return "Invalid credentials!"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_posts = [post for post in posts if post['author'] == session['user']]
    return render_template('dashboard.html', posts=user_posts, user=session['user'])

@app.route('/create', methods=['GET', 'POST'])
def create_post():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        posts.append({
            'title': title,
            'content': content,
            'author': session['user'],
            'date': datetime.now()
        })
        return redirect(url_for('dashboard'))

    return render_template('create_post.html')

@app.route('/edit/<int:index>', methods=['GET', 'POST'])
def edit_post(index):
    if 'user' not in session or index >= len(posts) or posts[index]['author'] != session['user']:
        return redirect(url_for('dashboard'))

    post = posts[index]

    if request.method == 'POST':
        post['title'] = request.form['title']
        post['content'] = request.form['content']
        post['date'] = datetime.now()
        return redirect(url_for('dashboard'))

    return render_template('edit_post.html', post=post, index=index)

@app.route('/delete/<int:index>')
def delete_post(index):
    if 'user' in session and index < len(posts) and posts[index]['author'] == session['user']:
        posts.pop(index)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
