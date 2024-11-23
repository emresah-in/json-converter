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
    
    # Initialize section counters
    main_section_counter = 0  # For level 2 headers
    sub_section_counter = 0   # For level 3 headers
    
    def get_section_number(level):
        nonlocal main_section_counter, sub_section_counter
        if level == 2:
            # Increment main section counter
            main_section_counter += 1
            # Reset subsection counter
            sub_section_counter = 0
            return f"{main_section_counter}"
        elif level == 3:
            # Increment subsection counter
            sub_section_counter += 1
            return f"{main_section_counter}.{sub_section_counter}"
        return ""  # For level 1 (title)
    
    def process_json(data, level=1):
        for key, value in data.items():
            # Skip metadata fields
            if key in ['id', 'version', 'createdAt', 'updatedAt']:
                continue
                
            # Add heading based on nesting level
            if isinstance(value, dict):
                # Object titles are header 2
                section_num = get_section_number(2)
                doc.add_heading(f"{section_num} {str(key)}", level=2)
                process_json(value, level + 1)
            else:
                # Properties are header 3 with their values as paragraphs
                section_num = get_section_number(3)
                doc.add_heading(f"{section_num} {str(key)}", level=3)
                paragraph = doc.add_paragraph(str(value))
                paragraph.paragraph_format.first_line_indent = Inches(0.5)
                doc.add_paragraph()  # Add spacing between sections
    
    # Reset counters
    main_section_counter = 0
    sub_section_counter = 0
    
    # Add document title using the ID if available
    if 'id' in json_data:
        doc.add_heading(f"Document {json_data['id']}", level=1)
    
    # Add metadata section if available
    metadata = []
    for key in ['id', 'version', 'createdAt', 'updatedAt']:
        if key in json_data:
            metadata.append(f"{key}: {json_data[key]}")
    
    if metadata:
        section_num = get_section_number(2)
        doc.add_heading(f"{section_num} Document Metadata", level=2)
        for item in metadata:
            doc.add_paragraph(item)
        doc.add_paragraph()  # Add space after metadata
    
    process_json(json_data)
    
    try:
        # Save to file or BytesIO
        if isinstance(output, str):
            doc.save(output)
            print(f"Word document created successfully: {output}")
        else:
            doc.save(output)
    except Exception as e:
        print(f"Error creating Word document: {str(e)}")

def create_pdf_document(json_data, output):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Set default font
    pdf.set_font("Times", "", 12)
    
    # Initialize section counters
    main_section_counter = 0  # For level 2 headers
    sub_section_counter = 0   # For level 3 headers
    
    def get_section_number(level):
        nonlocal main_section_counter, sub_section_counter
        if level == 2:
            # Increment main section counter
            main_section_counter += 1
            # Reset subsection counter
            sub_section_counter = 0
            return f"{main_section_counter}"
        elif level == 3:
            # Increment subsection counter
            sub_section_counter += 1
            return f"{main_section_counter}.{sub_section_counter}"
        return ""  # For level 1 (title)
    
    def process_json(data, level=1):
        for key, value in data.items():
            # Skip metadata fields
            if key in ['id', 'version', 'createdAt', 'updatedAt']:
                continue
                
            if isinstance(value, dict):
                # Object titles are header 2
                section_num = get_section_number(2)
                pdf.set_font("Times", "B", 14)
                pdf.cell(0, 10, f"{section_num} {str(key)}", ln=True)
                process_json(value, level + 1)
            else:
                # Properties are header 3 with their values as paragraphs
                section_num = get_section_number(3)
                pdf.set_font("Times", "B", 12)
                pdf.cell(0, 10, f"{section_num} {str(key)}", ln=True)
                pdf.set_font("Times", "", 12)
                pdf.multi_cell(0, 10, str(value))
                pdf.ln(5)  # Add some space between sections
    
    # Reset counters
    main_section_counter = 0
    sub_section_counter = 0
    
    # Add document title using the ID if available
    if 'id' in json_data:
        pdf.set_font("Times", "B", 16)
        pdf.cell(0, 10, f"Document {json_data['id']}", ln=True)
        pdf.ln(5)
    
    # Add metadata section if available
    metadata = []
    for key in ['id', 'version', 'createdAt', 'updatedAt']:
        if key in json_data:
            metadata.append(f"{key}: {json_data[key]}")
    
    if metadata:
        section_num = get_section_number(2)
        pdf.set_font("Times", "B", 14)
        pdf.cell(0, 10, f"{section_num} Document Metadata", ln=True)
        pdf.set_font("Times", "", 12)
        for item in metadata:
            pdf.cell(0, 10, item, ln=True)
        pdf.ln(5)  # Add space after metadata
    
    process_json(json_data)
    
    try:
        # Save to file or BytesIO
        if isinstance(output, str):
            pdf.output(output)
            print(f"PDF document created successfully: {output}")
        else:
            pdf.output(output)
    except Exception as e:
        print(f"Error creating PDF document: {str(e)}")

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
