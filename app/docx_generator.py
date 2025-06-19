from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt
import os
import re

UPLOAD_FOLDER = "uploads"
DOCX_FOLDER = "generated_docs"

def generate_docx_from_result(task_id, task_result):
    # Cria pasta se não existir
    os.makedirs(DOCX_FOLDER, exist_ok=True)

    doc = Document()

    # Estilo da fonte padrão
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Arial'
    font.size = Pt(11)

    lines = task_result.split("\n")
    for line in lines:
        line = line.strip()

        # Ignorar linhas vazias
        if not line:
            continue

        # Título H1
        if line.startswith("# "):
            doc.add_heading(line[2:].strip(), level=1)

        # Título H2
        elif line.startswith("## "):
            doc.add_heading(line[3:].strip(), level=2)

        # Título H3
        elif line.startswith("### "):
            doc.add_heading(line[4:].strip(), level=3)

        # Lista (bullets)
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:].strip(), style='List Bullet')

        # Negrito simples dentro de um parágrafo
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

        else:
            doc.add_paragraph(line)

    # Salvar arquivo
    output_path = os.path.join(DOCX_FOLDER, f"{task_id}.docx")
    doc.save(output_path)
    return output_path
