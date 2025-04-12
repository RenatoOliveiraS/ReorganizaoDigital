import flet as ft

def get_menu(on_menu_select):
    return ft.Column(
        controls=[
            ft.Text("Menu", size=20, weight="bold"),
            ft.Divider(),
            ft.ElevatedButton("Estrutura", on_click=lambda e: on_menu_select("estrutura")),
            ft.ElevatedButton("Pastas", on_click=lambda e: on_menu_select("pastas")),
            ft.ElevatedButton("Sair", on_click=lambda e: print("Sair")),
        ],
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.START,
        spacing=10
    )
