import flet as ft

def pastas_page():
    return ft.Column(
        controls=[
            ft.Text("Em desenvolvimento", size=24, weight="bold")
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )
