import flet as ft

def area_trabalho_page(titulo="Área de Trabalho", body_controls=[]):
    # Cabeçalho
    head_container = ft.Container(
        content=ft.Row(
            controls=[
                ft.Text(titulo, size=22, weight="bold"),
                # Aqui você pode incluir botões, filtros, etc
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        ),
        padding=ft.Padding(0, 10, 0, 10),

    )

    # Corpo com scroll
    body_scrollable = ft.Column(
        controls=body_controls,
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        expand=True
    )

    return ft.Column(
        controls=[
            head_container,
            body_scrollable
        ],
        expand=True
    )
