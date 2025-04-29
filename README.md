
# Reorganização Digital

Este projeto é uma aplicação para gerenciamento e reorganização estruturada de pastas e permissões, utilizando **FastAPI**, **Flet**, **SQLAlchemy** e **MySQL**. Ele permite a criação automatizada de diretórios no sistema de arquivos com base em dados configurados no banco, além de controle granular de permissões NTFS.


---

## 📌 Funcionalidades principais:

- Gerenciamento visual e hierárquico de pastas por empresas
- Criação automática e manual de estruturas de diretórios
- Controle de permissões baseado em grupos
- Integração por API REST com FastAPI
- Interface gráfica com Flet

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

```
git clone https://github.com/RenatoOliveiraS/ReorganizaoDigital.git
cd ReorganizaoDigital
```

### 2. Crie e ative um ambiente virtual (recomendado)

```
python -m venv venv
# Windows
.\venv\Scripts\activate
```

### 3. Instale as dependências

```
pip install -r requirements.txt
```
## Atenção - Após a instalação dos 'requirements.txt', por favor, reiniciar o VSCODE ou use o comando Developer: Reload Window (Ctrl+Shift+P → “Reload Window”) ou, mais simples, feche e reabra apenas o terminal integrado. Isso já faz o shell adotar o venv e não dá mais erro de módulo não encontrado.

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

```
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

📂 scripts/criar_pastas_automatica_por_empresa.py
-Processa estruturas com auto == 'S'

-Cria a hierarquia de pastas automaticamente para cada empresa cadastrada

-Atualiza a tabela WeBotPastasEmpresasEstruturas

```
python scripts/criar_pastas_automatica_por_empresa.py
```

Ideal para agendamento via Agendador de Tarefas.

🗂️ scripts/criar_pastas_estrutura_manual.py
-Processa estruturas com auto == 'N'

-Cria diretórios manualmente definidos na tabela WeBotPastasEstruturas

-Aplica permissões e heranças conforme o banco


```
python scripts/criar_pastas_estrutura_manual.py
```

---

### 📝 `scripts/renomear_pastas.py`

- Renomeia pastas de acordo com registros marcados para atualização (`razao_social_atualizar = 'S'`)
- Atualiza `old_path` e marca como atualizado no banco
- Útil para manter os nomes de diretórios em sincronia com o banco de dados

```
python scripts/renomear_pastas.py
```

---

## 🎯 Como executar a aplicação

### 1. Executar API (backend)

No diretório raiz:

```
cd src
uvicorn api:app --reload --port 8000
```

Acesse a documentação da API em:

```
http://localhost:8000/docs
```

### 2. Executar a interface visual (frontend)

Execute o seguinte comando no diretório raiz:

```
python src/app.py
```

---

## 🛠️ Estrutura do projeto

```
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
│   ├── criar_pastas_automatica_por_empresa.py
│   |── criar_pastas_estrutura_manual.py
|   └── renomear_pastas.py
└── README.md
```

---

## 📚 Documentação e Referências

- [Documentação oficial FastAPI](https://fastapi.tiangolo.com/)
- [Documentação oficial Flet](https://flet.dev/docs/)
- [Documentação SQLAlchemy](https://docs.sqlalchemy.org/en/20/)

---
![alt text](image.png)
![alt text](image-1.png)
![alt text](image-2.png)