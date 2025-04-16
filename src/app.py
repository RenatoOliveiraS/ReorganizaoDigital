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
        result = None

        if page_name == "Estrutura":
            result = tree_page(page)
        elif page_name == "Pasta":
            result = pastas_page()
        else:
            result = ft.Text("Página não definida")

        if isinstance(result, tuple):
            content_container.content = result[0]
            page.update()
            result[1](None)  # chama o callback
        else:
            content_container.content = result

        page.update()



    # Layout com menu lateral e área de conteúdo
    layout = get_menu_layout(update_content, content_container)
    page.add(layout)
    # Página inicial ao abrir o app
    #update_content("Estrutura")

ft.app(target=main)
