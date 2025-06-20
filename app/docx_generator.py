from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os
import re
import requests

UPLOAD_FOLDER = "uploads"
DOCX_FOLDER = "generated_docs"

def download_image(url, save_path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
        else:
            print(f"Erro ao baixar imagem: {url} - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"Erro ao baixar imagem: {url} - {str(e)}")
        return False

def generate_docx_from_result(task_id, task_result):
    os.makedirs(DOCX_FOLDER, exist_ok=True)
    doc = Document()

    # Estilo de fonte padrão
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    lines = task_result.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Títulos
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)

        # Listas
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:].strip(), style='List Bullet')

        # Imagens: Se a linha for uma URL de imagem (ex: https://...png ou jpg)
        elif re.match(r'^https?://.*\.(png|jpg|jpeg)$', line, re.IGNORECASE):
            try:
                image_filename = f"{task_id}_{os.path.basename(line)}"
                local_image_path = os.path.join(DOCX_FOLDER, image_filename)

                if download_image(line, local_image_path):
                    doc.add_picture(local_image_path, width=Inches(5))
                    last_paragraph = doc.paragraphs[-1]
                    last_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
            except Exception as e:
                doc.add_paragraph(f"[Erro ao inserir imagem: {str(e)}]")

        # Negritos inline (**texto**)
        elif "**" in line:
            paragraph = doc.add_paragraph()
            parts = re.split(r'(\*\*.*?\*\*)', line)
            for part in parts:
                run = paragraph.add_run()
                if part.startswith("**") and part.endswith("**"):
                    run.text = part[2:-2]
                    run.bold = True
                else:
                    run.text = part

        # Texto comum
        else:
            doc.add_paragraph(line)

    output_path = os.path.join(DOCX_FOLDER, f"{task_id}.docx")
    doc.save(output_path)
    return output_path
