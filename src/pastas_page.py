from area_trabalho_page import area_trabalho_page
import flet as ft

def pastas_page():
    return area_trabalho_page(
        titulo="Pastas",
        body_controls=[
            ft.Text("Conteúdo de exemplo da área de trabalho."),
            ft.ElevatedButton("Ação", on_click=lambda e: print("Cliquei"))
        ]
    )
