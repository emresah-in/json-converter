from flask import Flask, request, send_file, make_response
from json_converter import create_word_document, create_pdf_document
import json
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        if output_format == 'word':
            docx_buffer = BytesIO()
            create_word_document(json_data, docx_buffer)
            docx_buffer.seek(0)
            
            response = make_response(docx_buffer.getvalue())
            response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            response.headers['Content-Disposition'] = 'attachment; filename=document.docx'
            return response

        elif output_format == 'pdf':
            pdf_buffer = BytesIO()
            create_pdf_document(json_data, pdf_buffer)
            pdf_buffer.seek(0)
            
            response = make_response(pdf_buffer.getvalue())
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=document.pdf'
            return response

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
