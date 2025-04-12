import flet as ft

def main(page: ft.Page):
    page.title = "Estrutura de Pastas com End Drawer"

    def on_plus_click(path: list):
        folder_name = path[-1] if path else "Desconhecido"
        print("Botão clicado para pasta:", folder_name)
        # Cria o NavigationDrawer que queremos usar como end drawer
        nd = ft.NavigationDrawer(
            controls=[
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.ADD_TO_HOME_SCREEN_SHARP,
                    label=f"Adicionar pasta em: {folder_name}"
                ),
                ft.NavigationDrawerDestination(
                    icon=ft.Icons.ADD_COMMENT,
                    label="Opção Extra"
                )
            ]
        )
        # Configura o end drawer sem chamar open_end_drawer()
        page.end_drawer = nd
        nd.open = True
        page.update()

    def build_tree_widgets():
        # Estrutura fixa da árvore: cada tupla contém (nome, [lista de subpastas])
        folders = [
            ("Arquivo Digital", [
                ("_Certidões", []),
                ("_Comercial", []),
                ("_Empresas", [
                    ("__AutoPastWeBot - Empresas", [
                        ("___Arquivos", [
                            ("_____Dpto.Fiscal", [])
                        ])
                    ])
                ])
            ])
        ]

        def build_widgets(folder_list, indent=0, parent_path=[]):
            widgets = []
            for name, children in folder_list:
                current_path = parent_path + [name]
                def callback(e, folder_path=current_path):
                    on_plus_click(folder_path)
                row = ft.Row(
                    controls=[
                        ft.Icon(name=ft.Icons.FOLDER, size=20),
                        ft.Text(name),
                        ft.IconButton(
                            icon=ft.Icons.ADD,
                            tooltip="Adicionar Pasta",
                            on_click=callback
                        )
                    ],
                    vertical_alignment="center"
                )
                widgets.append(ft.Container(content=row, margin=ft.margin.only(left=indent)))
                if children:
                    widgets.extend(build_widgets(children, indent + 20, current_path))
            return widgets

        return build_widgets(folders)

    # Monta a árvore fixa
    tree = ft.Column(controls=build_tree_widgets(), scroll=ft.ScrollMode.AUTO)
    page.add(ft.Text("Estrutura de Pastas (Teste)", size=24))
    page.add(tree)

ft.app(target=main)
