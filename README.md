# Instagram Profiles Scraper

A scalable Instagram profile scraper with parallel processing, session management, and a user-friendly Streamlit interface.

## Features

- 🚀 Parallel processing with multiple worker threads
- 🔄 Smart session management and rotation
- 📊 Real-time progress tracking and statistics
- 🎯 Targeted follower data collection
- 💾 MySQL database integration
- 🌐 Proxy support
- 📱 User-friendly Streamlit interface

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/instagram-profiles-scraper.git
cd instagram-profiles-scraper
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
- Copy `.env.example` to `.env`
- Update the following variables:
  ```
  MYSQL_DB_HOST=your_mysql_host
  MYSQL_DB_USER=your_mysql_user
  MYSQL_DB_PASSWORD=your_mysql_password
  MYSQL_SYSTEM_DB_NAME=your_database_name
  ```

5. Initialize the database:
```bash
python scripts/init_db.py
```

## Usage

1. Start the Streamlit interface:
```bash
streamlit run app.py
```

2. Navigate to the web interface (usually http://localhost:8501)

3. Use the interface to:
- Start new scraping jobs
- Monitor active sessions
- View and filter follower data
- Export data to CSV
- Configure scraping settings

## Architecture

The scraper consists of several key components:

1. **Worker Pool**: Manages multiple worker threads for parallel processing
2. **Session Manager**: Handles Instagram session rotation and challenge detection
3. **Database Layer**: Stores account data, followers, and session information
4. **Streamlit UI**: Provides a user-friendly interface for control and monitoring

## Development

1. Run tests:
```bash
python -m pytest tests/
```

2. Format code:
```bash
black .
isort .
```

3. Type checking:
```bash
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 