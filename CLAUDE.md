## Development
- Our default webserver for development and testing purpose is Express.js. You can start it using npm start.
- For the backend database, we are using SQLite and Flask.
- When starting the webserver, do not run "npm start" in the foreground, as that will block. Run it in the background 
if you must restart it. Also, assume that it is already running.

# Claude Code Configuration

## Commands

Add your commonly used commands here for easy reference:

```bash
# Database operations
python3 app.py  # Start Flask backend with SQLite
sqlite3 database.db  # Access SQLite database directly
sqlite3 database.db ".tables"  # List all tables
sqlite3 database.db ".schema"  # Show database schema

# Development commands
npm start  # Start Express.js webserver (run in background)
npm run dev
npm run build
npm run test
npm run lint
```

## Frontend

### Technology Stack
- **Core**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **Audio Streaming**: HLS.js library for HTTP Live Streaming
- **External CDN**: Google Fonts (Montserrat, Open Sans)

### Main Pages
- **index.html**: User management interface with CRUD operations
- **radio.html**: Live radio streaming player with metadata display

### Key Frontend Features

#### User Management (index.html)
- User registration form with validation
- Real-time user statistics dashboard
- Dynamic user list with pagination
- RESTful API integration for user operations
- Responsive design with custom CSS styling

#### Radio Player (radio.html)
- **Live Audio Streaming**: HLS.js powered radio player
- **Real-time Metadata**: Track info, artist, album, year display
- **Album Art**: Dynamic cover art loading with fallback
- **Interactive Controls**: Play/pause, volume, mute functionality
- **Song Rating System**: Thumbs up/down with persistent ratings
- **Previous Tracks**: Dynamic footer showing recently played songs
- **Responsive Layout**: Mobile-friendly design
- **Browser Fingerprinting**: Persistent user identification without cookies

#### Styling & UX
- Modern CSS3 with flexbox layouts
- Custom color scheme (greens, whites, grays)
- Smooth animations and transitions
- Professional typography with web fonts
- Mobile-responsive breakpoints

#### API Integration
- Fetch API for all HTTP requests
- Real-time metadata polling (10-second intervals)
- Rating persistence with browser fingerprinting
- Error handling with user feedback

## Project Notes

RadioCalio2 is a modern web radio application combining user management with live audio streaming. The frontend uses vanilla JavaScript for maximum compatibility while providing rich features like real-time metadata updates and interactive rating systems.