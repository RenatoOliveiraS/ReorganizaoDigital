
# Reorganização Digital

Este projeto é uma aplicação que permite o gerenciamento e reorganização estruturada de pastas e permissões, construída utilizando **FastAPI**, **Flet** e **SQLAlchemy**.

---

## 📌 Funcionalidades principais:

- Gerenciamento estruturado e visualização em árvore das pastas.
- Controle detalhado de permissões por grupos.
- Interface visual simples, eficiente e intuitiva construída com Flet.
- API REST para integração com outros sistemas.

---

## 🚀 Tecnologias utilizadas:

- [Python](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Flet](https://flet.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [MySQL](https://www.mysql.com/)

---

## 📦 Como instalar

### 1. Clone o repositório

```bash
git clone https://github.com/RenatoOliveiraS/ReorganizaoDigital.git
cd ReorganizaoDigital
```

### 2. Crie e ative um ambiente virtual (recomendado)

```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo `.env.example` para `.env` e preencha-o com as suas credenciais corretas:

```bash
cp .env.example .env
```

Exemplo do arquivo `.env`:

```
DATABASE_URI='mysql+pymysql://usuario:senha@host:porta/nome_do_banco'
```

---

## 🎯 Como executar a aplicação

### 1. Executar API (backend)

No diretório raiz:

```bash
uvicorn src.api:app --reload
```

Acesse a documentação da API em:

```
http://localhost:8000/docs
```

### 2. Executar a interface visual (frontend)

Execute o seguinte comando no diretório raiz:

```bash
python src/app.py
```

---

## 🛠️ Estrutura do projeto

```bash
ReorganizaoDigital/
├── .env                   # Variáveis de ambiente locais (não versionado)
├── .env.example           # Exemplo para configuração inicial
├── .gitignore
├── requirements.txt       # Dependências do projeto
├── src/
│   ├── api.py             # API REST usando FastAPI
│   ├── app.py             # Aplicação Flet principal
│   └── outros arquivos auxiliares...
└── README.md
```

---

## 📚 Documentação e Referências

- [Documentação oficial FastAPI](https://fastapi.tiangolo.com/)
- [Documentação oficial Flet](https://flet.dev/docs/)
- [Documentação SQLAlchemy](https://docs.sqlalchemy.org/en/20/)

---
