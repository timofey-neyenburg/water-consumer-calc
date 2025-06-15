__version__ = "0.1.0"


from decimal import ROUND_UP, Decimal
import json
import os
import dearpygui.dearpygui as dpg

from latex import StopSignal, prepare_latex
from data import (
    PROJECT_ROOT,
    UPI,
    APP_CONTEXT,
    ProjectContext,
)
from mathematics import (
    MultipleObjectsDataReport,
    OneObjectDataReport,
    WaterConsumerNorms,
    calculate_consumption_for_multiple_objects,
    calculate_consumption_for_one_object,
)

from settings import app_logger, CONF


def _mk_handler(func: dpg.Callable, *args, **kwargs):
    def _(sender, app_data):
        func(*args, **kwargs)
    return _


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


def clear_viewport():
    dpg.set_primary_window("root_win", False)
    dpg.delete_item("root_win")


def quit():
    dpg.stop_dearpygui()


def _autosave():
    import time
    import datetime

    now_ = int(time.mktime(datetime.datetime.now().timetuple()))

    if (now_ - APP_CONTEXT["LAST_SAVE"]) > 10:
        UPI.dump()
        app_logger.debug("autosave")
        APP_CONTEXT["LAST_SAVE"] = now_


def show_error(message: str):
    with dpg.window(modal=True, no_resize=True, tag="error_modal"):
        dpg.add_text(message)


def create_report(project_ctx: ProjectContext, variant: str):
    import datetime
    dt_now = datetime.datetime.now().strftime("%d.%m.%Y")
    report_fname = f"Отчет по водопотреблению {dt_now}"

    from tkinter import Tk
    from tkinter.filedialog import asksaveasfilename

    Tk().withdraw()
    fpath = asksaveasfilename(
        initialdir=PROJECT_ROOT,
        initialfile=report_fname,
    )

    try:
        prepare_latex(fpath, project_ctx, variant)
    except OSError:
        show_error("Операционная система не поддерживает компиляцию в LaTeX. Мы работаем над этим ;)")
    except TypeError:
        show_error("Водопотребители не добавлены. Отсутствуют данные для отчета")
    except StopSignal:
        show_error("Документ успешно сохранен")
    except:
        show_error("Ошибка сборки документа")


def draw_consumer_card(
    parent: int | str,
    variant: str,
    project_ctx: ProjectContext,
    draw_only: bool = False,
    card: WaterConsumerNorms | None = None,
    card_num_of_visitors: int | None = None,
):
    consumer_type = dpg.get_value(f"{variant}_consumer_value")
    cons: WaterConsumerNorms = APP_CONTEXT["WATER_CONSUMERS"][consumer_type]
    cons.upd_id()

    num_of_devices_less_200 = dpg.get_value(f"{variant}_num_of_devices_check_value")
    num_of_devices = dpg.get_value(f"{variant}_num_of_devices_input_value")
    num_of_devices_hot = dpg.get_value(f"{variant}_num_of_devices_hot_input")
    num_of_measurers = dpg.get_value(f"{variant}_num_of_measurers_input_value")
    temp_hot = dpg.get_value(f"{variant}_temp_hot")
    temp_cold = dpg.get_value(f"{variant}_temp_cold")
    work_hours = dpg.get_value(f"{variant}_work_hours")

    if card is not None:
        if card_num_of_visitors is None:
            return
        num_of_measurers = card_num_of_visitors
        cons: WaterConsumerNorms = card

    if num_of_measurers <= 0:
        show_error("Количество измерителей не может равняться 0")
        return

    def _delcons():
        _, win = APP_CONTEXT["CHOOSEN_CONSUMERS"][cons.id]
        del APP_CONTEXT["CHOOSEN_CONSUMERS"][cons.id]
        dpg.delete_item(win)
        dpg.delete_item(f"spacer_{cons.id}")
        # TODO: THIS ID DOESNT WORK
        project_ctx.remove_consumer(variant, cons)

    if not draw_only:
        project_ctx.add_variant_object(
            variant,
            cons,
            num_of_measurers,
            num_of_devices,
            num_of_devices_hot,
            temp_hot,
            temp_cold,
            work_hours,
            num_of_devices_less_200
        )

    with dpg.child_window(parent=parent, height=660, width=460) as cwin:
        with dpg.group(horizontal=True):
            dpg.add_button(label="X", callback=_mk_handler(_delcons))
            dpg.add_separator(label=cons.name)

        dpg.add_spacer(height=3)
        dpg.add_text(f"ID: {cons.id}")

        dpg.add_spacer(height=3)
        dpg.add_text(f"Количество измерителей: {num_of_measurers}")
        dpg.add_text(f"Количество приборов всего: {num_of_devices}")
        dpg.add_text(f"Количество приборов горячей воды: {num_of_devices_hot}")

        dpg.add_spacer(height=10)
        dpg.add_text("Норма расхода воды")

        dpg.add_spacer(height=10)
        dpg.add_text("Среднесуточное потребление: ")
        dpg.add_text(f"Общая (в том числе горячей) q^tot_u: {cons.avg_hot_and_cold_water_norms_per_day}")
        dpg.add_text(f"Горячей qhu: {cons.avg_hot_water_norms_per_day}")

        dpg.add_spacer(height=10)
        dpg.add_text("В час наибольшего потребления")
        dpg.add_text(f"Общая (в том числе горячей) q_tothr,u: {cons.max_hot_and_cold_water_norms_per_hour}")
        dpg.add_text(f"Горячей qhhr,u: {cons.max_hot_water_norms_per_hour}")

        dpg.add_spacer(height=10)
        dpg.add_text(f"Расход воды прибором, л/с (л/ч)")
        dpg.add_text(f"Общий (холодной и горячей) qtoto: {cons.device_water_consumption_hot_and_cold_q0tot} ({cons.device_water_consumption_hot_and_cold_q0tot_hr})")
        dpg.add_text(f"Холодной или горячей: {cons.device_water_consumption_hot_or_cold_q0} ({cons.device_water_consumption_hot_or_cold_q0_hr})")

        dpg.add_spacer(height=10)
        dpg.add_text(f"Температура горячей воды: {temp_hot}")
        dpg.add_text(f"Температура холодной воды: {temp_cold}")

        dpg.add_spacer(height=10)
        dpg.add_text(f"Рабочие часы в сутках: {work_hours}")

        dpg.add_spacer(height=10)
        dpg.add_text(f"Т,ч: {cons.T}")

    dpg.add_spacer(parent=parent, height=10, tag=f"spacer_{cons.id}")

    APP_CONTEXT["CHOOSEN_CONSUMERS"][cons.id] = cons, cwin


def variant_screen(parent_tab: str, project_ctx: ProjectContext):
    def mark_num_of_devices():
        enable: bool = dpg.get_value(f"{parent_tab}_num_of_devices_check_value")
        print(enable)
        if enable is True:
            dpg.disable_item(f"{parent_tab}_num_of_devices_input")
            dpg.disable_item(f"{parent_tab}_num_of_devices_hot_input")
        else:
            dpg.enable_item(f"{parent_tab}_num_of_devices_hot_input")
            dpg.enable_item(f"{parent_tab}_num_of_devices_input")
    

    def _update_alphas_and_make_report(data_report: OneObjectDataReport | MultipleObjectsDataReport, project_ctx: ProjectContext, variant: str):
        if isinstance(data_report, OneObjectDataReport):
            data_report.seconds_report.alpha_total = dpg.get_value(f"{parent_tab}_preedit_oo_seconds_alpha_tot")
            data_report.seconds_report.alpha_hot = dpg.get_value(f"{parent_tab}_preedit_oo_seconds_alpha_hot")
            data_report.seconds_report.alpha_cold = dpg.get_value(f"{parent_tab}_preedit_oo_seconds_alpha_cold")
            data_report.hours_max_report.alpha_total = dpg.get_value(f"{parent_tab}_preedit_oo_max_hour_alpha_tot")
            data_report.hours_max_report.alpha_hot = dpg.get_value(f"{parent_tab}_preedit_oo_max_hour_alpha_hot")
            data_report.hours_max_report.alpha_cold = dpg.get_value(f"{parent_tab}_preedit_oo_max_hour_alpha_cold")
        else:
            data_report.seconds_consumption.alpha_tot = dpg.get_value(f"{parent_tab}_preedit_mo_seconds_alpha_tot")
            data_report.seconds_consumption.alpha_h = dpg.get_value(f"{parent_tab}_preedit_mo_seconds_alpha_hot")
            data_report.seconds_consumption.alpha_c = dpg.get_value(f"{parent_tab}_preedit_mo_seconds_alpha_cold")
            data_report.hours_consumption.alpha_hr_tot = dpg.get_value(f"{parent_tab}_preedit_mo_hour_alpha_tot")
            data_report.hours_consumption.alpha_hr_h = dpg.get_value(f"{parent_tab}_preedit_mo_hour_alpha_hot")
            data_report.hours_consumption.alpha_hr_c = dpg.get_value(f"{parent_tab}_preedit_mo_hour_alpha_cold")
        
        create_report(project_ctx, variant)
        dpg.delete_item("preedit_modal")
    
    def show_report_modal():
        viewport_width = dpg.get_viewport_client_width()
        viewport_height = dpg.get_viewport_client_height()

        modal_width = 450
        modal_height = 400
    
        objects = project_ctx.get_variant_objects(parent_tab)
        if len(objects) == 0:
            show_error("Отсутствуют объекты для расчета")

        if len(objects) > 1:
            data_report = calculate_consumption_for_multiple_objects(objects)
        else:
            data_report = calculate_consumption_for_one_object(objects[0])
        
        def rd(d: Decimal) -> float:
            return float(d.quantize(Decimal(".001"), rounding=ROUND_UP))
        
        try:
            with dpg.value_registry():
                if isinstance(data_report, OneObjectDataReport):
                    print(rd(data_report.seconds_report.alpha_total))
                    dpg.add_float_value(default_value=data_report.seconds_report.alpha_total, tag=f"{parent_tab}_preedit_oo_seconds_alpha_tot")
                    dpg.add_float_value(default_value=data_report.seconds_report.alpha_hot, tag=f"{parent_tab}_preedit_oo_seconds_alpha_hot")
                    dpg.add_float_value(default_value=data_report.seconds_report.alpha_cold, tag=f"{parent_tab}_preedit_oo_seconds_alpha_cold")
                    dpg.add_float_value(default_value=data_report.hours_max_report.alpha_total, tag=f"{parent_tab}_preedit_oo_max_hour_alpha_tot")
                    dpg.add_float_value(default_value=data_report.hours_max_report.alpha_hot, tag=f"{parent_tab}_preedit_oo_max_hour_alpha_hot")
                    dpg.add_float_value(default_value=data_report.hours_max_report.alpha_cold, tag=f"{parent_tab}_preedit_oo_max_hour_alpha_cold")
                else:
                    dpg.add_float_value(default_value=data_report.seconds_consumption.alpha_tot, tag=f"{parent_tab}_preedit_mo_seconds_alpha_tot")
                    dpg.add_float_value(default_value=data_report.seconds_consumption.alpha_h, tag=f"{parent_tab}_preedit_mo_seconds_alpha_hot")
                    dpg.add_float_value(default_value=data_report.seconds_consumption.alpha_c, tag=f"{parent_tab}_preedit_mo_seconds_alpha_cold")
                    dpg.add_float_value(default_value=data_report.hours_consumption.alpha_hr_tot, tag=f"{parent_tab}_preedit_mo_hour_alpha_tot")
                    dpg.add_float_value(default_value=data_report.hours_consumption.alpha_hr_h, tag=f"{parent_tab}_preedit_mo_hour_alpha_hot")
                    dpg.add_float_value(default_value=data_report.hours_consumption.alpha_hr_c, tag=f"{parent_tab}_preedit_mo_hour_alpha_cold")
        except Exception as err:
            app_logger.warning(str(err))


        with dpg.window(
            label="Предварительный просмотр расчетов",
            width=modal_width,
            height=modal_height,
            modal=True,
            pos=[viewport_width // 2 - modal_width // 2, viewport_height // 3],
            tag="preedit_modal"
        ):
            if isinstance(data_report, OneObjectDataReport):
                dpg.add_text("Общий секундный расход")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"P_tot = {rd(data_report.seconds_report.P_total)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_oo_seconds_alpha_tot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"P_h = {rd(data_report.seconds_report.P_hot)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_oo_seconds_alpha_hot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"P_c = {rd(data_report.seconds_report.P_cold)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_oo_seconds_alpha_cold", width=150)
                dpg.add_spacer(height=10)
                dpg.add_text("Максимальный часовой расход")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Phr_tot = {rd(data_report.hours_max_report.P_total)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_oo_max_hour_alpha_tot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Phr_h = {rd(data_report.hours_max_report.P_hot)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_oo_max_hour_alpha_hot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"Phr_c = {rd(data_report.hours_max_report.P_cold)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_oo_max_hour_alpha_cold", width=150)
            else:
                dpg.add_text("Общий секундный расход")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"NP_tot = {rd(data_report.seconds_consumption.NPs_tot_sum)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_mo_seconds_alpha_tot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"NP_h = {rd(data_report.seconds_consumption.NPs_h_sum)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_mo_seconds_alpha_hot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"NP_c = {rd(data_report.seconds_consumption.NPs_c_sum)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_mo_seconds_alpha_cold", width=150)
                dpg.add_spacer(height=10)
                dpg.add_text("Общий часовой расход")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"NP_tot = {rd(data_report.hours_consumption.NPhrs_tot_sum)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_mo_hour_alpha_tot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"NP_h = {rd(data_report.hours_consumption.NPhrs_h_sum)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_mo_hour_alpha_hot", width=150)
                with dpg.group(horizontal=True):
                    dpg.add_text(f"NP_c = {rd(data_report.hours_consumption.NPhrs_c_sum)} -> alpha = ")
                    dpg.add_input_float(source=f"{parent_tab}_preedit_mo_hour_alpha_cold", width=150)

            dpg.add_spacer(height=20)
            dpg.add_button(
                label="Сохранить",
                height=30, width=-1,
                callback=_mk_handler(
                    _update_alphas_and_make_report,
                    data_report=data_report,
                    project_ctx=project_ctx,
                    variant=parent_tab
                )
            )

    with dpg.value_registry():
        dpg.add_string_value(default_value="23 Бани: душевая кабина", tag=f"{parent_tab}_consumer_value")

        dpg.add_bool_value(default_value=False, tag=f"{parent_tab}_num_of_devices_check_value")
        dpg.add_int_value(default_value=1, tag=f"{parent_tab}_num_of_devices_input_value")
        dpg.add_int_value(default_value=1, tag=f"{parent_tab}_num_of_devices_hot_input_value")

        dpg.add_int_value(default_value=1, tag=f"{parent_tab}_num_of_measurers_input_value")

        dpg.add_int_value(default_value=5, tag=f"{parent_tab}_temp_cold")
        dpg.add_int_value(default_value=61, tag=f"{parent_tab}_temp_hot")

        dpg.add_int_value(default_value=12, tag=f"{parent_tab}_work_hours")

    with dpg.group(horizontal=True, parent=parent_tab) as mwin:
        with dpg.child_window(width=APP_CONTEXT["LEFT_CHILD_WIN_W"], border=False):
            with dpg.child_window(border=False):
                dpg.add_text("Тип потребителя")

                dpg.add_combo(
                    items=list(APP_CONTEXT["WATER_CONSUMERS"].keys()),
                    source=f"{parent_tab}_consumer_value",
                    height_mode=10,
                    width=480
                )

                dpg.add_spacer(height=10)
                dpg.add_text("Количество измерителей")
                print(f"{parent_tab}_num_of_measurers_input")
                dpg.add_input_int(
                    min_clamped=True,
                    tag=f"{parent_tab}_num_of_measurers_input",
                    source=f"{parent_tab}_num_of_measurers_input_value")
                dpg.add_spacer(height=10)
                with dpg.group(horizontal=True):
                    dpg.add_text("Количество приборов всего")
                    dpg.add_checkbox(
                        label="> 200",
                        callback=mark_num_of_devices,
                        tag=f"{parent_tab}_num_of_devices_checkbox",
                        source=f"{parent_tab}_num_of_devices_check_value")
                dpg.add_input_int(
                    min_clamped=True,
                    tag=f"{parent_tab}_num_of_devices_input",
                    source=f"{parent_tab}_num_of_devices_input_value")
                dpg.add_spacer(height=5)
                dpg.add_text("Количество приборов горячей воды")
                dpg.add_input_int(
                    min_clamped=True,
                    tag=f"{parent_tab}_num_of_devices_hot_input",
                    source=f"{parent_tab}_num_of_devices_hot_input_value")
                dpg.add_spacer(height=5)
                dpg.add_text("Температура горячей воды")
                dpg.add_input_int(
                    min_clamped=True,
                    tag=f"{parent_tab}_temp_hot_input",
                    source=f"{parent_tab}_temp_hot")
                dpg.add_spacer(height=5)
                dpg.add_text("Температура холодной воды")
                dpg.add_input_int(
                    min_clamped=True,
                    tag=f"{parent_tab}_temp_cold_input",
                    source=f"{parent_tab}_cold_hot")
                dpg.add_spacer(height=5)
                dpg.add_text("Время работы в сутки (ч)")
                dpg.add_input_int(
                    min_clamped=True,
                    tag=f"{parent_tab}_work_hours_input",
                    source=f"{parent_tab}_work_hours")

                dpg.add_spacer(height=10)

                with dpg.group(horizontal=True):
                    dpg.add_button(
                        label="Добавить",
                        height=30, width=240,
                        callback=_mk_handler(
                            draw_consumer_card,
                            f"right_var_win_{parent_tab}",
                            parent_tab,
                            project_ctx,
                        )
                    )

                    dpg.add_button(
                        label="Сформировать отчет",
                        height=30, width=240,
                        # callback=_mk_handler(
                        #     create_report,
                        #     project_ctx=project_ctx,
                        #     variant=parent_tab
                        # )
                        callback=_mk_handler(
                            show_report_modal
                        )
                    )

            with dpg.child_window(parent=mwin, tag=f"right_var_win_{parent_tab}", border=False) as cw:
                dpg.add_text("Добавленные потребители:", parent=cw)
                for object_ in project_ctx.variants_data[parent_tab]["objects"]:
                    card = APP_CONTEXT["WATER_CONSUMERS"][object_["name"]]
                    card.id = object_["id"]
                    draw_consumer_card(
                        parent=f"right_var_win_{parent_tab}",
                        variant=parent_tab,
                        project_ctx=project_ctx,
                        card=card,
                        card_num_of_visitors=object_["num_of_measurers"],
                        draw_only=True,
                    )

        with dpg.theme() as container_theme:
            with dpg.theme_component(dpg.mvGroup):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (100, 0, 240), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ModalWindowDimBg, (255, 0, 0), category=dpg.mvThemeCat_Core)

            dpg.bind_item_theme(cw, container_theme)


def project_screen(project_path: str, pctx: ProjectContext):
    APP_CONTEXT["CURRENT_WIN"] = "project"
    APP_CONTEXT["CURRENT_PROJECT_PATH"] = project_path

    def add_variant_button():
        pctx.last_var_num = pctx.last_var_num + 1
        pctx.vars = pctx.vars + [f"вариант_{pctx.last_var_num}"]

        dpg.add_button(
            label=f"вариант {pctx.last_var_num}",
            tag=f"var_win_{pctx.last_var_num}",
            width=150, height=100, parent="vars_hor",
            callback=_mk_tab_opnr(f"var_win_вариант_{pctx.last_var_num}")
        )

    def open_variant_tab(tabname: str, open_tabs_on_startup: bool = False):
        if not open_tabs_on_startup:
            for tname, tid in pctx.opened_tabs_tags.items():
                if not dpg.is_item_visible(tid):
                    dpg.delete_item(tid)
                    pctx.rm_tab(tname)

        if not open_tabs_on_startup:
            if tabname not in pctx.opened_tabs_tags:
                label = "Вариант" + tabname.split("_")[-1]

                dpg.add_tab(parent="project_bar", label=label, tag=f"tab_{tabname}", closable=True)
                pctx.add_variant(f"tab_{tabname}")

                tab_id = dpg.get_item_children("project_bar")[1][-1] # type:ignore
                pctx.add_tab(tabname, tab_id)

                variant_screen(f"tab_{tabname}", pctx)
        else:
            label = "Вариант" + tabname.split("_")[-1]
            dpg.add_tab(parent="project_bar", label=label, tag=f"tab_{tabname}", closable=True)

            tab_id = dpg.get_item_children("project_bar")[1][-1] # type:ignore
            pctx.add_tab(tabname, tab_id)

            variant_screen(f"tab_{tabname}", pctx)
    
    def _mk_tab_opnr(nm: str):
        app_logger.debug(nm)
        def _open():
            open_variant_tab(nm)
        return _open
    
    with dpg.window(
        label="Водопотребление",
        width=APP_CONTEXT["WIN_W"],
        height=APP_CONTEXT["WIN_H"],
        autosize=True,
        on_close=_mk_handler(quit),
        tag="root_win"
    ):
        tb = dpg.add_tab_bar(reorderable=True, tag="project_bar")
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
        
        for tab in pctx.opened_tabs_tags.keys():
            open_variant_tab(tab, open_tabs_on_startup=True)

    dpg.set_primary_window("root_win", True)


def main_screen():
    APP_CONTEXT["CURRENT_WIN"] = "main"

    def create_project_button_handler():
        from tkinter import Tk
        from tkinter.filedialog import asksaveasfilename

        Tk().withdraw()
        fpath = asksaveasfilename(
            defaultextension="wcp",
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
            defaultextension="wcp",
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


def _startup():
    dpg.create_context()
    dpg.create_viewport(
        title=f'waterconsumption v{__version__}',
        width=APP_CONTEXT["WIN_W"],
        max_width=APP_CONTEXT["WIN_W"] + 100,
        max_height=APP_CONTEXT["WIN_H"] + 100,
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

        font_path = os.path.join(CONF.ASSETS_FOLDER, "notomono-regular.ttf")
        app_logger.debug(f"FONT: {font_path}")
       
        with dpg.font(font_path, 18, default_font=True, tag="font-ru"):
            dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
            dpg.bind_font("font-ru")


def _finalize():
    dpg.setup_dearpygui()
    dpg.set_viewport_small_icon("./icon.ico")
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