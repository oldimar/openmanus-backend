FROM python:3.11-slim

WORKDIR /app

COPY app/ ./app/

# Instala FastAPI, Uvicorn, OpenAI e python-dotenv
RUN pip install fastapi uvicorn openai python-dotenv

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
