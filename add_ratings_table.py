#!/usr/bin/env python3
import sqlite3

def add_ratings_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Create ratings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS song_ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            song_title TEXT NOT NULL,
            song_artist TEXT NOT NULL,
            song_album TEXT,
            user_identifier TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating IN (-1, 1)),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(song_title, song_artist, user_identifier)
        )
    ''')
    
    # Create index for faster lookups
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_song_ratings_lookup 
        ON song_ratings (song_title, song_artist)
    ''')
    
    conn.commit()
    conn.close()
    print("Song ratings table created successfully!")

if __name__ == "__main__":
    add_ratings_table()