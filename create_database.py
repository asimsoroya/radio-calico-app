#!/usr/bin/env python3
import sqlite3
import os

# Create database connection
db_path = 'database.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Creating database tables...")

# Create users table
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Create posts table
cursor.execute('''
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    author_id INTEGER,
    published BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
)
''')

print("Inserting sample data...")

# Insert sample users
cursor.execute("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
               ('admin@example.com', 'hashed_password', 'Admin User'))
cursor.execute("INSERT INTO users (email, password_hash, name) VALUES (?, ?, ?)",
               ('user@example.com', 'hashed_password', 'Regular User'))

# Insert sample posts
cursor.execute("INSERT INTO posts (title, content, author_id, published) VALUES (?, ?, ?, ?)",
               ('Welcome Post', 'This is a sample post for testing.', 1, 1))
cursor.execute("INSERT INTO posts (title, content, author_id, published) VALUES (?, ?, ?, ?)",
               ('Draft Post', 'This is a draft post.', 2, 0))

# Commit changes and close
conn.commit()
conn.close()

print(f"Database setup complete!")
print(f"Database file: {os.path.abspath(db_path)}")
print("To view data, use python to connect to the database or install sqlite3 separately.")