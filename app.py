from flask import Flask, request, send_file, make_response, url_for, send_from_directory
from json_converter import create_word_document, create_pdf_document
import json
from io import BytesIO
from flask_cors import CORS
import os
import uuid
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Use system temp directory
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'generated_files')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Store file information
file_storage = {}

@app.route('/')
def home():
    return {
        'message': 'JSON Converter API is running',
        'endpoints': {
            '/convert': 'POST - Convert JSON to Word/PDF documents',
            '/download/<file_id>': 'GET - Download generated document',
            '/delete/<file_id>': 'DELETE - Delete a generated document',
            '/files': 'GET - List all generated files'
        }
    }

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Log raw request data
        raw_data = request.get_data().decode('utf-8')
        logger.debug(f"Raw request data: {raw_data[:200]}...")
        
        # Log content type
        content_type = request.headers.get('Content-Type')
        logger.debug(f"Content-Type: {content_type}")
        
        # Try to get JSON data
        try:
            json_data = request.get_json()
            logger.debug(f"Parsed JSON data type: {type(json_data)}")
            logger.debug(f"Parsed JSON data: {str(json_data)[:200]}...")
        except Exception as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return {'error': f'JSON parsing error: {str(e)}'}, 400

        if not json_data:
            logger.error("No JSON data provided")
            return {'error': 'No JSON data provided'}, 400

        # Generate unique file ID
        file_id = str(uuid.uuid4())
        logger.debug(f"Generated file ID: {file_id}")
        
        try:
            # Create Word document
            docx_buffer = BytesIO()
            logger.debug("Creating Word document...")
            create_word_document(json_data, docx_buffer)
            docx_buffer.seek(0)
            logger.debug("Word document created successfully")
            
            # Save file permanently
            filename = f"{file_id}.docx"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(docx_buffer.getvalue())
            logger.debug(f"Document saved to {filepath}")
            
            # Store file info
            file_storage[file_id] = {
                'filepath': filepath,
                'filename': filename,
                'created_at': json_data.get('createdAt', 'Not specified')
            }
            
            # Generate download URL
            download_url = request.host_url.rstrip('/') + url_for('download_file', file_id=file_id)
            logger.debug(f"Download URL generated: {download_url}")
            
            return {
                'message': 'Document created successfully',
                'file_id': file_id,
                'download_url': download_url
            }

        except Exception as e:
            logger.error(f"Document creation error: {str(e)}")
            return {'error': str(e)}, 500

    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/download/<file_id>')
def download_file(file_id):
    logger.debug(f"Download requested for file ID: {file_id}")
    # Check if file exists
    file_info = file_storage.get(file_id)
    if not file_info or not os.path.exists(file_info['filepath']):
        logger.error(f"File not found: {file_id}")
        return {'error': 'File not found'}, 404
    
    try:
        return send_file(
            file_info['filepath'],
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=file_info['filename']
        )
    except Exception as e:
        logger.error(f"Error sending file: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/delete/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    logger.debug(f"Delete requested for file ID: {file_id}")
    # Check if file exists
    file_info = file_storage.get(file_id)
    if not file_info:
        logger.error(f"File not found: {file_id}")
        return {'error': 'File not found'}, 404
    
    try:
        # Delete the file
        if os.path.exists(file_info['filepath']):
            os.remove(file_info['filepath'])
        # Remove from storage
        del file_storage[file_id]
        return {'message': f'File {file_id} deleted successfully'}
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        return {'error': str(e)}, 500

@app.route('/files')
def list_files():
    try:
        files = []
        for file_id, info in file_storage.items():
            if os.path.exists(info['filepath']):
                files.append({
                    'file_id': file_id,
                    'filename': info['filename'],
                    'created_at': info['created_at'],
                    'download_url': request.host_url.rstrip('/') + url_for('download_file', file_id=file_id)
                })
        return {'files': files}
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
