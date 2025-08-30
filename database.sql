-- Database schema for local prototyping
-- Run this with: sqlite3 database.db < database.sql

-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Sample content table
CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT,
    author_id INTEGER,
    published BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES users(id)
);

-- Insert sample data
INSERT INTO users (email, password_hash, name) VALUES 
    ('admin@example.com', 'hashed_password', 'Admin User'),
    ('user@example.com', 'hashed_password', 'Regular User');

INSERT INTO posts (title, content, author_id, published) VALUES 
    ('Welcome Post', 'This is a sample post for testing.', 1, 1),
    ('Draft Post', 'This is a draft post.', 2, 0);