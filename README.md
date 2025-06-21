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

1. **Download the sample file**: Visit the web app and click "Download Sample CSV" - choose either:
   - **Sample (10 players)** - `sample_small.csv` with mixed sections
   - **Full Sample (20 players)** - `sample_tournament.csv` with Crown section players
2. **Upload it**: Use the sample file to test the web application
3. **See the results**: The sample contains real CFC IDs that will demonstrate the rating lookup functionality

The sample files include:
- **sample_small.csv**: 10 players with Crown, U1800, and U1400 sections, including unrated players
- **sample_tournament.csv**: 20 tournament players from Crown section
- Examples of players with and without CFC memberships (marked as N/A)
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
docker run -d -p 5000:8080 --name cfc-app cfc-status-ui

# Access the application
open http://localhost:5000
```
