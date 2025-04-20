import flet as ft

def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK  # garante o dark theme

    header = ft.Text("MultiSelect Dropdown Demo", size=20)
    instruction = ft.Text("Clique na seta para mostrar o dropdown e selecione uma opção.", size=14)

    all_options = [
        "Bootstrap", "Reactjs", "Laravel", "Vuejs",
        "Angular", "Django", "Flask", "Svelte",
        "Nodejs", "TailwindCSS"
    ]
    selected_options = []
    search_query = ""

    chips_and_field = ft.Row(wrap=True, spacing=5, run_spacing=5)

    search_field = ft.TextField(
        hint_text="Selecione opções...",
        border=None,
        expand=True,
        on_change=lambda e: filter_options(e),
        on_focus=lambda e: show_dropdown(e)
    )

    toggle_button = ft.IconButton(
        icon=ft.icons.ARROW_DROP_DOWN,
        on_click=lambda e: show_dropdown(e)
    )

    search_field_row = ft.Row(
        controls=[search_field, toggle_button],
        spacing=5,
        alignment=ft.MainAxisAlignment.START
    )

    multi_select_container = ft.Container(
        content=chips_and_field,
        border=ft.border.all(1, ft.colors.GREY),
        border_radius=ft.border_radius.all(4),
        padding=ft.padding.all(6),
        width=400
    )

    dropdown_list = ft.Column(spacing=5)
    dropdown_container = ft.Container(
        visible=False,
        width=400,
        border=ft.border.all(1, ft.colors.GREY),
        border_radius=ft.border_radius.all(4),
        # Removido fundo branco para compatibilidade com tema escuro
        padding=ft.padding.all(8),
        content=dropdown_list
    )

    def build_chips():
        chips_and_field.controls.clear()
        for opt in selected_options:
            chip = ft.Container(
                content=ft.Row(
                    [
                        ft.Text(opt),
                        ft.IconButton(
                            icon=ft.icons.CLOSE,
                            icon_size=14,
                            on_click=lambda e, o=opt: remove_option(e, o),
                            tooltip="Remover opção"
                        )
                    ],
                    spacing=3,
                    alignment=ft.MainAxisAlignment.CENTER
                ),
                border=ft.border.all(1, ft.colors.GREY),
                border_radius=ft.border_radius.all(12),
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=ft.colors.GREY
            )
            chips_and_field.controls.append(chip)

        chips_and_field.controls.append(search_field_row)
        search_field.hint_text = "" if selected_options else "Selecione opções..."
        search_field.value = ""
        page.update()

    def remove_option(e: ft.ControlEvent, opt: str):
        if opt in selected_options:
            selected_options.remove(opt)
        build_chips()

    def show_dropdown(e: ft.ControlEvent):
        dropdown_container.visible = True
        filter_options(e)

    def hide_dropdown():
        dropdown_container.visible = False
        page.update()

    def filter_options(e: ft.ControlEvent):
        nonlocal search_query
        search_query = search_field.value.lower().strip()

        # Só opções ainda não selecionadas
        filtered = [
            opt for opt in all_options
            if search_query in opt.lower() and opt not in selected_options
        ]

        dropdown_list.controls.clear()
        for opt in filtered:
            item_row = ft.Row(
                controls=[
                    ft.Text(opt, expand=True),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        icon_size=14,
                        on_click=lambda e, o=opt: select_option(e, o),
                        tooltip="Selecionar"
                    )
                ],
                spacing=5,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )

            item_container = ft.Container(
                content=item_row,
                padding=ft.padding.all(6),
                on_click=lambda e, o=opt: select_option(e, o),
                # Remove fundo branco; respeita tema do app
                bgcolor=None
            )

            dropdown_list.controls.append(item_container)

        page.update()

    def select_option(e: ft.ControlEvent, opt: str):
        if opt not in selected_options:
            selected_options.append(opt)
        build_chips()
        hide_dropdown()

    layout = ft.Column(
        controls=[
            header,
            instruction,
            multi_select_container,
            dropdown_container
        ],
        spacing=10
    )

    page.add(layout)
    build_chips()

ft.app(target=main)
