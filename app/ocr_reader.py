import fitz  # PyMuPDF
import os

UPLOAD_FOLDER = "uploads"

def extract_text_from_pdf(task_id_files):
    folder_path = os.path.join(UPLOAD_FOLDER, task_id_files)
    if not os.path.exists(folder_path):
        return f"Erro: Pasta '{folder_path}' não encontrada."

    extracted_texts = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            try:
                doc = fitz.open(file_path)
                pdf_text = ""
                for page_num in range(doc.page_count):
                    page = doc.load_page(page_num)
                    pdf_text += page.get_text("text") + "\n\n"
                extracted_texts.append(f"📄 Conteúdo extraído de {filename}:\n\n{pdf_text.strip()}")
            except Exception as e:
                extracted_texts.append(f"Erro ao processar {filename}: {str(e)}")

    if not extracted_texts:
        return "Nenhum PDF com texto encontrado para leitura."

    return "\n\n".join(extracted_texts)
