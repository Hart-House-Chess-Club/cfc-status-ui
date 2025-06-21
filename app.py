from flask import Flask, render_template, request, send_file, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename
import tempfile
from datetime import datetime
import requests
from csv import reader, writer
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configuration from environment variables
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-to-a-random-secret-key-for-production-213423jgasd')

# Application Configuration
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'csv').split(','))
MAX_FILE_SIZE = int(os.environ.get('MAX_FILE_SIZE', 16 * 1024 * 1024))  # 16MB default

# CFC API Configuration
CFC_API_BASE_URL = os.environ.get('CFC_API_BASE_URL', 'https://server.chess.ca/api/player/v1')
API_TIMEOUT = int(os.environ.get('API_TIMEOUT', 10))
API_RATE_LIMIT_DELAY = float(os.environ.get('API_RATE_LIMIT_DELAY', 0.1))

# Event Configuration
DEFAULT_EVENT_DATE = os.environ.get('DEFAULT_EVENT_DATE', '2025-06-16')
DEFAULT_CFC_ID_COLUMN = int(os.environ.get('DEFAULT_CFC_ID_COLUMN', 2))

# File Processing Configuration
MAX_PLAYERS_PER_FILE = int(os.environ.get('MAX_PLAYERS_PER_FILE', 1000))
PROCESSING_TIMEOUT = int(os.environ.get('PROCESSING_TIMEOUT', 300))

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_profile(cfcid):
    """Get player profile from CFC API"""
    URL = f"{CFC_API_BASE_URL}/{cfcid}"
    try:
        page = requests.get(URL, timeout=API_TIMEOUT)
        return page.json()
    except requests.RequestException as e:
        print(f"Error fetching profile for {cfcid}: {e}")
        return None


def process_csv_file(file_path, event_date, cfc_id_index=2):
    """Process the uploaded CSV file and add ratings"""
    id_list = []
    new_csv_rows = []
    
    with open(file_path, 'r') as f:
        csv_reader = reader(f)
        header = next(csv_reader)  # skip the header

        for row in csv_reader:
            print(f"Processing row: {row}")
            cfc_id = row[cfc_id_index] if len(row) > cfc_id_index else ''

            data_to_write = row[0:cfc_id_index + 1]  # keep the first few indices
            
            if cfc_id != '':  # if the id is not empty
                if cfc_id.lower() == "na" or cfc_id.lower() == "n/a":
                    data_to_write.append("0")
                    data_to_write += ["", "", ""] + row[cfc_id_index + 1:] if len(row) > cfc_id_index + 1 else ["", "", ""]
                    new_csv_rows.append(data_to_write)
                    continue

                if cfc_id in id_list: 
                    continue
                id_list.append(cfc_id)

                profile = get_profile(cfc_id)
                
                if profile is None or profile.get("player", {}).get("events") == []:
                    data_to_write.append("0")
                    data_to_write += ["", "", ""] + row[cfc_id_index + 1:] if len(row) > cfc_id_index + 1 else ["", "", ""]
                    new_csv_rows.append(data_to_write)
                    continue
                else:
                    # Use quick_rating (for rapid/blitz) or regular_rating (for standard)
                    rating = profile["player"].get("quick_rating", 0)
                    data_to_write.append(rating)

                # Check CFC membership expiry
                cfc_expiry = profile["player"].get("cfc_expiry", "")
                if not cfc_expiry.strip():
                    data_to_write.append("NA")
                else:
                    try:
                        expiry_date = datetime.strptime(cfc_expiry, '%Y-%m-%d')
                        if expiry_date < event_date:
                            data_to_write.append("Expired")
                        else:
                            data_to_write.append("Valid")
                    except ValueError:
                        data_to_write.append("NA")

                # Add additional player information
                data_to_write.append(profile["player"].get("fide_id", ""))
                data_to_write.append(profile["player"].get("name_first", ""))
                data_to_write.append(profile["player"].get("name_last", ""))
                
                # Add remaining columns from original row
                if len(row) > cfc_id_index + 4:
                    data_to_write += row[cfc_id_index + 4:]

                new_csv_rows.append(data_to_write)
                
                # Add a small delay to be respectful to the API
                time.sleep(API_RATE_LIMIT_DELAY)

    # Create new header
    new_header = header[0:cfc_id_index + 1] + ["CFC Rating", "CFC Membership", "FIDE ID", "First Name", "Last Name"]
    if len(header) > cfc_id_index + 4:
        new_header += header[cfc_id_index + 4:]
    
    # Sort by rating
    sorted_data = sort_by_rating(new_csv_rows, cfc_id_index + 1)
    
    return new_header, sorted_data


def sort_by_rating(data, ratings_index):
    """Sort data by ratings and update rankings"""
    # Filter out non-numeric ratings for sorting
    def get_rating(row):
        try:
            return int(row[ratings_index]) if row[ratings_index] and row[ratings_index] != "" else 0
        except (ValueError, IndexError):
            return 0
    
    data.sort(key=get_rating, reverse=True)

    rankings_number = 1
    for line in data:
        line[0] = rankings_number  # assume that the first value is the rankings
        rankings_number += 1

    return data


def write_to_file(filename, header, contents):
    """Write processed data to CSV file"""
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        write = writer(f)
        write.writerow(header)
        for content in contents:
            write.writerow(content)


@app.route('/')
def index():
    """Main page with file upload form"""
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(
        file_path,
        as_attachment=True,
        download_name=filename,
        mimetype='text/csv'
    )
    

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file selected')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        event_date_str = request.form.get('event_date')
        cfc_id_column = int(request.form.get('cfc_id_column', DEFAULT_CFC_ID_COLUMN))
        
        try:
            event_date = datetime.strptime(event_date_str, '%Y-%m-%d') if event_date_str else datetime.now()
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            flash('Processing your file... This may take a few minutes.')
            header, processed_data = process_csv_file(file_path, event_date, cfc_id_column)

            if len(processed_data) > MAX_PLAYERS_PER_FILE:
                flash(f'File too large! Maximum {MAX_PLAYERS_PER_FILE} players allowed. Your file has {len(processed_data)} players.')
                os.remove(file_path)
                return redirect(url_for('index'))

            output_filename = f"processed_{filename}"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
            write_to_file(output_path, header, processed_data)

            os.remove(file_path)

            flash(f'File processed successfully! {len(processed_data)} players processed.')
            return render_template(
                'index.html',
                headers=header,
                rows=processed_data,
                download_url=url_for('download_file', filename=output_filename)
            )

        except Exception as e:
            flash(f'Error processing file: {str(e)}')
            return redirect(url_for('index'))
    else:
        flash('Invalid file type. Please upload a CSV file.')
        return redirect(url_for('index'))


@app.route('/about')
def about():
    """About page explaining how to use the tool"""
    return render_template('about.html')


@app.route('/sample')
def download_sample():
    """Download sample CSV file"""
    sample_path = os.path.join(os.getcwd(), 'samples/sample_tournament.csv')
    return send_file(
        sample_path,
        as_attachment=True,
        download_name='sample_tournament.csv',
        mimetype='text/csv'
    )


@app.route('/sample-small')
def download_sample_small():
    """Download small sample CSV file for quick testing"""
    sample_path = os.path.join(os.getcwd(), 'samples/sample_small.csv')
    return send_file(
        sample_path,
        as_attachment=True,
        download_name='sample_small.csv',
        mimetype='text/csv'
    )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
