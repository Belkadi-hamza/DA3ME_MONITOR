# Da3me Monitor

A Moodle course activity monitor that continuously tracks new quizzes, PDFs, and assignments on the Da3me platform.

## Features

✨ **Continuous Monitoring** - Periodically checks for new course activities  
📧 **State Persistence** - Tracks seen items to avoid duplicate notifications  
🌐 **Web API** - Flask-based REST API for programmatic access  
🔍 **Multi-Activity Support** - Monitors quizzes, PDFs, assignments, and more  
📊 **Section Organization** - Groups activities by course section  
🤖 **Automated Login** - Uses Selenium for automatic Moodle authentication

## Project Structure

```
da3me-monitor/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Entry point (CLI or server mode)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # Global driver lifecycle
│   │   └── routes.py           # Flask API endpoints
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py             # Moodle authentication
│   │   ├── config.py           # Configuration from .env
│   │   ├── parser.py           # HTML parsing
│   │   └── scraper.py          # Course data extraction
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic data models
│   ├── services/
│   │   ├── __init__.py
│   │   └── course_service.py   # State management & tracking
│   └── utils/
│       ├── __init__.py
│       └── logging.py          # Logging setup
├── .env                        # Configuration (not in repo)
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

### Prerequisites

- Python 3.8+
- Google Chrome or Chromium
- pip package manager

### Setup

1. **Clone or extract the project:**
   ```bash
   cd da3me-monitor
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   ```bash
   cp .env.example .env
   ```

5. **Configure credentials in `.env`:**
   ```env
   # Da3me Configuration
   DA3ME_BASE_URL=https://da3me.ma
   DA3ME_LOGIN_URL=https://da3me.ma/login/index.php
   DA3ME_COURSE_URL=https://da3me.ma/course/view.php?id=123

   # Credentials (IMPORTANT: Verify these work by logging in manually)
   USERNAME=your_username_or_email
   PASSWORD=your_password

   # Monitoring
   CHECK_INTERVAL_SECONDS=3600

   # Server
   HOST=0.0.0.0
   PORT=5000
   DEBUG=false
   ```

## Usage

### Mode 1: API Server (Default)

Run as a Flask web server:

```bash
python -m app.main --mode server
```

**Endpoints:**

- `GET /api/course` - Get all sections with activities
- `GET /api/health` - Health check

Example:
```bash
curl http://localhost:5000/api/course
```

### Mode 2: CLI Monitoring

Run continuous monitoring with console logging:

```bash
python -m app.main --mode cli
```

This will:
1. Log in to Da3me
2. Check for new activities every 3600 seconds (configurable)
3. Log findings to console
4. Persist state to `state.json`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `USERNAME` | Moodle username or email | - |
| `PASSWORD` | Moodle password | - |
| `DA3ME_COURSE_URL` | Full course URL to monitor | - |
| `CHECK_INTERVAL_SECONDS` | Monitoring interval in seconds | 3600 |
| `STATE_FILE` | State persistence file | state.json |
| `HOST` | Server bind address | 0.0.0.0 |
| `PORT` | Server port | 5000 |
| `DEBUG` | Flask debug mode | false |

### State File

The application tracks seen activities in `state.json`:

```json
{
  "sections": {
    "section_123": {
      "title": "Week 1",
      "quizzes": {
        "https://...": {
          "name": "Quiz 1",
          "first_seen": "2026-06-03T...",
          "last_seen": "2026-06-03T..."
        }
      },
      "pdfs": {},
      "assignments": {}
    }
  }
}
```

## Troubleshooting

### Login Fails with "Invalid login, please try again"

**Solution:**
1. Verify credentials work by logging in manually to https://da3me.ma
2. Check that `USERNAME` and `PASSWORD` in `.env` match exactly
3. Consider using your email address instead of username
4. Check if your account is disabled or needs activation

### Chrome Driver Not Found

**Solution:**
```bash
pip install --upgrade webdriver-manager
```

The app automatically downloads the correct Chrome driver version.

### Timeout Waiting for Login Form

**Solution:**
1. Check internet connection
2. Verify Da3me is accessible: `https://da3me.ma/login/index.php`
3. Try increasing timeout in `auth.py` (default: 20 seconds)

### No New Activities Detected

- First run: State is empty, so all current items are added to state
- Subsequent runs: Only genuinely new items trigger detection
- Check `state.json` to see what's been tracked

## API Examples

### Get Course Activities

```bash
curl http://localhost:5000/api/course
```

Response:
```json
{
  "status": "ok",
  "course_url": "https://da3me.ma/course/view.php?id=123",
  "sections": [
    {
      "section_id": "1",
      "section_title": "Week 1",
      "quizzes": [
        {
          "name": "Quiz 1",
          "url": "https://da3me.ma/mod/quiz/view.php?id=456"
        }
      ],
      "pdfs": [],
      "assignments": []
    }
  ]
}
```

### Health Check

```bash
curl http://localhost:5000/api/health
```

Response:
```json
{
  "status": "alive"
}
```

## Development

### Adding New Activity Types

1. Update parser in `app/core/parser.py` → add to `classify_activity_by_url()`
2. Update CourseService in `app/services/course_service.py` → add tracking
3. Update Scraper in `app/core/scraper.py` → add to returned sections

### Modifying State Schema

Edit `app/services/course_service.py` to change how activities are stored and compared.

### Extending API

Add new routes in `app/api/routes.py` following Flask conventions.

## Requirements

See `requirements.txt` for full list. Key dependencies:

- `selenium>=4.0` - Browser automation
- `beautifulsoup4` - HTML parsing
- `webdriver-manager` - Chrome driver management
- `flask` - Web framework
- `pydantic` - Data validation
- `python-dotenv` - Environment configuration

## Logs

Logs are printed to console with timestamps and severity levels:

```
2026-06-03 14:30:15 - app.main - INFO - 🚀 Logging in once...
2026-06-03 14:30:18 - app.core.auth - INFO - ✅ Login successful
2026-06-03 14:30:20 - app.core.scraper - INFO - 📚 Extracted 8 sections with activities
```

## License

Educational project for course monitoring.

## Support

For issues:
1. Check logs for error messages
2. Review `.env` configuration
3. Test credentials manually
4. Check project structure matches this README

---

**Last Updated:** June 3, 2026
