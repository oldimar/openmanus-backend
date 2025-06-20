from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, Inches
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
    temp_image_folder = os.path.join(DOCX_FOLDER, f"images_{task_id}")
    os.makedirs(temp_image_folder, exist_ok=True)

    doc = Document()

    # Estilo padrão da fonte
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    lines = task_result.split("\n")
    for line in lines:
        line = line.strip()
        if not line:
            doc.add_paragraph()  # Adiciona uma linha em branco real entre os blocos
            continue

        # Cabeçalhos
        if line.startswith("# "):
            heading = doc.add_heading(line[2:].strip(), level=1)
            heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        elif line.startswith("## "):
            heading = doc.add_heading(line[3:].strip(), level=2)
            heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        elif line.startswith("### "):
            heading = doc.add_heading(line[4:].strip(), level=3)
            heading.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT

        # Listas com espaçamento
        elif line.startswith("- ") or line.startswith("* "):
            para = doc.add_paragraph(line[2:].strip(), style='List Bullet')
            para.paragraph_format.space_after = Pt(6)

        # Imagens via URL Markdown ![](url)
        elif re.match(r'!\[.*\]\(http.*\)', line):
            match = re.match(r'!\[(.*?)\]\((http.*?)\)', line)
            if match:
                alt_text = match.group(1)
                image_url = match.group(2)
                image_filename = os.path.join(temp_image_folder, os.path.basename(image_url).split("?")[0])
                if download_image(image_url, image_filename):
                    try:
                        doc.add_picture(image_filename, width=Inches(5))
                        last_paragraph = doc.paragraphs[-1]
                        last_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        doc.add_paragraph(alt_text).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    except Exception as e:
                        doc.add_paragraph(f"[Erro ao adicionar imagem: {str(e)}]")

        # Negrito real: **texto**
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
            paragraph.paragraph_format.space_after = Pt(8)

        # Texto comum
        else:
            para = doc.add_paragraph(line)
            para.paragraph_format.space_after = Pt(8)

    output_path = os.path.join(DOCX_FOLDER, f"{task_id}.docx")
    doc.save(output_path)
    return output_path
