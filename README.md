
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

O projeto utiliza SQLAlchemy como ORM e está preparado para criar o banco a partir dos modelos Python.

### a. Configure o arquivo `.env`

Certifique-se de que o arquivo `.env` contém a variável `DATABASE_URI` com a string de conexão para seu banco MySQL. Exemplo:

```
DATABASE_URI='mysql+pymysql://usuario:senha@localhost:3306/nome_do_banco'
```

Crie o banco de dados manualmente (caso ele ainda não exista) com o nome desejado usando sua ferramenta preferida (DBeaver, MySQL Workbench ou terminal).

### b. Crie as tabelas automaticamente

Execute o script abaixo para criar todas as tabelas no banco com base nos modelos definidos:

```bash
python src/create_db.py

```


📁 Scripts de geração de pastas
Scripts auxiliares que leem a estrutura do banco e criam diretórios locais com permissões, conforme regras definidas.

⚠️ Devem ser executados localmente em ambiente Windows com permissão de administrador.

🛠️ Pré-requisitos

Um caminho base configurável para criação das pastas. Edite no topo dos scripts:

```
base_path = r'D:\\Arquivos'
```

📂 scripts/2_cria_auto_empresas_estrutura.py
-Processa estruturas com auto == 'S'

-Cria a hierarquia de pastas automaticamente para cada empresa cadastrada

-Atualiza a tabela WeBotPastasEmpresasEstruturas

```
python scripts/2_cria_auto_empresas_estrutura.py
```

Ideal para agendamento via Agendador de Tarefas.

🗂️ scripts/3_cria_estrutura.py
-Processa estruturas com auto == 'N'

-Cria diretórios manualmente definidos na tabela WeBotPastasEstruturas

-Aplica permissões e heranças conforme o banco


```
python scripts/3_cria_estrutura.py
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
├── scripts/
│   ├── 2_cria_auto_empresas_estrutura.py
│   └── 3_cria_estrutura.py
└── README.md
```

---

## 📚 Documentação e Referências

- [Documentação oficial FastAPI](https://fastapi.tiangolo.com/)
- [Documentação oficial Flet](https://flet.dev/docs/)
- [Documentação SQLAlchemy](https://docs.sqlalchemy.org/en/20/)

---
