import flet as ft
from flet import icons, Colors

def get_menu_layout(on_menu_select, content_container):
    def expandable_section(title, icon, subitems):
        subitems_column = ft.Ref[ft.Column]()

        def toggle_expand(e):
            subitems_column.current.visible = not subitems_column.current.visible
            subitems_column.current.update()

        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(icon, size=20, color=Colors.WHITE),
                    ft.Text(title, size=13, weight="bold", color=Colors.WHITE),
                    ft.Icon(name=icons.KEYBOARD_ARROW_DOWN, size=16, color=Colors.WHITE)
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            on_click=toggle_expand,
            padding=10
        )

        subitems_controls = [
            ft.TextButton(
                f"• {label}",
                on_click=lambda e, name=label: on_menu_select(name),
                style=ft.ButtonStyle(color=Colors.WHITE70)
            ) for label in subitems
        ]

        return ft.Column(
            controls=[
                header,
                ft.Column(ref=subitems_column, visible=False, controls=subitems_controls, spacing=5)
            ],
            spacing=5
        )

    # Bloco: Título (Logo)
    logo_container = ft.Container(
        content=ft.Text("WeBot", size=20, weight="bold", color=Colors.WHITE),
        alignment=ft.alignment.center,
        padding=ft.Padding(0, 20, 0, 20)
    )

    # Bloco: Menus (topo)
    nav_container = ft.Container(
        content=ft.Column(
            controls=[
                expandable_section("Reorganização Digital", icons.ROCKET_LAUNCH, [
                    "Estrutura", "Pasta"
                ])
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START
        ),
        expand=True
    )

    # Bloco: User info (rodapé)
    user_info_container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Divider(color=Colors.WHITE24),
                ft.Text("Renato", size=12, color=Colors.WHITE),
                ft.Text("CDM CONTABILIDADE", size=10, color=Colors.WHITE54),
                ft.TextButton("SAIR", icon=icons.LOGOUT, style=ft.ButtonStyle(color=Colors.WHITE))
            ],
            spacing=4
        ),
        alignment=ft.alignment.bottom_left,
        margin=ft.margin.only(top=10)
    )

    # Menu final
    menu_column = ft.Column(
        controls=[
            logo_container,
            nav_container,
            user_info_container
        ],
        expand=True,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    menu = ft.Container(
        content=menu_column,
        width=250,
        padding=20,
        bgcolor="#404470",
    )

    divider = ft.VerticalDivider(width=0, color=Colors.GREY_400)

    return ft.Row(
        controls=[menu, divider, content_container],
        expand=True,
        spacing=0
    )
