import flet as ft
import requests

API_URL = "http://localhost:8000/arvore"  # Ajuste se necessário

def fetch_tree_data():
    """
    Chama a API para buscar os dados da árvore.
    Retorna uma lista de nós (dicionários) ou uma lista vazia em caso de erro.
    """
    try:
        response = requests.get(API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            print("Erro ao buscar árvore:", response.status_code)
            return []
    except Exception as e:
        print("Erro ao buscar árvore:", e)
        return []

def build_tree_widgets_from_api(data, indent=0, parent_path=[], on_plus_click=None):
    """
    Constrói recursivamente a lista de widgets para exibir a árvore de pastas.
    
    :param data: Lista de nós, onde cada nó é um dicionário com 'nomepasta' e 'children'
    :param indent: Número de pixels para recuo (indentação)
    :param parent_path: Lista que armazena o caminho (nomes) até o nó atual
    :param on_plus_click: Callback executado ao clicar no ícone de adição
    :return: Lista de widgets
    """
    widgets = []
    for node in data:
        current_path = parent_path + [node["nomepasta"]]
        # Função callback definida para capturar o caminho atual corretamente.
        def callback(e, folder_path=current_path):
            if on_plus_click:
                on_plus_click(folder_path)
        row = ft.Row(
            controls=[
                ft.Icon(name=ft.Icons.FOLDER, size=20),
                ft.Text(node["nomepasta"]),
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    tooltip="Adicionar Pasta",
                    on_click=callback
                )
            ],
            vertical_alignment="center"
        )
        widgets.append(
            ft.Container(content=row, margin=ft.margin.only(left=indent))
        )
        if node.get("children"):
            widgets.extend(
                build_tree_widgets_from_api(
                    node["children"], 
                    indent=indent+20, 
                    parent_path=current_path, 
                    on_plus_click=on_plus_click
                )
            )
    return widgets

def build_tree_widgets(on_plus_click=None):
    """Busca os dados da API e constrói a lista de widgets a partir deles."""
    data = fetch_tree_data()
    return build_tree_widgets_from_api(data, indent=0, parent_path=[], on_plus_click=on_plus_click)

def main(page: ft.Page):
    page.title = "Estrutura de Pastas com End Drawer (API) - Scroll"
    
    def on_plus_click(path: list):
        # Extrai o nome da pasta a partir do caminho
        folder_name = path[-1] if path else "Desconhecido"
        print("Botão clicado para pasta:", folder_name)
        # Cria o NavigationDrawer que será usado como end drawer
        nd = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.ADD_TO_HOME_SCREEN_SHARP,
                    label=f"Adicionar pasta em: {folder_name}"
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.ADD_COMMENT,
                    label="Opção Extra"
                )
            ]
        )
        page.end_drawer = nd
        nd.open = True
        page.update()

    # Constrói a árvore usando os dados da API
    tree_widgets = build_tree_widgets(on_plus_click)
    # Cria um widget de coluna com scroll
    tree_column = ft.Column(controls=tree_widgets, scroll=ft.ScrollMode.AUTO)
    # Envolvemos a coluna em um container com altura fixa para que a rolagem ocorra
    tree_container = ft.Container(
        content=tree_column,
        height=600,  # ajuste conforme necessário
        expand=True
    )

    page.add(ft.Text("Estrutura de Pastas:", size=24))
    page.add(tree_container)

ft.app(target=main)
