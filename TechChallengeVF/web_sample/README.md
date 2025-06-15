# Modern Dashboard

A modern, interactive web dashboard built with HTML, CSS, and JavaScript that showcases various components commonly used in web applications.

## Features

### 🗓️ Calendar Component
- Interactive calendar using FullCalendar library
- Displays events loaded from a local JSON file
- Allows selecting single dates or date ranges
- Shows event details when an event is clicked
- Displays event details in a side panel and modal

### 📄 Results Block with Pagination
- Loads dummy data from a local JSON file
- Displays results in card format
- Includes pagination controls
- Allows changing the number of items per page (5, 10, 20)
- Dynamically updates the visible items using frontend logic

### 🔗 Dummy File Links Section
- Displays downloadable/viewable files with metadata
- Loads file information from a local JSON file
- Shows appropriate icons based on file type
- Allows downloading or viewing files (when supported)
- Displays file size in a human-readable format

## Project Structure

```
modern-dashboard/
├── css/
│   └── styles.css           # Main stylesheet
├── data/
│   ├── events.json          # Calendar events data
│   ├── files.json           # File metadata
│   └── results.json         # Results data for pagination
├── js/
│   ├── calendar.js          # Calendar component logic
│   ├── files.js             # Files section logic
│   ├── main.js              # Main application logic
│   └── results.js           # Results and pagination logic
└── index.html               # Main HTML file
```

## Setup and Installation

1. Clone or download this repository
2. No build process is required - this is a static website
3. Open `index.html` in a modern web browser
4. Alternatively, serve the files using a local web server:
   - Using Python: `python -m http.server`
   - Using Node.js: `npx serve`

## Technologies Used

- **HTML5** - Structure and content
- **CSS3** - Styling and responsive design
- **JavaScript (ES6+)** - Functionality and interactivity
- **Bootstrap 5** - UI framework for responsive design
- **FullCalendar** - Calendar component
- **Fetch API** - Loading JSON data

## Browser Compatibility

This dashboard is designed to work in modern browsers that support ES6+ features:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Data Sources

All data is loaded from local JSON files:
- `events.json` - Calendar events
- `results.json` - Paginated results
- `files.json` - File metadata for the downloads section

## License

This project is available for educational and demonstration purposes.