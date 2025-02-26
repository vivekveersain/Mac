import PyPDF2

def extract_pages(pdf_path, page_range, output_path):
    # Open the original PDF
    with open(pdf_path, 'rb') as input_pdf:
        reader = PyPDF2.PdfReader(input_pdf)
        
        # Parse the page range
        start, end = map(int, page_range.split('-'))
        
        # Adjust to 0-based index for PyPDF2
        start -= 1
        end -= 1
        
        # Create a PdfWriter object to write the extracted pages
        writer = PyPDF2.PdfWriter()

        # Loop through the pages in the given range
        for page_num in range(start, end + 1):
            writer.add_page(reader.pages[page_num])

        # Write the extracted pages to a new PDF file
        with open(output_path, 'wb') as output_pdf:
            writer.write(output_pdf)
    
    print(f"Extracted pages {start + 1} to {end + 1} into '{output_path}'")

# Example usage
path = "/Users/vabarya/Downloads/dev/"
path = ""
pdf_path = path+"input.pdf"  # Replace with your input PDF file path
page_range = input("Page Range: ")
output_path = path+"extracted_pages.pdf"  # Output PDF file name

# Call the function to extract pages
extract_pages(pdf_path, page_range, output_path)
