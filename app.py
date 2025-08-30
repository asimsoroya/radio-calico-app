from flask import Flask, request, jsonify, g
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)

# Database configuration
DATABASE = 'database.db'

def get_db():
    """Get database connection"""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # This enables column access by name
    return g.db

def close_db(e=None):
    """Close database connection"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def close_db(error):
    close_db()

# Routes
@app.route('/')
def home():
    return jsonify({
        'message': 'RadioCalio2 Flask API Server',
        'status': 'running',
        'database': 'SQLite'
    })

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    db = get_db()
    users = db.execute(
        'SELECT id, email, name, created_at FROM users ORDER BY created_at DESC'
    ).fetchall()
    
    return jsonify({
        'users': [dict(user) for user in users]
    })

@app.route('/api/posts', methods=['GET'])
def get_posts():
    """Get all posts with author information"""
    db = get_db()
    posts = db.execute('''
        SELECT p.id, p.title, p.content, p.published, p.created_at,
               u.name as author_name, u.email as author_email
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    return jsonify({
        'posts': [dict(post) for post in posts]
    })

@app.route('/api/posts/published', methods=['GET'])
def get_published_posts():
    """Get only published posts"""
    db = get_db()
    posts = db.execute('''
        SELECT p.id, p.title, p.content, p.created_at,
               u.name as author_name, u.email as author_email
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.published = 1
        ORDER BY p.created_at DESC
    ''').fetchall()
    
    return jsonify({
        'posts': [dict(post) for post in posts]
    })

@app.route('/api/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID"""
    db = get_db()
    post = db.execute('''
        SELECT p.id, p.title, p.content, p.published, p.created_at,
               u.name as author_name, u.email as author_email
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.id = ?
    ''', (post_id,)).fetchone()
    
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    return jsonify({'post': dict(post)})

@app.route('/api/posts', methods=['POST'])
def create_post():
    """Create a new post"""
    data = request.get_json()
    
    if not data or not data.get('title') or not data.get('author_id'):
        return jsonify({'error': 'Title and author_id are required'}), 400
    
    title = data.get('title')
    content = data.get('content', '')
    author_id = data.get('author_id')
    published = data.get('published', 0)
    
    db = get_db()
    cursor = db.execute(
        'INSERT INTO posts (title, content, author_id, published) VALUES (?, ?, ?, ?)',
        (title, content, author_id, published)
    )
    db.commit()
    
    return jsonify({
        'message': 'Post created successfully',
        'post_id': cursor.lastrowid
    }), 201

@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a post"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    db = get_db()
    
    # Check if post exists
    post = db.execute('SELECT id FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    # Update fields
    fields = []
    values = []
    
    if 'title' in data:
        fields.append('title = ?')
        values.append(data['title'])
    if 'content' in data:
        fields.append('content = ?')
        values.append(data['content'])
    if 'published' in data:
        fields.append('published = ?')
        values.append(data['published'])
    
    if not fields:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    fields.append('updated_at = CURRENT_TIMESTAMP')
    values.append(post_id)
    
    query = f"UPDATE posts SET {', '.join(fields)} WHERE id = ?"
    db.execute(query, values)
    db.commit()
    
    return jsonify({'message': 'Post updated successfully'})

@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a post"""
    db = get_db()
    
    # Check if post exists
    post = db.execute('SELECT id FROM posts WHERE id = ?', (post_id,)).fetchone()
    if post is None:
        return jsonify({'error': 'Post not found'}), 404
    
    db.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    db.commit()
    
    return jsonify({'message': 'Post deleted successfully'})

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DATABASE):
        print(f"Database {DATABASE} not found. Please run create_database.py first.")
        exit(1)
    
    print("Starting Flask server...")
    print("Available endpoints:")
    print("  GET    / - Server status")
    print("  GET    /api/users - All users")
    print("  GET    /api/posts - All posts")
    print("  GET    /api/posts/published - Published posts only")
    print("  GET    /api/posts/<id> - Specific post")
    print("  POST   /api/posts - Create new post")
    print("  PUT    /api/posts/<id> - Update post")
    print("  DELETE /api/posts/<id> - Delete post")
    
    app.run(debug=True, host='0.0.0.0', port=5000)