__version__ = "0.0.0"


import json
import dearpygui.dearpygui as dpg

from utils import get_id, timestamp_now
from latex import prepare_latex
from data import (
    PROJECT_ROOT,
    UPI,
    APP_CONTEXT,
    ProjectContext,
    WaterConsumerNorms,
    get_water_consumer_norm_by_name,
    set_num_of_visitors,
)

from settings import app_logger


def _autosave():
    now_ = _utsn()
    if (now_ - APP_CONTEXT["LAST_SAVE"]) > 10:
        UPI.dump()
        app_logger.debug("autosave")
        APP_CONTEXT["LAST_SAVE"] = now_


def _mk_handler(func: dpg.Callable, *args, **kwargs):
    def _(sender, app_data):
        func(*args, **kwargs)
    return _

def _utsn() -> int:
    import time
    import datetime
    return int(time.mktime(datetime.datetime.now().timetuple()))

def create_report():
    report_fname = f"report_{timestamp_now()}"

    from tkinter import Tk
    from tkinter.filedialog import asksaveasfilename

    Tk().withdraw()
    fpath = asksaveasfilename(
        initialdir=PROJECT_ROOT,
        initialfile=report_fname,
    )

    prepare_latex(fpath, **{})

def handle_mouse_move_event():
    _autosave()

def handle_mouse_click_event():
    _autosave()


def handle_double_click(*args, **kwargs):
    if APP_CONTEXT["CURRENT_WIN"] == "main":
        if dpg.is_item_hovered("listbox"):
            project_path = dpg.get_value("listbox")
            app_logger.debug(("litbox", args, kwargs, project_path))
            clear_viewport()
            project_screen(project_path, ProjectContext.load(project_path))


def quit():
    dpg.stop_dearpygui()


def show_error(message: str):
    with dpg.window(modal=True, no_resize=True, tag="error_modal"):
        dpg.add_text(message)


def draw_consumer_card(
    parent: int | str,
    variant: str,
    project_ctx: ProjectContext,
    draw_only: bool = False,
    card: WaterConsumerNorms | None = None,
    card_num_of_visitors: int | None = None,
):
    if card is None:
        num_of_visitors = APP_CONTEXT["NUM_OF_VISITORS"]
        cons: WaterConsumerNorms = APP_CONTEXT["CURRENT_CONSUMER"]
        cons_id = get_id()
    else:
        if card_num_of_visitors is None:
            return
        num_of_visitors = card_num_of_visitors
        cons: WaterConsumerNorms = card
        cons_id = get_id()

    if num_of_visitors <= 0:
        show_error("Количество измерителей не может равняться 0")
        return

    def _delcons():
        _, win = APP_CONTEXT["CHOOSEN_CONSUMERS"][cons_id]
        del APP_CONTEXT["CHOOSEN_CONSUMERS"][cons_id]
        dpg.delete_item(win)
        dpg.delete_item(f"spacer_{cons_id}")

    if not draw_only:
        project_ctx.add_variant_object(variant, cons.name, cons.id, num_of_visitors)

    with dpg.child_window(parent=parent, height=360, width=450) as cwin:
        with dpg.group(horizontal=True):
            dpg.add_button(label="X", callback=_mk_handler(_delcons))
            dpg.add_separator(label=cons.name)

        dpg.add_spacer(height=10)
        dpg.add_text("Норма расхода воды")

        dpg.add_spacer(height=10)
        # dpg.add_text("В сутки наибольшего потребления: ")
        # dpg.add_text(f"Общая (в том числе горячей) q^tot_u: {cons.max_hot_and_cold_water_norms_per_day}")
        # dpg.add_text(f"Горячей qhu: {cons.max_hot_water_norms_per_day}")

        dpg.add_spacer(height=10)
        dpg.add_text("В час наибольшего потребления")
        dpg.add_text(f"Общая (в том числе горячей) q_tothr,u: {cons.max_hot_and_cold_water_norms_per_hour}")
        dpg.add_text(f"Горячей qhhr,u: {cons.max_hot_water_norms_per_hour}")

        dpg.add_spacer(height=10)
        dpg.add_text(f"Расход воды прибором, л/с (л/ч)")
        dpg.add_text(f"Общий (холодной и горячей) qtoto: {cons.device_water_consumption_hot_and_cold}")
        dpg.add_text(f"Холодной или горячей: {cons.device_water_consumption_hot_or_cold}")

        dpg.add_spacer(height=10)
        dpg.add_text("Т,ч")

    dpg.add_spacer(parent=parent, height=10, tag=f"spacer_{cons_id}")

    APP_CONTEXT["CHOOSEN_CONSUMERS"][cons_id] = cons, cwin


def main_screen():
    APP_CONTEXT["CURRENT_WIN"] = "main"

    def create_project_button_handler():
        from tkinter import Tk
        from tkinter.filedialog import asksaveasfilename

        Tk().withdraw()
        fpath = asksaveasfilename(
            defaultextension="json",
            initialdir=PROJECT_ROOT,
            initialfile="project"
        )

        with open(fpath, "w") as f:
            json.dump({}, f)
        
        UPI.add_project(fpath)

        pctx = ProjectContext.new(fpath)

        clear_viewport()
        project_screen(fpath, pctx)
    
    def open_project_button_handler():
        from tkinter import Tk
        from tkinter.filedialog import askopenfilename

        Tk().withdraw()
        fpath = askopenfilename(
            defaultextension="json",
            initialdir=PROJECT_ROOT,
        )

        try:
            with open(fpath) as f:
                json.load(f)
        except:
            with dpg.window(label="Ошибка", modal=True):
                dpg.add_text("Неверный формат файла")
            return
        
        UPI.add_project(fpath)

        pctx = ProjectContext.load(fpath)
        
        clear_viewport()
        project_screen(fpath, pctx)

    with dpg.window(
        label="Водопотребление",
        width=APP_CONTEXT["WIN_W"],
        height=APP_CONTEXT["WIN_H"],
        autosize=True,
        on_close=_mk_handler(quit),
        tag="root_win"
    ):
        with dpg.group(horizontal=True):
            dpg.add_button(label="Открыть", callback=open_project_button_handler)
            dpg.add_button(label="Создать", callback=create_project_button_handler)
        dpg.add_spacer(height=10)
        with dpg.group(height=200, width=-1):
            dpg.add_text("Недавние проекты:")
            listbox = dpg.add_listbox(items=UPI.users_projects_paths, num_items=20, indent=-20, tracked=True, tag="listbox")
        with dpg.theme() as listbox_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (37, 37, 38), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (37, 37, 38), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (190, 190, 190), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, (102, 104, 107), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, (90, 93, 94), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (98, 145, 156), category=dpg.mvThemeCat_Core)
        dpg.bind_item_theme(listbox, listbox_theme)


def project_screen(project_path: str, pctx: ProjectContext):
    APP_CONTEXT["CURRENT_WIN"] = "project"
    APP_CONTEXT["CURRENT_PROJECT_PATH"] = project_path

    app_logger.error("PROJECT SCREEN")
    
    def add_variant_button():
        pctx.last_var_num = pctx.last_var_num + 1
        pctx.vars = pctx.vars + [f"вариант {pctx.last_var_num}"]

        dpg.add_button(
            label=f"вариант {pctx.last_var_num}",
            tag=f"var_win_{pctx.last_var_num}",
            width=150, height=100, parent="vars_hor",
            callback=_mk_tab_opnr(f"var_win_вариант {pctx.last_var_num}")
        )

    def open_variant_tab(tabname: str):
        app_logger.debug(tabname)
        if tabname not in pctx.opened_tabs_tags:
            dpg.add_tab(parent="project_bar", label=tabname, tag=f"tab_{tabname}", closable=True)
            pctx.add_variant(f"tab_{tabname}")
            variant_screen(f"tab_{tabname}", pctx)
    
    def _mk_tab_opnr(nm: str):
        app_logger.debug(nm)
        def _open():
            open_variant_tab(nm)
        return _open
    
    def handle_tab_change():
        app_logger.debug("changed")

        children = dpg.get_item_children('project_bar')
        if children is not None:
            for tab in children[1]:
                if not dpg.is_item_visible(tab):
                    app_logger.debug(('this tab was closed:', tab))
                    dpg.delete_item(tab)

    with dpg.window(
        label="Водопотребление",
        width=APP_CONTEXT["WIN_W"],
        height=APP_CONTEXT["WIN_H"],
        autosize=True,
        on_close=_mk_handler(quit),
        tag="root_win"
    ):
        tb = dpg.add_tab_bar(reorderable=True, tag="project_bar", callback=handle_tab_change)

        with dpg.tab(parent=tb, label="Проект"):
            with dpg.group():
                dpg.add_text("Варианты объектов:")
                dpg.add_button(label="+", tag="add_var_win", width=50, height=40, callback=add_variant_button)
                dpg.add_spacer(height=5)
                with dpg.group(horizontal=True, tag="vars_hor"):
                    if pctx.is_loaded():
                        for el in pctx.vars:
                            dpg.add_button(label=el, tag=f"var_win_{el}", width=150, height=100, callback=_mk_tab_opnr(f"var_win_{el}"))
        with dpg.theme() as var_win_style:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (90, 93, 94), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (102, 104, 107), category=dpg.mvThemeCat_Core)
        with dpg.theme() as add_var_win_style:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (98, 145, 156), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (98, 145, 156), category=dpg.mvThemeCat_Core)
        dpg.bind_item_theme("add_var_win", add_var_win_style)
        if pctx.is_loaded():
            for var in pctx.vars:
                dpg.bind_item_theme(f"var_win_{var}", var_win_style)

    dpg.set_primary_window("root_win", True)


def clear_viewport():
    dpg.set_primary_window("root_win", False)
    dpg.delete_item("root_win")


def variant_screen(parent_tab: str, project_ctx: ProjectContext):
    with dpg.group(horizontal=True, parent=parent_tab) as mwin:
        with dpg.child_window(width=APP_CONTEXT["LEFT_CHILD_WIN_W"], border=False):
            with dpg.child_window(border=False):
                dpg.add_text("Тип потребителя")

                dpg.add_combo(
                    items=[el.name for el in APP_CONTEXT["WATER_CONSUMERS"]],
                    default_value=APP_CONTEXT["WATER_CONSUMERS"][0].name,
                    callback=lambda _, d: get_water_consumer_norm_by_name(d),
                    height_mode=10,
                    width=480
                )

                dpg.add_spacer(height=10)
                dpg.add_text("Количество измерителей")
                dpg.add_input_int(min_clamped=True, callback=lambda _, d: set_num_of_visitors(d))
                dpg.add_spacer(height=10)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Добавить",
                        height=30, width=240,
                        callback=_mk_handler(
                            draw_consumer_card,
                            f"right_var_win_{parent_tab}",
                            # parent_tab,
                            parent_tab,
                            project_ctx,
                        )
                    )

                    dpg.add_button(
                        label="Сформировать отчет",
                        height=30, width=240,
                        callback=_mk_handler(create_report)
                    )
            # cw = dpg.add_child_window(parent=mwin, tag=f"right_var_win_{parent_tab}")
            with dpg.child_window(parent=mwin, tag=f"right_var_win_{parent_tab}", border=False) as cw:
                dpg.add_text("Добавленные потребители:", parent=cw)
                for k, v in project_ctx.variants_data[parent_tab]["objects"].items():
                    card = APP_CONTEXT["WATER_CONSUMERS"][v["params"]["id"]-1]
                    draw_consumer_card(f"right_var_win_{parent_tab}", parent_tab, project_ctx, True, card, v["num_of_object_visitors"])

        with dpg.theme() as container_theme:
            with dpg.theme_component(dpg.mvGroup):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (100, 0, 240), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (255, 0, 0), category=dpg.mvThemeCat_Core)

            dpg.bind_item_theme(cw, container_theme)

def _startup():
    dpg.create_context()
    dpg.create_viewport(
        title=f'waterconsumption v{__version__}',
        width=APP_CONTEXT["WIN_W"],
        min_width=APP_CONTEXT["WIN_W"],
        height=APP_CONTEXT["WIN_H"],
        min_height=APP_CONTEXT["WIN_H"],
    )
    with dpg.handler_registry() as dcr:
        dpg.add_mouse_double_click_handler(callback=handle_double_click)
        dpg.add_mouse_move_handler(callback=handle_mouse_move_event)
        dpg.add_mouse_click_handler(callback=handle_mouse_click_event)

def prep_font():
    with dpg.font_registry():
        # NOTE: dearpygui can't go to folders with non-utf8 symbols. fuck my ass
        # app_logger.debug(f"cwd: {os.getcwd()}")
        # font_path = f"{PROJECT_ROOT}\\assets\\notomono-regular.ttf".replace("\\", "/")

        font_path = "./assets/notomono-regular.ttf"

        with dpg.font(font_path, 18, default_font=True, tag="font-ru"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.bind_font("font-ru")

def _finalize():
    dpg.setup_dearpygui()
    dpg.show_viewport()
    prep_font()
    dpg.set_primary_window("root_win", True)
    dpg.start_dearpygui()
    dpg.destroy_context()


def main():
    _startup()
    main_screen()
    _finalize()


if __name__ == "__main__":
    app_logger.debug("starting app")
    main()