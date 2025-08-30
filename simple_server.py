#!/usr/bin/env python3
import http.server
import socketserver
import json
import sqlite3
import urllib.parse
from urllib.parse import urlparse, parse_qs

PORT = 8000

class RadioCalioHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if path == '/':
            self.serve_file('index.html')
        elif path == '/radio':
            self.serve_file('radio.html')
        elif path == '/api/users':
            self.get_users()
        elif path == '/api/posts':
            self.get_posts()
        elif path == '/api/posts/published':
            self.get_published_posts()
        elif path.startswith('/api/ratings/'):
            self.handle_ratings_get(path)
        elif path.startswith('/static/') or path.endswith(('.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.ico')):
            self.serve_file(path.lstrip('/'))
        else:
            self.send_error(404, 'Not Found')
    
    def do_POST(self):
        if self.path == '/api/posts':
            self.create_post()
        elif self.path == '/api/users':
            self.create_user()
        elif self.path == '/api/ratings':
            self.create_rating()
        else:
            self.send_error(404, 'Not Found')
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def serve_file(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                content = f.read()
            
            self.send_response(200)
            if filepath.endswith('.html'):
                self.send_header('Content-type', 'text/html')
            elif filepath.endswith('.css'):
                self.send_header('Content-type', 'text/css')
            elif filepath.endswith('.js'):
                self.send_header('Content-type', 'application/javascript')
            elif filepath.endswith('.png'):
                self.send_header('Content-type', 'image/png')
            elif filepath.endswith('.jpg') or filepath.endswith('.jpeg'):
                self.send_header('Content-type', 'image/jpeg')
            elif filepath.endswith('.gif'):
                self.send_header('Content-type', 'image/gif')
            elif filepath.endswith('.ico'):
                self.send_header('Content-type', 'image/x-icon')
            else:
                self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, 'File not found')
    
    def get_users(self):
        try:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT id, email, name, created_at FROM users ORDER BY created_at DESC')
            users = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json({'users': users})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def get_posts(self):
        try:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.title, p.content, p.published, p.created_at,
                       u.name as author_name, u.email as author_email
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                ORDER BY p.created_at DESC
            ''')
            posts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json({'posts': posts})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def get_published_posts(self):
        try:
            conn = sqlite3.connect('database.db')
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT p.id, p.title, p.content, p.created_at,
                       u.name as author_name, u.email as author_email
                FROM posts p
                LEFT JOIN users u ON p.author_id = u.id
                WHERE p.published = 1
                ORDER BY p.created_at DESC
            ''')
            posts = [dict(row) for row in cursor.fetchall()]
            conn.close()
            self.send_json({'posts': posts})
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def create_post(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not data.get('title') or not data.get('author_id'):
                self.send_json({'error': 'Title and author_id are required'}, 400)
                return
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO posts (title, content, author_id, published) VALUES (?, ?, ?, ?)',
                (data.get('title'), data.get('content', ''), data.get('author_id'), data.get('published', 0))
            )
            conn.commit()
            post_id = cursor.lastrowid
            conn.close()
            
            self.send_json({'message': 'Post created successfully', 'post_id': post_id}, 201)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def create_user(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            if not data.get('email') or not data.get('name'):
                self.send_json({'error': 'Email and name are required'}, 400)
                return
            
            # Simple password hash (in production, use proper hashing)
            password_hash = data.get('password', 'default_password')
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            try:
                cursor.execute(
                    'INSERT INTO users (email, name, password_hash) VALUES (?, ?, ?)',
                    (data.get('email'), data.get('name'), password_hash)
                )
                conn.commit()
                user_id = cursor.lastrowid
                conn.close()
                
                self.send_json({'message': 'User created successfully', 'user_id': user_id}, 201)
            except sqlite3.IntegrityError:
                conn.close()
                self.send_json({'error': 'Email already exists'}, 409)
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def handle_ratings_get(self, path):
        """Handle GET requests for ratings"""
        path_parts = path.split('/')
        if len(path_parts) >= 4 and path_parts[3] == 'song':
            # GET /api/ratings/song?title=...&artist=...
            query_params = self.parse_query_params()
            title = query_params.get('title', [''])[0]
            artist = query_params.get('artist', [''])[0]
            
            if not title or not artist:
                self.send_json({'error': 'Title and artist parameters required'}, 400)
                return
                
            self.get_song_ratings(title, artist)
        else:
            self.send_error(404, 'Not Found')
    
    def parse_query_params(self):
        """Parse query parameters from URL"""
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(self.path)
        return parse_qs(parsed.query)
    
    def get_song_ratings(self, title, artist):
        """Get ratings for a specific song"""
        try:
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            # Get thumbs up count
            cursor.execute(
                'SELECT COUNT(*) FROM song_ratings WHERE song_title = ? AND song_artist = ? AND rating = 1',
                (title, artist)
            )
            thumbs_up = cursor.fetchone()[0]
            
            # Get thumbs down count
            cursor.execute(
                'SELECT COUNT(*) FROM song_ratings WHERE song_title = ? AND song_artist = ? AND rating = -1',
                (title, artist)
            )
            thumbs_down = cursor.fetchone()[0]
            
            conn.close()
            
            self.send_json({
                'song': {'title': title, 'artist': artist},
                'ratings': {
                    'thumbs_up': thumbs_up,
                    'thumbs_down': thumbs_down,
                    'total': thumbs_up + thumbs_down
                }
            })
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def create_rating(self):
        """Create or update a song rating"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Validate required fields
            title = data.get('title')
            artist = data.get('artist')
            album = data.get('album', '')
            rating = data.get('rating')  # 1 for thumbs up, -1 for thumbs down
            
            # Generate persistent user identifier based on client characteristics
            user_id = self.generate_user_identifier(data.get('browser_fingerprint', ''))
            
            if not title or not artist or rating not in [1, -1]:
                self.send_json({'error': 'Title, artist, and rating (1 or -1) are required'}, 400)
                return
            
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            
            try:
                # Try to insert new rating
                cursor.execute(
                    '''INSERT INTO song_ratings (song_title, song_artist, song_album, user_identifier, rating) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (title, artist, album, user_id, rating)
                )
                conn.commit()
                
                self.send_json({'message': 'Rating submitted successfully'}, 201)
                
            except sqlite3.IntegrityError:
                # User already rated this song - update the rating
                cursor.execute(
                    '''UPDATE song_ratings 
                       SET rating = ?, created_at = CURRENT_TIMESTAMP 
                       WHERE song_title = ? AND song_artist = ? AND user_identifier = ?''',
                    (rating, title, artist, user_id)
                )
                conn.commit()
                
                self.send_json({'message': 'Rating updated successfully'}, 200)
            
            conn.close()
            
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def generate_user_identifier(self, browser_fingerprint):
        """Generate a persistent user identifier based on client characteristics"""
        import hashlib
        
        # Get client IP address
        client_ip = self.get_client_ip()
        
        # Get User-Agent
        user_agent = self.headers.get('User-Agent', '')
        
        # Get Accept-Language
        accept_language = self.headers.get('Accept-Language', '')
        
        # Get Accept-Encoding
        accept_encoding = self.headers.get('Accept-Encoding', '')
        
        # Combine all identifiers
        identifier_parts = [
            client_ip,
            user_agent,
            accept_language,
            accept_encoding,
            browser_fingerprint
        ]
        
        # Create a hash of all parts
        combined = '|'.join(identifier_parts)
        user_hash = hashlib.sha256(combined.encode()).hexdigest()
        
        return f"user_{user_hash[:16]}"
    
    def get_client_ip(self):
        """Get the real client IP address"""
        # Check for forwarded headers first (in case of proxy/load balancer)
        forwarded_for = self.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        real_ip = self.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        # Fall back to direct connection IP
        return self.client_address[0]

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), RadioCalioHandler) as httpd:
        print(f"Starting server at http://localhost:{PORT}")
        print("Available endpoints:")
        print("  GET  / - Server status")
        print("  GET  /api/users - All users")
        print("  GET  /api/posts - All posts")
        print("  GET  /api/posts/published - Published posts only")
        print("  POST /api/posts - Create new post")
        print("  POST /api/users - Create new user")
        print("\nTest in browser:")
        print(f"  http://localhost:{PORT}")
        print(f"  http://localhost:{PORT}/api/users")
        print(f"  http://localhost:{PORT}/api/posts")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")