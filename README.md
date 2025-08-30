# Local Database Setup

## Quick Start

1. Run the setup script:
   ```bash
   ./setup-database.sh
   ```

2. Connect to the database:
   ```bash
   sqlite3 database.db
   ```

## Database Details

- **Type**: SQLite3 (perfect for local prototyping)
- **File**: `database.db` 
- **Schema**: Defined in `database.sql`

## Sample Tables

- `users` - User accounts with email, password, name
- `posts` - Content posts linked to users

## Usage Examples

```sql
-- View all users
SELECT * FROM users;

-- View published posts
SELECT p.title, u.name as author 
FROM posts p 
JOIN users u ON p.author_id = u.id 
WHERE p.published = 1;

-- Add a new user
INSERT INTO users (email, password_hash, name) 
VALUES ('newuser@example.com', 'hashed_password', 'New User');
```

## Configuration

Copy `.env.example` to `.env` and adjust database settings as needed.