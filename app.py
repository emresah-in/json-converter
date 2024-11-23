from flask import Flask, request, send_file, make_response, url_for, send_from_directory
from json_converter import create_word_document, create_pdf_document
import json
from io import BytesIO
from flask_cors import CORS
import os
import uuid
from datetime import datetime, timedelta
import tempfile

app = Flask(__name__)
CORS(app)

# Use system temp directory
UPLOAD_FOLDER = tempfile.gettempdir()

# Store file information with expiration time
file_storage = {}

@app.route('/')
def home():
    return {
        'message': 'JSON Converter API is running',
        'endpoints': {
            '/convert': 'POST - Convert JSON to Word/PDF documents',
            '/download/<file_id>': 'GET - Download generated document'
        }
    }

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Get JSON data from request
        json_data = request.get_json()
        if not json_data:
            return {'error': 'No JSON data provided'}, 400

        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create Word document
        docx_buffer = BytesIO()
        create_word_document(json_data, docx_buffer)
        docx_buffer.seek(0)
        
        # Save file temporarily
        filename = f"{file_id}.docx"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(docx_buffer.getvalue())
        
        # Store file info with 15-minute expiration
        file_storage[file_id] = {
            'filepath': filepath,
            'expires_at': datetime.now() + timedelta(minutes=15)
        }
        
        # Generate download URL
        download_url = request.host_url.rstrip('/') + url_for('download_file', file_id=file_id)
        
        return {
            'message': 'Document created successfully',
            'download_url': download_url,
            'expires_in': '15 minutes'
        }

    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/download/<file_id>')
def download_file(file_id):
    # Check if file exists and hasn't expired
    file_info = file_storage.get(file_id)
    if not file_info:
        return {'error': 'File not found'}, 404
    
    if datetime.now() > file_info['expires_at']:
        # Clean up expired file
        try:
            os.remove(file_info['filepath'])
        except:
            pass
        del file_storage[file_id]
        return {'error': 'File has expired'}, 410
    
    try:
        return send_file(
            file_info['filepath'],
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name='document.docx'
        )
    except Exception as e:
        return {'error': str(e)}, 500

# Cleanup function for expired files
def cleanup_expired_files():
    current_time = datetime.now()
    expired_files = [fid for fid, info in file_storage.items() 
                    if current_time > info['expires_at']]
    
    for file_id in expired_files:
        try:
            os.remove(file_storage[file_id]['filepath'])
            del file_storage[file_id]
        except:
            pass

# Run cleanup periodically
@app.before_request
def before_request():
    cleanup_expired_files()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
