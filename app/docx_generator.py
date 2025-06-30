from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Pt, Inches
import os
import re
import requests
from datetime import datetime

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

    # ✅ CAPA
    doc.add_heading('Relatório de Atividades Gerado pela IA', level=0).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph(f'Task ID: {task_id}').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph(f'Data de geração: {datetime.now().strftime("%d/%m/%Y %H:%M")}').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_page_break()

    # ✅ SUMÁRIO
    doc.add_heading('Sumário', level=1)
    doc.add_paragraph('Este é um sumário estático. Para gerar um sumário real, atualize manualmente dentro do Word Desktop.')
    doc.add_paragraph('- Plano de Aula')
    doc.add_paragraph('- Código Gerado')
    doc.add_paragraph('- Texto Produzido')
    doc.add_paragraph('- Imagens Geradas')
    doc.add_paragraph('- Relatório Final')
    doc.add_page_break()

    # ✅ Blocos estruturados
    for bloco in task_result:
        texto = bloco.get("texto", "")
        imagem_url = bloco.get("imagem_url", "").strip()
        opcoes = bloco.get("opcoes", [])

        if texto:
            lines = texto.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    doc.add_paragraph()
                    continue

                match_agent = re.match(r"Resultado do agente '(.*?)':", line)
                if match_agent:
                    agent_name = match_agent.group(1)
                    section_title = {
                        "plan": "Plano de Aula",
                        "code": "Código Gerado",
                        "write": "Texto Produzido",
                        "image": "Imagens Geradas",
                        "report": "Relatório Final"
                    }.get(agent_name, f"Agente: {agent_name}")
                    doc.add_page_break()
                    doc.add_heading(section_title, level=1)
                    continue

                if line.startswith("# "):
                    doc.add_heading(line[2:].strip(), level=2)
                elif line.startswith("## "):
                    doc.add_heading(line[3:].strip(), level=3)
                elif line.startswith("### "):
                    doc.add_heading(line[4:].strip(), level=4)
                elif line.startswith("- ") or line.startswith("* "):
                    para = doc.add_paragraph(line[2:].strip(), style='List Bullet')
                    para.paragraph_format.space_after = Pt(6)
                elif re.match(r'!\[.*\]\(http.*\)', line):
                    match = re.match(r'!\[(.*?)\]\((http.*?)\)', line)
                    if match:
                        alt_text = match.group(1)
                        image_url = match.group(2)
                        image_filename = os.path.join(temp_image_folder, os.path.basename(image_url).split("?")[0])
                        if download_image(image_url, image_filename):
                            try:
                                doc.add_picture(image_filename, width=Inches(5))
                                doc.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                                doc.add_paragraph(alt_text).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                            except Exception as e:
                                doc.add_paragraph(f"[Erro ao adicionar imagem markdown: {str(e)}]")
                elif re.match(r'^https?://.*\.(png|jpg|jpeg)', line, re.IGNORECASE):
                    image_url = line
                    image_filename = os.path.join(temp_image_folder, os.path.basename(image_url).split("?")[0])
                    if download_image(image_url, image_filename):
                        try:
                            doc.add_picture(image_filename, width=Inches(5))
                            doc.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                        except Exception as e:
                            doc.add_paragraph(f"[Erro ao adicionar imagem direta: {str(e)}]")
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
                else:
                    para = doc.add_paragraph(line)
                    para.paragraph_format.space_after = Pt(8)

        if imagem_url.startswith("http"):
            image_filename = os.path.join(temp_image_folder, os.path.basename(imagem_url).split("?")[0])
            if download_image(imagem_url, image_filename):
                try:
                    doc.add_paragraph()
                    doc.add_picture(image_filename, width=Inches(5))
                    doc.paragraphs[-1].alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                    doc.add_paragraph("[Imagem gerada automaticamente]").alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
                except Exception as e:
                    doc.add_paragraph(f"[Erro ao adicionar imagem externa: {str(e)}]")

    output_path = os.path.join(DOCX_FOLDER, f"{task_id}.docx")
    doc.save(output_path)
    return output_path
