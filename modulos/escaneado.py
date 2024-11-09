import PyPDF2

try:
    pdf_file_obj = open('modulos/Descargas/IFA_DFZ-2024-344-VIII-NE_FABRICA NESTLE-LOS ANGELES.pdf', 'rb') # abrir documento en lectura binaria
    pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
    num_pages = len(pdf_reader.pages)
    content = ""
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        content += page.extract_text()
    print(content)
except FileNotFoundError:
    print("Error: El archivo no se encontró.")