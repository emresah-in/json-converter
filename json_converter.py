import json
from docx import Document
from docx.shared import Pt, Inches
from fpdf import FPDF
import sys
from io import BytesIO

def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error reading JSON file: {str(e)}")
        return None

def create_word_document(json_data, output):
    doc = Document()
    
    # Add legal document styling
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.paragraph_format.line_spacing = 1.5
    
    # Add title
    if 'title' in json_data:
        doc.add_heading(json_data['title'], level=1)
    
    # Process sections if they exist
    if 'sections' in json_data:
        sections = json_data['sections']
    else:
        sections = json_data  # Treat the entire data as sections if no 'sections' key
    
    def process_sections(sections, level=1):
        for key, value in sections.items():
            if isinstance(value, dict):
                # Add section heading
                doc.add_heading(str(key), level=level)
                # Process subsections
                process_sections(value, level + 1)
            else:
                # Add section heading and content
                doc.add_heading(str(key), level=level)
                paragraph = doc.add_paragraph(str(value))
                paragraph.paragraph_format.first_line_indent = Inches(0.5)
                doc.add_paragraph()  # Add spacing
    
    # Process the sections
    process_sections(sections, level=2)
    
    try:
        # Save to file or BytesIO
        if isinstance(output, str):
            doc.save(output)
        else:
            doc.save(output)
    except Exception as e:
        print(f"Error creating Word document: {str(e)}")
        raise

def create_pdf_document(json_data, output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set default font
    pdf.set_font("Times", "", 12)
    
    # Add title
    if 'title' in json_data:
        pdf.set_font("Times", "B", 16)
        pdf.cell(0, 10, json_data['title'], ln=True)
        pdf.ln(5)
    
    # Process sections if they exist
    if 'sections' in json_data:
        sections = json_data['sections']
    else:
        sections = json_data  # Treat the entire data as sections if no 'sections' key
    
    def process_sections(sections, level=1):
        for key, value in sections.items():
            if isinstance(value, dict):
                # Add section heading
                pdf.set_font("Times", "B", 14 - level)
                pdf.cell(0, 10, str(key), ln=True)
                # Process subsections
                process_sections(value, level + 1)
            else:
                # Add section heading
                pdf.set_font("Times", "B", 14 - level)
                pdf.cell(0, 10, str(key), ln=True)
                # Add content
                pdf.set_font("Times", "", 12)
                pdf.multi_cell(0, 10, str(value))
                pdf.ln(5)
    
    # Process the sections
    process_sections(sections, level=1)
    
    try:
        # Save to file or BytesIO
        if isinstance(output, str):
            pdf.output(output)
        else:
            pdf.output(output)
    except Exception as e:
        print(f"Error creating PDF document: {str(e)}")
        raise

def convert_json(json_file_path, output_format="both"):
    # Read JSON file
    json_data = read_json_file(json_file_path)
    if not json_data:
        return False
    
    # Generate output file names
    file_base = json_file_path.rsplit('.', 1)[0]
    success = True
    
    # Convert based on requested format
    if output_format.lower() in ["both", "word"]:
        word_output = f"{file_base}.docx"
        try:
            create_word_document(json_data, word_output)
        except Exception as e:
            print(f"Error creating Word document: {str(e)}")
            success = False
    
    if output_format.lower() in ["both", "pdf"]:
        pdf_output = f"{file_base}.pdf"
        try:
            create_pdf_document(json_data, pdf_output)
        except Exception as e:
            print(f"Error creating PDF document: {str(e)}")
            success = False
    
    return success

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_converter.py <json_file_path> [output_format]")
        print("output_format can be: 'word', 'pdf', or 'both' (default)")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "both"
    
    convert_json(json_file_path, output_format)
