import flet as ft
from tree_page import tree_page    # Já deve existir conforme versões anteriores
from pastas_page import pastas_page
from menu import get_menu

def main(page: ft.Page):
    page.title = "Meu App - Estrutura de Pastas"
    
    # Container para a área de conteúdo que será atualizada
    content_container = ft.Container(
        expand=True,
        padding=20,
        margin=ft.margin.all(10)
    )
    
    def update_content(page_name: str):
        if page_name == "estrutura":
            content_container.content = tree_page()
        elif page_name == "pastas":
            content_container.content = pastas_page()
        else:
            content_container.content = ft.Text("Página não definida")
        page.update()
    
    # Inicializa o menu com callback para navegação
    menu_widget = get_menu(update_content)
    menu_container = ft.Container(
        content=menu_widget,
        width=250,
        padding=20,
        margin=ft.margin.only(right=10, top=10, left=10, bottom=10)
    )
    
    # Carrega a página de "Estrutura" por padrão
    update_content("estrutura")
    
    # Layout principal: menu à esquerda e conteúdo à direita
    layout = ft.Row(
        controls=[
            menu_container,
            content_container
        ],
        spacing=20,
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True
    )
    
    # Container externo para dar uma margem geral no layout
    outer_container = ft.Container(
        content=layout,
        margin=ft.margin.all(10)
    )
    
    page.add(outer_container)

ft.app(target=main)
