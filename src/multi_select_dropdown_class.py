import flet as ft
from typing import Any, Callable, Optional

class MultiSelectDropdown:
    def __init__(
        self,
        page: ft.Page,
        all_options: list[Any],
        *,
        width: int = 400,
        hint_text: str = "Selecione opções...",
        on_change: Optional[Callable[[list[Any]], None]] = None,
        display_key: Optional[str] = None,
        max_selected_items: Optional[int] = None,
    ):
        """
        :param page: instância de ft.Page
        :param all_options: lista de itens (str ou dicts)
        :param width: largura do controle
        :param hint_text: texto de dica
        :param on_change: callback que recebe a lista de itens selecionados
        :param display_key: chave de dict para extrair o label (quando item for dict)
        :param max_selected_items: 
            - None (padrão) → ilimitado (multi-select)  
            - 1 → single-select  
            - N (>1) → até N seleções
        """
        if max_selected_items is not None and max_selected_items < 1:
            raise ValueError("max_selected_items deve ser >= 1 ou None")
        self.page = page
        self.all_options = all_options.copy()
        self.selected_options: list[Any] = []
        self.search_query = ""
        self.width = width
        self.hint_text = hint_text
        self.on_change = on_change or (lambda sel: None)
        self.display_key = display_key
        self.max_selected_items = max_selected_items

        # controles
        self.chips_and_field = ft.Row(wrap=True, spacing=5, run_spacing=5)
        self.search_field = ft.TextField(
            hint_text=self.hint_text,
            border=None,
            expand=True,
            on_change=self._filter_options,
            on_focus=lambda e: self._show_dropdown(),
        )
        self.toggle_button = ft.IconButton(
            icon=ft.icons.ARROW_DROP_DOWN,
            on_click=lambda e: self._show_dropdown()
        )
        self.search_field_row = ft.Row(
            controls=[self.search_field, self.toggle_button],
            spacing=5,
            alignment=ft.MainAxisAlignment.START
        )
        self.multi_select_container = ft.Container(
            content=self.chips_and_field,
            border=ft.border.all(1, ft.colors.GREY),
            border_radius=ft.border_radius.all(4),
            padding=ft.padding.all(6),
            width=self.width
        )
        self.dropdown_list = ft.Column(spacing=5)
        self.dropdown_container = ft.Container(
            visible=False,
            width=self.width,
            border=ft.border.all(1, ft.colors.GREY),
            border_radius=ft.border_radius.all(4),
            padding=ft.padding.all(8),
            content=self.dropdown_list
        )

        self._build_chips()

    def _get_label(self, item: Any) -> str:
        if isinstance(item, dict) and self.display_key:
            return str(item.get(self.display_key, ""))
        return str(item)

    def _build_chips(self):
        self.chips_and_field.controls.clear()
        for opt in self.selected_options:
            label = self._get_label(opt)
            chip = ft.Container(
                content=ft.Row([
                    ft.Text(label),
                    ft.IconButton(
                        icon=ft.icons.CLOSE,
                        icon_size=14,
                        on_click=lambda e, o=opt: self._remove_option(o),
                        tooltip="Remover opção"
                    )
                ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
                border=ft.border.all(1, ft.colors.GREY),
                border_radius=ft.border_radius.all(12),
                padding=ft.Padding(8, 4, 8, 4),
                bgcolor=ft.colors.GREY
            )
            self.chips_and_field.controls.append(chip)

        self.chips_and_field.controls.append(self.search_field_row)
        self.search_field.hint_text = "" if self.selected_options else self.hint_text
        self.search_field.value = ""
        self.page.update()

    def _show_dropdown(self):
        self.dropdown_container.visible = True
        self._filter_options(None)

    def _hide_dropdown(self):
        self.dropdown_container.visible = False
        self.page.update()

    def _filter_options(self, e):
        self.search_query = (self.search_field.value or "").lower().strip()
        if self.max_selected_items == 1:
            # single-select: mostra todas as opções que batem com a busca
            candidates = self.all_options
        else:
            # multi-select: exclui já selecionadas
            candidates = [
                opt for opt in self.all_options
                if opt not in self.selected_options
            ]
        filtered = [
            opt for opt in candidates
            if self.search_query in self._get_label(opt).lower()
        ]
        self.dropdown_list.controls.clear()
        for opt in filtered:
            label = self._get_label(opt)
            item = ft.Container(
                content=ft.Row([
                    ft.Text(label, expand=True),
                    ft.IconButton(
                        icon=ft.icons.ADD,
                        icon_size=14,
                        on_click=lambda e, o=opt: self._select_option(o),
                        tooltip="Selecionar"
                    )
                ], spacing=5, alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=ft.padding.all(6),
                on_click=lambda e, o=opt: self._select_option(o),
            )
            self.dropdown_list.controls.append(item)
        self.page.update()

    def _select_option(self, opt: Any):
        # single-select
        if self.max_selected_items == 1:
            self.selected_options = [opt]
            self.on_change(self.selected_options)
        else:
            # multi-select com limite
            if opt not in self.selected_options:
                if (self.max_selected_items is None
                        or len(self.selected_options) < self.max_selected_items):
                    self.selected_options.append(opt)
                    self.on_change(self.selected_options)
        self._build_chips()
        self._hide_dropdown()

    def _remove_option(self, opt: Any):
        if opt in self.selected_options:
            self.selected_options.remove(opt)
            self.on_change(self.selected_options)
        self._build_chips()

    def widget(self) -> ft.Column:
        return ft.Column([
            self.multi_select_container,
            self.dropdown_container
        ])
