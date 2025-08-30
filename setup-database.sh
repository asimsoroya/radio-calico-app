#!/bin/bash

# Database setup script for local prototyping

echo "Setting up local SQLite database..."

# Install SQLite if not present (requires sudo)
if ! command -v sqlite3 &> /dev/null; then
    echo "Installing SQLite3..."
    sudo apt update && sudo apt install -y sqlite3
fi

# Create database with schema
echo "Creating database with schema..."
sqlite3 database.db < database.sql

echo "Database setup complete!"
echo "Database file: database.db"
echo "To connect: sqlite3 database.db"