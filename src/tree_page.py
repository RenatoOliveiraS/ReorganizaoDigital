import flet as ft
import requests
from area_trabalho_page import area_trabalho_page

API_URL = "http://localhost:8000/arvore"

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

def build_tree_widgets_from_api(data, indent=0, parent_path=[], on_plus_click=None):
    widgets = []
    for node in data:
        current_path = parent_path + [node["nomepasta"]]
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
                    on_click=callback,
                ),
            ],
            vertical_alignment="center"
        )

        widgets.append(ft.Container(content=row, margin=ft.margin.only(left=indent)))

        if node.get("children"):
            widgets.extend(
                build_tree_widgets_from_api(
                    node["children"],
                    indent=indent+20,
                    parent_path=current_path,
                    on_plus_click=on_plus_click,
                )
            )
    return widgets

def build_tree_widgets(on_plus_click=None):
    data = fetch_tree_data()
    return build_tree_widgets_from_api(data, indent=0, parent_path=[], on_plus_click=on_plus_click)

def tree_page():
    tree_widgets = build_tree_widgets(on_plus_click=lambda path: print("Adicionar em:", path))
    return area_trabalho_page(
        titulo="Estrutura de Pastas",
        body_controls=tree_widgets
    )
