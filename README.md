# Sistema de Feedback para Cursos Livres

Este projeto é um dashboard interativo construído com **Streamlit** que simula a coleta e análise de feedbacks de cursos livres, utilizando **SQLite** para persistência de dados e **Docker Compose** para padronizar o ambiente de execução.

## 🚀 Como Executar o Projeto

Para garantir que o ambiente seja idêntico ao de desenvolvimento (evitando erros de compilação como o que ocorreu com o `numpy` no seu sistema local), utilize o **Docker Compose**.

### Pré-requisitos
* **Docker Desktop** instalado e rodando.

### 1. Preparação dos Arquivos
Certifique-se de que todos os arquivos estejam na mesma pasta:
* `app.py`
* `requirements.txt`
* `Dockerfile`
* `docker-compose.yml`
* `.python-version` (Opcional, mas recomendado)

### 2. Execução (Via Docker Compose)
Abra o terminal (PowerShell, CMD, ou terminal Linux/Mac) na pasta raiz do projeto e execute o seguinte comando:

```bash
docker compose up --build


Endereço para testar: http://localhost:8501