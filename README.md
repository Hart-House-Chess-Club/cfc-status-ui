# CFC Rating Processor Web App

A Flask web application that processes tournament CSV files and automatically fetches current CFC (Chess Federation of Canada) ratings, membership status, and FIDE information for all players.

## Features

- **Upload CSV files** with tournament player data
- **Automatic rating lookup** from the official CFC API
- **Membership validation** with expiry date checking
- **FIDE ID retrieval** when available
- **Automatic ranking** by rating with updated positions
- **Download processed CSV** with all updated information
- **Modern web interface** with drag-and-drop file upload

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Setup

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your web browser** and go to:
   ```
   http://localhost:5000
   ```

## Usage

### CSV File Format

Your CSV file should have at least these columns:
- **Column 0**: Starting rank/position
- **Column 1**: Player name  
- **Column 2**: CFC ID (default location)

Example:
```csv
Rank,Player Name,CFC ID,Additional Info
1,John Smith,123456,Club Name
2,Jane Doe,789012,Another Club
3,Bob Wilson,NA,Unrated Player
```

### Special CFC ID Values
- `NA` or `N/A` - Player without CFC membership
- Empty cell - Will be skipped
- Numeric ID - Will be looked up in CFC database

### Configuration Options

- **Event Date**: Set to your tournament date for membership validation
- **CFC ID Column Index**: Specify which column contains CFC IDs (0-based index)

### Output

The processed file will include these additional columns:
- **CFC Rating**: Current CFC quick rating
- **CFC Membership**: Valid/Expired/NA status
- **FIDE ID**: International rating system ID
- **First Name**: From CFC database
- **Last Name**: From CFC database

Players will be automatically sorted by rating (highest to lowest) and rankings updated.

## Quick Start with Sample File

To test the application immediately:

1. **Download the sample file**: Visit the web app and click "Download Sample CSV" or use the file `sample_tournament.csv`
2. **Upload it**: Use the sample file to test the web application
3. **See the results**: The sample contains real CFC IDs that will demonstrate the rating lookup functionality

The sample file includes:
- 60 tournament players with various rating levels
- Mix of different sections (Crown, U1800, U1400)
- Examples of players with and without CFC memberships
- Real CFC IDs for testing the API integration

## Deployment Options

### Local Development
```bash
python app.py
```

### Docker Deployment

#### Quick Start with Docker
```bash
# Build the Docker image
docker build -t cfc-status-ui .

# Run the container
docker run -d -p 8080:8080 --name cfc-app cfc-status-ui

# Access the application
open http://localhost:8080
```

#### Docker Commands Reference

**Build the image:**
```bash
docker build -t cfc-status-ui .
```

**Run in development mode:**
```bash
# Run with logs visible
docker run -p 8080:8080 cfc-status-ui

# Run in background (detached)
docker run -d -p 8080:8080 --name cfc-app cfc-status-ui
```

**Manage the container:**
```bash
# Check container status
docker ps

# View logs
docker logs cfc-app

# Stop the container
docker stop cfc-app

# Remove the container
docker rm cfc-app

# Remove the image
docker rmi cfc-status-ui
```

**Run with environment variables:**
```bash
docker run -d -p 8080:8080 \
  -e FLASK_ENV=production \
  -e FLASK_DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  --name cfc-app cfc-status-ui
```

**Run with volume for persistent uploads:**
```bash
docker run -d -p 8080:8080 \
  -v $(pwd)/uploads:/app/uploads \
  --name cfc-app cfc-status-ui
```

#### Docker Compose (Optional)

Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  cfc-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=False
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
```

Then run:
```bash
# Start the application
docker-compose up -d

# Stop the application
docker-compose down
```

### Production Deployment

#### Option 1: Docker Production (Recommended)

Docker is an excellent choice for production deployment, offering:
- **Consistency**: Same environment across development, testing, and production
- **Scalability**: Easy to scale with orchestrators like Kubernetes or Docker Swarm
- **Isolation**: Application runs in its own container with all dependencies
- **Portability**: Deploy anywhere that supports Docker

**Production Docker Setup:**

1. **Build optimized production image:**
   ```bash
   docker build -t cfc-status-ui:latest .
   ```

2. **Run with production settings:**
   ```bash
   docker run -d \
     --name cfc-app-prod \
     -p 80:8080 \
     -e FLASK_ENV=production \
     -e FLASK_DEBUG=False \
     -e SECRET_KEY=your-secure-secret-key \
     -e API_RATE_LIMIT_DELAY=0.5 \
     --restart unless-stopped \
     cfc-status-ui:latest
   ```

## Environment Configuration

### Quick Setup
1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Generate secure production environment:**
   ```bash
   python generate_env.py production
   ```

3. **Validate your configuration:**
   ```bash
   python validate_env.py
   ```

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for sessions | - | ✅ |
| `FLASK_ENV` | Environment (development/production) | development | ✅ |
| `FLASK_DEBUG` | Debug mode (True/False) | True | ❌ |
| `API_RATE_LIMIT_DELAY` | Delay between API calls (seconds) | 0.1 | ❌ |
| `MAX_FILE_SIZE` | Maximum upload size (bytes) | 16777216 | ❌ |
| `MAX_PLAYERS_PER_FILE` | Maximum players per file | 1000 | ❌ |
| `CFC_API_BASE_URL` | CFC API endpoint | https://server.chess.ca/api/player/v1 | ❌ |
| `API_TIMEOUT` | API request timeout (seconds) | 10 | ❌ |

### Security Notes
- Never commit `.env` files to version control
- Use `generate_env.py` to create secure secret keys
- Set `FLASK_DEBUG=False` in production
- Use longer `API_RATE_LIMIT_DELAY` in production (0.5 seconds recommended)

## Security Notes

- Change the `secret_key` in `app.py` for production
- Consider adding rate limiting for production use
- The application respects CFC API rate limits with built-in delays

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure all requirements are installed with `pip install -r requirements.txt`

2. **Player not found**: CFC ID may be incorrect or player not in CFC database

3. **Processing takes long**: Normal for large files due to API rate limiting (1-2 seconds per player)

4. **File upload fails**: Check file size (max 16MB) and ensure it's a valid CSV file

### Getting Help

- Check the "About" page in the web app for detailed usage instructions
- Ensure your CSV file follows the required format
- Verify CFC IDs are correct and properly formatted

## Technical Details

- **Framework**: Flask (Python web framework)
- **Frontend**: Bootstrap 5 with modern responsive design
- **File Processing**: Native Python CSV module
- **API**: CFC (Chess Federation of Canada) public API
- **File Upload**: Werkzeug secure filename handling

## Contributing

This tool was built for Canadian chess tournament organizers. Feel free to submit issues or improvements!

