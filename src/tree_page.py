import flet as ft
import requests
from area_trabalho_page import area_trabalho_page
from multi_select_dropdown_class import MultiSelectDropdown

API_URL = "http://localhost:8000"
expanded_ids: set[int] = set()


def sort_tree_alphabetically(nodes: list[dict]) -> None:
    for node in nodes:
        if "children" in node and node["children"]:
            sort_tree_alphabetically(node["children"])
    nodes.sort(key=lambda x: x["nomepasta"].lower())


def fetch_tree_data() -> list[dict]:
    try:
        response = requests.get(f"{API_URL}/arvore")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print("Erro ao buscar árvore:", e)
        return []


def tree_page(page: ft.Page):
    data = fetch_tree_data()
    tree_ref = ft.Ref[ft.Column]()
    sort_tree_alphabetically(data)

    def open_subfolder_dialog(e: ft.ControlEvent, parent_id: int):
        auto_switch = ft.Switch(label="Auto", value=False)

        # --- pasta dropdown (single-select) ---
        try:
            resp = requests.get(f"{API_URL}/pastas")
            resp.raise_for_status()
            pastas = resp.json()
        except requests.RequestException as err:
            pastas = []
            page.open(ft.SnackBar(ft.Text(f"Erro ao carregar pastas: {err}")))
            page.update()

        pasta_dropdown = MultiSelectDropdown(
            page,
            pastas,
            display_key="nomepasta",
            width=300,
            hint_text="Selecione pasta...",
            max_selected_items=1
        )

        # --- criar nova pasta ---
        def criar_pasta_popup(ev: ft.ControlEvent):
            nome_field = ft.TextField(label="Nome da Nova Pasta", width=300)

            def salvar_pasta(ev2: ft.ControlEvent):
                try:
                    resp2 = requests.post(f"{API_URL}/pastas", json={"nomepasta": nome_field.value})
                    resp2.raise_for_status()
                    resp3 = requests.get(f"{API_URL}/pastas")
                    resp3.raise_for_status()
                    pasta_dropdown.all_options = resp3.json()
                    pasta_dropdown._build_chips()
                except requests.RequestException as e:
                    page.open(ft.SnackBar(ft.Text(f"Erro ao criar pasta: {e}")))
                    
                subdialog.open = False
                page.update()

            subdialog = ft.AlertDialog(
                title=ft.Text("Criar Pasta"),
                content=ft.Column([nome_field]),
                actions=[ft.ElevatedButton("Gravar", on_click=salvar_pasta)]
            )
                
            page.overlay.append(subdialog)
            subdialog.open = True
            page.update()

        criar_pasta_btn = ft.ElevatedButton("Criar Pasta", icon=ft.icons.ADD, on_click=criar_pasta_popup)

        # lista de controles de permissão
        permissoes_controls: list[tuple[MultiSelectDropdown, MultiSelectDropdown]] = []

        # --- adicionar linha de permissão ---
        def adicionar_permissao(ev: ft.ControlEvent):
            try:
                tipos = requests.get(f"{API_URL}/tipos-permissao").json()
            except requests.RequestException:
                tipos = []
            tp_dropdown = MultiSelectDropdown(
                page,
                tipos,
                display_key="nome",
                width=300,
                hint_text="Tipo permissão",
                max_selected_items=1
            )

            try:
                grupos = requests.get(f"{API_URL}/grupos").json()
            except requests.RequestException:
                grupos = []
            gp_dropdown = MultiSelectDropdown(
                page,
                grupos,
                display_key="nome",
                width=300,
                hint_text="Grupos",
                max_selected_items=None
            )

            permissoes_controls.append((tp_dropdown, gp_dropdown))
            # Adiciona linha de permissão
            form_content.controls.insert(
                -2,
                ft.Row([tp_dropdown.widget(), gp_dropdown.widget()], spacing=10)
            )
            # Adiciona divisor após a permissão
            form_content.controls.insert(
                -2,
                ft.Divider()
            )
            page.update()

        adicionar_permissoes_btn = ft.ElevatedButton(
            "Adicionar Permissões", icon=ft.icons.ADD, on_click=adicionar_permissao
        )

        # --- ações Cancelar / Gravar ---
        def cancelar(ev: ft.ControlEvent):
            dialog.open = False
            page.update()

        def gravar(ev: ft.ControlEvent):
            pasta_sel = pasta_dropdown.selected_options
            pasta_id = int(pasta_sel[0]["id"]) if pasta_sel else None

            body = {
                "WeBotPastas_pasta_id": pasta_id,
                "auto": "S" if auto_switch.value else "N",
                "gerado": "N",
                "pai_id": parent_id,
                "replicar_para_empresas": 0,
                "permissoes": [
                    {
                        "grupo_ids": [int(g["id"]) for g in gp.selected_options],
                        "permissao_id": int(tp.selected_options[0]["id"]) if tp.selected_options else None
                    }
                    for tp, gp in permissoes_controls
                ]
            }
            try:
                requests.post(f"{API_URL}/estrutura-permissao", json=body)
                page.open(ft.SnackBar(ft.Text(f"Subpasta criada com sucesso!")))
                
            except requests.RequestException as e:
                page.open(ft.SnackBar(ft.Text(f"Erro ao gravar permissão: {e}")))



            dialog.open = False
            page.update()

        # --- monta conteúdo do formulário ---
        form_content = ft.Column([
            ft.Text(f"Pasta Pai (ID): {parent_id}"),
            auto_switch,
            ft.Row([pasta_dropdown.widget(), criar_pasta_btn], spacing=10),
            ft.Divider(),
            adicionar_permissoes_btn,
            ft.Row([], spacing=10),  # placeholder para linhas de permissão
        ], spacing=15)

        dialog = ft.AlertDialog(
            title=ft.Text("Criar Nova Subpasta", size=20, weight="bold"),
            content=ft.Container(content=form_content, width=800),
            actions=[
                ft.ElevatedButton("CANCELAR", on_click=cancelar),
                ft.ElevatedButton("GRAVAR", on_click=gravar),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    def render_node(node: dict, level: int = 0) -> list[ft.Control]:
        widgets: list[ft.Control] = []
        node_id = node["id"]
        children = node.get("children", [])
        is_expandable = bool(children)
        is_expanded = node_id in expanded_ids

        def toggle_expand(e: ft.ControlEvent, target_id=node_id):
            if target_id in expanded_ids:
                expanded_ids.remove(target_id)
            else:
                expanded_ids.add(target_id)
            refresh_tree()

        row_controls: list[ft.Control] = []
        if is_expandable:
            row_controls.append(
                ft.IconButton(
                    icon=ft.icons.KEYBOARD_ARROW_DOWN if is_expanded else ft.icons.CHEVRON_RIGHT,
                    on_click=toggle_expand,
                    icon_size=16,
                )
            )
        else:
            row_controls.append(ft.Container(width=40))

        row_controls.extend([
            ft.Icon(name=ft.icons.FOLDER, size=20),
            ft.Text(node["nomepasta"], color=ft.colors.WHITE),
            ft.IconButton(
                icon=ft.icons.ADD,
                tooltip="Criar subpasta",
                on_click=lambda e, nid=node_id: open_subfolder_dialog(e, nid)
            )
        ])

        row = ft.Row(controls=row_controls, vertical_alignment=ft.MainAxisAlignment.CENTER)
        widgets.append(ft.Container(content=row, margin=ft.margin.only(left=level * 20)))

        if is_expandable and is_expanded:
            for child in children:
                widgets.extend(render_node(child, level + 1))

        return widgets

    def refresh_tree():
        widgets: list[ft.Control] = []
        for node in data:
            if node["pai_id"] is None:
                sort_tree_alphabetically(data)
                widgets.extend(render_node(node, level=0))
        tree_ref.current.controls = widgets
        tree_ref.current.update()

    tree_column = ft.Column(ref=tree_ref, scroll=ft.ScrollMode.AUTO, expand=True)

    def after_layout(e: ft.ControlEvent):
        refresh_tree()

    return (
        area_trabalho_page(
            titulo="Estrutura de Pastas",
            body_controls=[tree_column]
        ),
        after_layout
    )
