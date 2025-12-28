# Team Activity Tracker

A Django-based chatbot application that tracks and reports team member activity from Jira and GitHub. This application provides a natural language interface to query team member contributions, pull requests, commits, and Jira issues.

## Features

- **Natural Language Query Interface**: Ask questions about team member activity using plain English
- **Jira Integration**: Query Jira issues assigned to team members
- **GitHub Integration**: Track commits, pull requests, and repository contributions
- **Intent Recognition**: Automatically detects query intent (Jira, GitHub, or both)
- **Time-based Filtering**: Support for time-based queries (today, this week, this month, recent)
- **Graceful Error Handling**: Retry logic with exponential backoff for API failures
- **Modern Web UI**: Dark-themed, responsive chat interface

## Supported Team Members

The application currently supports the following team members:
- John
- Sarah
- Mike

## Query Examples

The chatbot understands various query formats:

- `"What is John working on?"` - Returns both Jira and GitHub activity
- `"Show me Sarah's Jira tickets"` - Returns only Jira issues
- `"What are Mike's GitHub commits this week?"` - Returns recent commits
- `"List John's pull requests"` - Returns active pull requests
- `"Show Sarah's repositories"` - Returns recently contributed repositories
- `"What is Mike doing on GitHub?"` - Returns GitHub activity summary

## Architecture

### Backend
- **Framework**: Django 4.2.27 with Django REST Framework
- **Database**: SQLite (default)
- **API Clients**: 
  - GitHub API v3 (REST)
  - Jira API v3 (REST)
- **Retry Logic**: Tenacity library for resilient API calls

### Frontend
- **Static HTML/CSS/JavaScript**: Vanilla JavaScript with modern CSS
- **UI Theme**: Dark mode with gradient backgrounds
- **Communication**: RESTful API calls to backend

### Project Structure

```
team-activity-tracker/
├── chatbot/              # Main application
│   ├── github_client.py  # GitHub API integration
│   ├── jira_client.py    # Jira API integration
│   ├── query_parser.py   # Natural language parsing
│   ├── response_generator.py  # Response formatting
│   ├── views.py          # API endpoints
│   └── serializers.py    # Request validation
├── static/               # Frontend assets
│   ├── index.html        # Main UI
│   ├── script.js         # Frontend logic
│   └── style.css         # Styling
├── team_activity_tracker/  # Django project settings
└── requirements.txt      # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip
- Access to Jira and GitHub APIs (with appropriate credentials)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd team-activity-tracker
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Create a `.env` file in the project root with the following variables:

   ```env
   # Jira Configuration
   JIRA_ACCOUNT_ID=your_jira_account_id
   JIRA_EMAIL=your_email@example.com
   JIRA_API_TOKEN=your_jira_api_token
   JIRA_BASE_URL=https://your-domain.atlassian.net

   # GitHub Configuration
   GITHUB_BASE_URL=https://api.github.com
   ```

   **Note**: For GitHub, you may need a personal access token if you hit rate limits. Add it to the request headers in `github_client.py` if needed.

5. **Configure user mappings**

   Update `chatbot/constants.py` to map team member names to their actual Jira account IDs and GitHub usernames:

   ```python
   JIRA_USERNAME_TO_ACCOUNT_ID_MAP = {
       "john": "account-id-1",
       "sarah": "account-id-2",
       "mike": "account-id-3",
   }

   GITHUB_USER_ALIAS_TO_USERNAME_MAP = {
       "john": "github-username-1",
       "sarah": "github-username-2",
       "mike": "github-username-3",
   }
   ```

6. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

7. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open your browser and navigate to `http://localhost:8000`
   - The chat interface should be available

## API Documentation

### Endpoints

#### POST `/api/chat/`

Send a natural language query about team member activity.

**Request Body:**
```json
{
  "message": "What is John working on?"
}
```

**Response (Success):**
```json
{
  "success": true,
  "data": "John is working on 3 JIRA issue(s):\n- PROJ-123 (In Progress): Fix login bug\n- PROJ-124 (To Do): Add new feature\n\nRecent GitHub commits by John:\n- org/repo: Fixed authentication issue"
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "User not found",
  "errors": {}
}
```

#### GET `/ping`

Health check endpoint.

**Response:**
```json
{
  "success": true,
  "data": "pong"
}
```

### Query Intent Detection

The system automatically detects intent from the query:

- **JIRA_ONLY**: Queries containing "jira", "ticket", or "issue"
- **GITHUB_COMMITS**: Queries containing "commit" or "commits"
- **GITHUB_PRS**: Queries containing "pull request", "pr", or "prs"
- **GITHUB_REPOS**: Queries containing "repo", "repos", "repository", or "repositories"
- **GITHUB_ONLY**: Queries containing "github"
- **BOTH**: Default fallback for general queries

### Time Filtering

The parser recognizes time-based queries:
- `"today"` → 1 day
- `"this week"` → 7 days
- `"this month"` → 30 days
- `"recent"` or `"these days"` → 3 days

## Error Handling

The application implements robust error handling:

- **Retry Logic**: Automatic retries (up to 3 attempts) for 5xx HTTP errors
- **Graceful Degradation**: If one service fails, the other continues to work
- **Service Unavailable**: Custom exceptions for GitHub and Jira service failures

## Deployment

The application is configured for deployment on Render.com (see `render.yaml`).


## Technologies Used

- **Django 4.2.27**: Web framework
- **Django REST Framework 3.16.1**: API framework
- **Requests 2.32.5**: HTTP client
- **Tenacity 9.1.2**: Retry library
- **WhiteNoise 6.11.0**: Static file serving
- **Gunicorn 21.2.0**: WSGI server

## Limitations

- Currently supports only three hardcoded team members (John, Sarah, Mike)
- User mappings must be manually configured in `constants.py`
- GitHub API rate limits may apply (60 requests/hour for unauthenticated requests)

## Future Enhancements

Potential improvements:
- Dynamic user discovery from Jira/GitHub
- Caching for API responses
- Support for more team members
- Advanced natural language processing
- Webhook support for real-time updates
