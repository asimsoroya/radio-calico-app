const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Database connection
const dbPath = path.join(__dirname, 'database.db');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error opening database:', err.message);
    } else {
        console.log('Connected to SQLite database');
    }
});

// Routes
app.get('/', (req, res) => {
    res.json({ message: 'RadioCalio2 API Server', status: 'running' });
});

// Get all users
app.get('/api/users', (req, res) => {
    db.all('SELECT id, email, name, created_at FROM users', (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ users: rows });
    });
});

// Get all posts
app.get('/api/posts', (req, res) => {
    const query = `
        SELECT p.id, p.title, p.content, p.published, p.created_at,
               u.name as author_name, u.email as author_email
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        ORDER BY p.created_at DESC
    `;
    
    db.all(query, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ posts: rows });
    });
});

// Get published posts only
app.get('/api/posts/published', (req, res) => {
    const query = `
        SELECT p.id, p.title, p.content, p.created_at,
               u.name as author_name, u.email as author_email
        FROM posts p
        LEFT JOIN users u ON p.author_id = u.id
        WHERE p.published = 1
        ORDER BY p.created_at DESC
    `;
    
    db.all(query, (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ posts: rows });
    });
});

// Create a new post
app.post('/api/posts', (req, res) => {
    const { title, content, author_id, published = 0 } = req.body;
    
    if (!title || !author_id) {
        return res.status(400).json({ error: 'Title and author_id are required' });
    }
    
    const query = 'INSERT INTO posts (title, content, author_id, published) VALUES (?, ?, ?, ?)';
    db.run(query, [title, content, author_id, published], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json({ 
            message: 'Post created successfully',
            post_id: this.lastID 
        });
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log('Available endpoints:');
    console.log('  GET  / - Server status');
    console.log('  GET  /api/users - All users');
    console.log('  GET  /api/posts - All posts');
    console.log('  GET  /api/posts/published - Published posts only');
    console.log('  POST /api/posts - Create new post');
});

// Graceful shutdown
process.on('SIGINT', () => {
    db.close((err) => {
        if (err) {
            console.error('Error closing database:', err.message);
        } else {
            console.log('Database connection closed');
        }
        process.exit(0);
    });
});