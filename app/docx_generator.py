from docx import Document
from docx.shared import Inches
import os
from datetime import datetime

UPLOAD_FOLDER = "uploads"
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def generate_docx(task_id, task_result, task_description="", file_folder=""):
    """
    Gera um DOCX com estrutura pedagógica básica: Capa, Sumário, Texto, Imagens, Relatório.

    Args:
        task_id (str): ID da task.
        task_result (str): Resultado completo da task (texto dos agentes).
        task_description (str): Descrição original da task.
        file_folder (str): Nome da pasta de uploads (imagens).

    Returns:
        str: Caminho do DOCX gerado.
    """
    try:
        doc = Document()

        # --- CAPA ---
        doc.add_heading("📚 Documento Gerado pela IA", level=0)
        doc.add_paragraph(f"Task ID: {task_id}")
        doc.add_paragraph(f"Descrição da Tarefa: {task_description}")
        doc.add_paragraph(f"Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

        doc.add_page_break()

        # --- SUMÁRIO SIMPLES ---
        doc.add_heading("Sumário", level=1)
        doc.add_paragraph("1. Introdução")
        doc.add_paragraph("2. Texto Principal")
        doc.add_paragraph("3. Imagens Geradas")
        doc.add_paragraph("4. Relatório Final (se houver)")

        doc.add_page_break()

        # --- TEXTO PRINCIPAL ---
        doc.add_heading("1. Introdução", level=1)
        doc.add_paragraph(f"Esta é uma geração automática baseada na task {task_id}.")

        doc.add_heading("2. Texto Principal", level=1)
        for line in task_result.split("\n"):
            doc.add_paragraph(line)

        doc.add_page_break()

        # --- IMAGENS (Se houver imagens no upload) ---
        if file_folder:
            folder_path = os.path.join(UPLOAD_FOLDER, file_folder)
            if os.path.exists(folder_path):
                doc.add_heading("3. Imagens Geradas", level=1)
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(folder_path, filename)
                        try:
                            doc.add_picture(image_path, width=Inches(5))
                            doc.add_paragraph(f"Imagem: {filename}")
                        except Exception as e:
                            doc.add_paragraph(f"Erro ao inserir {filename}: {str(e)}")

                doc.add_page_break()

        # --- RELATÓRIO FINAL (se houver bloco de agent report) ---
        if "Resultado do agente 'report':" in task_result:
            doc.add_heading("4. Relatório Final", level=1)
            report_start = task_result.find("Resultado do agente 'report':")
            report_text = task_result[report_start:].replace("Resultado do agente 'report':", "").strip()
            for line in report_text.split("\n"):
                doc.add_paragraph(line)

        # Salvar o DOCX
        output_path = os.path.join(EXPORT_FOLDER, f"{task_id}.docx")
        doc.save(output_path)

        return output_path

    except Exception as e:
        return f"Erro ao gerar DOCX: {str(e)}"
