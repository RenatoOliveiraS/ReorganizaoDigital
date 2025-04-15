import flet as ft
import requests
from area_trabalho_page import area_trabalho_page

API_URL = "http://localhost:8000/arvore"
expanded_ids = set()

def sort_tree_alphabetically(nodes):
    for node in nodes:
        if "children" in node and node["children"]:
            sort_tree_alphabetically(node["children"])
    nodes.sort(key=lambda x: x["nomepasta"].lower())

def fetch_tree_data():
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

def tree_page(page: ft.Page):
    data = fetch_tree_data()
    tree_ref = ft.Ref[ft.Column]()
    sort_tree_alphabetically(data)

    def open_subfolder_form(e: ft.ControlEvent, parent_id: int):
        # Cria o formulário para criação de subpasta a partir da pasta selecionada
        nome_field = ft.TextField(label="Nome da Subpasta", width=300)

        def salvar_subpasta(e_salvar: ft.ControlEvent):
            print(f"Salvar subpasta: {nome_field.value} com pai_id: {parent_id}")
            # Fecha o end drawer após salvar
            page.end_drawer = None
            page.update()

        salvar_button = ft.ElevatedButton("Salvar", on_click=salvar_subpasta)
        
        # Container com padding para o formulário
        form_content = ft.Container(
            padding=20,
            content=ft.Column(
                controls=[
                    ft.Text("Criar Nova Subpasta", size=20, weight="bold"),
                    nome_field,
                    salvar_button
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20,
                width=350
            )
        )

        # Criação do NavigationDrawer sem parâmetro "content" no construtor
        drawer = ft.NavigationDrawer()
        # Atribui o conteúdo ao drawer após a criação
        drawer.content = form_content

        # Configura o end drawer da page e abre-o
        page.end_drawer = drawer
        drawer.open = True
        page.update()


    def render_node(node, level=0):
        widgets = []
        node_id = node["id"]
        children = node.get("children", [])
        is_expandable = len(children) > 0
        is_expanded = node_id in expanded_ids

        def toggle_expand(e, target_id=node_id):
            if target_id in expanded_ids:
                expanded_ids.remove(target_id)
            else:
                expanded_ids.add(target_id)
            refresh_tree()

        row_controls = []

        if is_expandable:
            row_controls.append(
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_ARROW_DOWN if is_expanded else ft.Icons.CHEVRON_RIGHT,
                    on_click=toggle_expand,
                    icon_size=16
                )
            )
        else:
            row_controls.append(ft.Container(width=40))

        row_controls.append(ft.Icon(name=ft.Icons.FOLDER, size=20))
        row_controls.append(ft.Text(node["nomepasta"], color=ft.colors.WHITE))
        
        row_controls.append(
            ft.IconButton(
                icon=ft.Icons.ADD,
                tooltip="Criar subpasta",
                on_click=lambda e, node_id=node["id"]: open_subfolder_form(e, node_id)
            )
        )

        row = ft.Row(controls=row_controls, vertical_alignment="center")
        widgets.append(ft.Container(content=row, margin=ft.margin.only(left=level * 20)))

        if is_expandable and is_expanded:
            for child in children:
                widgets.extend(render_node(child, level + 1))

        return widgets

    def refresh_tree():
        widgets = []
        for node in data:
            if node["pai_id"] is None:
                sort_tree_alphabetically(data)
                widgets.extend(render_node(node, level=0))
        tree_ref.current.controls = widgets
        tree_ref.current.update()

    tree_column = ft.Column(ref=tree_ref, scroll=ft.ScrollMode.AUTO, expand=True)

    def after_layout(e):
        refresh_tree()

    return (
        area_trabalho_page(
            titulo="Estrutura de Pastas",
            body_controls=[tree_column]
        ),
        after_layout
    )
