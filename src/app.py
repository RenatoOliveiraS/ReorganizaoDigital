import flet as ft
from tree_page import tree_page
from pastas_page import pastas_page
from menu import get_menu_layout



def main(page: ft.Page):
    
    page.title = "Meu App - Estrutura de Pastas"
    page.window_width = 1000
    page.window_height = 600
    page.window_resizable = True

    # Container da área de conteúdo, controlado dinamicamente
    content_container = ft.Container(
        expand=True,
        padding=20,
        
    )

    def update_content(page_name: str):
        if page_name == "Estrutura":
            content_container.content = tree_page()
        elif page_name == "Pasta":
            content_container.content = pastas_page()
        else:
            content_container.content = ft.Text("Página não definida")
        page.update()

    # Layout com menu lateral e área de conteúdo
    layout = get_menu_layout(update_content, content_container)
    page.add(layout)

ft.app(target=main)
