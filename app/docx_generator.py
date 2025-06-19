from docx import Document
from docx.shared import Inches
import os

UPLOAD_FOLDER = "uploads"
EXPORT_FOLDER = "exports"
os.makedirs(EXPORT_FOLDER, exist_ok=True)

def generate_docx(task_id, task_result, task_description="", file_folder=""):
    """
    Gera um arquivo .docx com base no resultado da task e nos anexos de imagens.

    Args:
        task_id (str): O ID da task.
        task_result (str): Texto final gerado pelos agentes.
        task_description (str): Descrição da tarefa (opcional).
        file_folder (str): Nome da pasta onde estão as imagens enviadas (opcional).

    Returns:
        str: Caminho do arquivo gerado.
    """
    try:
        doc = Document()

        # Capa
        doc.add_heading(f"Resultado da Task: {task_id}", level=0)
        if task_description:
            doc.add_paragraph(f"Descrição da tarefa: {task_description}")

        doc.add_paragraph("\n")

        # Conteúdo gerado pela IA
        doc.add_heading("Resultado Gerado:", level=1)
        for line in task_result.split("\n"):
            doc.add_paragraph(line)

        doc.add_paragraph("\n")

        # Inserir imagens se houver
        if file_folder:
            folder_path = os.path.join(UPLOAD_FOLDER, file_folder)
            if os.path.exists(folder_path):
                doc.add_heading("Imagens Anexadas:", level=1)
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        image_path = os.path.join(folder_path, filename)
                        try:
                            doc.add_picture(image_path, width=Inches(5))
                            doc.add_paragraph(f"Imagem: {filename}")
                        except Exception as e:
                            doc.add_paragraph(f"Erro ao adicionar imagem {filename}: {str(e)}")

        # Caminho final do DOCX
        output_path = os.path.join(EXPORT_FOLDER, f"{task_id}.docx")
        doc.save(output_path)

        return output_path

    except Exception as e:
        return f"Erro ao gerar DOCX: {str(e)}"
