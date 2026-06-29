import fitz

def read_pdf(pdf_path):
    document = fitz.open(pdf_path)

    text = ""

    for page_num in range(len(document)):
        page = document.load_page(page_num)
        page_text = page.get_text("text")

        print(f"Page {page_num + 1} chars: {len(page_text)}")

        text += page_text + "\n"

    document.close()

    print("Total extracted chars:", len(text))

    return text.strip()