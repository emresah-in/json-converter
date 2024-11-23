from flask import Flask, request, send_file
from json_converter import create_word_document, create_pdf_document
import json
from io import BytesIO

app = Flask(__name__)

@app.route('/')
def home():
    return {
        'message': 'JSON Converter API is running',
        'endpoints': {
            '/convert': 'POST - Convert JSON to Word/PDF documents',
        }
    }

@app.route('/convert', methods=['POST'])
def convert():
    try:
        # Get JSON data from request
        json_data = request.get_json()
        if not json_data:
            return {'error': 'No JSON data provided'}, 400

        # Get the desired output format (default to both)
        output_format = request.args.get('format', 'both').lower()
        if output_format not in ['word', 'pdf', 'both']:
            return {'error': 'Invalid format. Use "word", "pdf", or "both"'}, 400

        # Create documents in memory
        if output_format in ['word', 'both']:
            docx_buffer = BytesIO()
            create_word_document(json_data, docx_buffer)
            docx_buffer.seek(0)

        if output_format in ['pdf', 'both']:
            pdf_buffer = BytesIO()
            create_pdf_document(json_data, pdf_buffer)
            pdf_buffer.seek(0)

        # Return the appropriate file(s)
        if output_format == 'word':
            return send_file(
                docx_buffer,
                mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                as_attachment=True,
                download_name='document.docx'
            )
        elif output_format == 'pdf':
            return send_file(
                pdf_buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name='document.pdf'
            )
        else:  # both
            return {
                'message': 'Documents created successfully',
                'files': {
                    'word': '/download/word',
                    'pdf': '/download/pdf'
                }
            }

    except Exception as e:
        return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
