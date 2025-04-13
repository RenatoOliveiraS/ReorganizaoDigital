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

def tree_page():
    data = fetch_tree_data()
    tree_ref = ft.Ref[ft.Column]()
    sort_tree_alphabetically(data)  
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

        # Botão de expandir (somente se tiver filhos)
        if is_expandable:
            row_controls.append(
                ft.IconButton(
                    icon=ft.Icons.KEYBOARD_ARROW_DOWN if is_expanded else ft.Icons.CHEVRON_RIGHT,
                    on_click=toggle_expand,
                    icon_size=16
                )
            )
        else:
            row_controls.append(ft.Container(width=40))  # espaçamento para alinhar com quem tem botão

        # Ícone da pasta + nome
        row_controls.append(ft.Icon(name=ft.Icons.FOLDER, size=20))
        row_controls.append(ft.Text(node["nomepasta"], color=ft.colors.WHITE))

        row = ft.Row(controls=row_controls, vertical_alignment="center")
        widgets.append(ft.Container(content=row, margin=ft.margin.only(left=level * 20)))

        # Renderiza filhos, se expandido
        if is_expandable and is_expanded:
            for child in children:
                widgets.extend(render_node(child, level + 1))

        return widgets



    def refresh_tree():
        widgets = []
        for node in data:
            if node["pai_id"] is None:
                sort_tree_alphabetically(data)

                widgets.extend(render_node(node, level=0))  # começa do nível 0

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
