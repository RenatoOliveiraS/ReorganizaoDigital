Como executar o projeto
Requisitos
Python 3.10+

Dependências do projeto (instalar com pip install -r requirements.txt)

Banco de dados MySQL ativo e acessível

1. Subir a API (FastAPI)
Navegue até a pasta src e execute o seguinte comando:

bash
Copiar
Editar
cd src
uvicorn api:app --reload --port 8000
Isso iniciará o servidor FastAPI localmente na porta 8000.

2. Executar o Frontend com Flet
Com a API já rodando, em outro terminal execute:

python app.py

Isso abrirá a interface gráfica baseada em Flet, conectando-se à API que você subiu no passo anterior.

