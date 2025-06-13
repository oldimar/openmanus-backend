# OpenManus Backend

Backend FastAPI do OpenManus — pronto para deploy na Railway.

---

## 🚀 Deploy com 1 clique

Clique no botão abaixo para fazer deploy automático no Railway:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/project?template=https://github.com/oldimar/openmanus-backend)

---

## 🧪 Como usar a API

Após o deploy, acesse:

[https://openmanus-production-7c01.up.railway.app/docs](https://openmanus-production-7c01.up.railway.app/docs)

### Endpoints disponíveis:

- `POST /task`
  - Exemplo de body:
    ```json
    { "task": "Planeje uma viagem de 3 dias para Recife" }
    ```

- `GET /status/{task_id}`
  - Verifica o status e resultado da tarefa

---

## 📂 Estrutura

- `main.py`: Define a API FastAPI
- `logic.py`: Simula tarefas em background
- `Dockerfile`: Define como rodar o app na Railway
