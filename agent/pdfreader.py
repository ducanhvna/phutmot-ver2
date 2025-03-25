import os
from PyPDF2 import PdfReader
import tabula
import fitz  # PyMuPDF

def extract_pdf_content(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".pdf"):
            pdf_name = os.path.splitext(file)[0]
            pdf_output_dir = os.path.join(output_dir, pdf_name)
            os.makedirs(pdf_output_dir, exist_ok=True)
            
            pdf_path = os.path.join(input_dir, file)
            reader = PdfReader(pdf_path)
            
            # Extract text
            text_output_path = os.path.join(pdf_output_dir, "text.txt")
            with open(text_output_path, "w", encoding="utf-8") as text_file:
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_blocks = text.split("\n\n")
                        for block in text_blocks:
                            text_file.write(block.strip() + "\n")
            
            # Extract tables
            table_count = 1
            tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True, lattice=True)
            for table in tables:
                table_output_path = os.path.join(pdf_output_dir, f"table_{table_count}.csv")
                table.to_csv(table_output_path, index=False)
                table_count += 1
            
            # Extract images
            doc = fitz.open(pdf_path)
            image_count = 1
            for page_num in range(len(doc)):
                page = doc[page_num]
                for img_index, img in enumerate(page.get_images(full=True), start=1):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    image_output_path = os.path.join(pdf_output_dir, f"image_{image_count}.{image_ext}")
                    with open(image_output_path, "wb") as image_file:
                        image_file.write(image_bytes)
                    image_count += 1

# Paths
input_directory = "input"
output_directory = "output"

# Call the function
extract_pdf_content(input_directory, output_directory)
