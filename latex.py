import datetime
import logging
import threading

from pathlib import Path

from data import ProjectContext
from mathematics import (
    MultipleObjectsDataReport,
    OneObjectDataReport,
    WaterConsumerNorms,
    WaterConsumerParams,
    calculate_consumption_for_multiple_objects,
    calculate_consumption_for_one_object,
    _r, _d
)

from settings import CONF, app_logger


def prepare_latex(
    filepath: str,
    project_ctx: ProjectContext,
    variant: str,
    use_thread: bool = True,
):
    import os

    def _run(text: str):
        from subprocess import run
        from shutil import move

        capture_output = app_logger.level == logging.DEBUG
        
        cwd = CONF.TEX_COMPILER_DIR
        tex_fname = f"{filename_without_extention}.tex"
        tex_fname_ws_decoded = os.fsencode(tex_fname).decode()
        temp_tex_filepath = Path(cwd) / tex_fname

        with open(temp_tex_filepath, "w", encoding="utf-8") as f:
            f.write(text)

        command = ["pdflatex.exe", "--interaction=nonstopmode", tex_fname_ws_decoded]

        app_logger.debug(f"starting latex compilation: {command}")
        run(
            command,
            cwd=cwd,
            shell=True,
            capture_output=capture_output,
        )
        app_logger.debug("finished latex compilation")

        if not os.path.exists(Path(cwd) / f"{filename_without_extention}.pdf"):
            raise ValueError("Unable to compile document")

        app_logger.debug("moving pdf file")
        move(
            Path(cwd) / f"{filename_without_extention}.pdf",
            file_dir / f"{filename_without_extention}.pdf",
        )
        app_logger.debug("done moving pdf file")

        app_logger.debug("removing trash files")
        for file in os.listdir(cwd):
            if file.endswith((".log", ".aux")):#, ".tex")):
                os.remove(Path(cwd) / file)
        app_logger.debug("done trash files")

    file_dir = Path(filepath).parent

    filename_without_extention = os.path.basename(filepath)
    if filename_without_extention.endswith(".tex"):
        filename_without_extention = filename_without_extention[:-4]

    if not filepath.endswith(".tex"):
        filepath += ".tex"
    
    objects = project_ctx.get_variant_objects(variant)
    if len(objects) == 0:
        raise TypeError("Nothing to build")

    if len(objects) > 1:
        data_report = calculate_consumption_for_multiple_objects(objects)
    else:
        data_report = calculate_consumption_for_one_object(objects[0])

    document_text = build_document_text(data_report)

    if use_thread:
        threading.Thread(target=_run, args=(document_text,), daemon=True).start()
    else:
        _run(document_text)


def build_document_text(
    data_report: OneObjectDataReport | MultipleObjectsDataReport,
    project_name: str = "Предложение по застройке территории на правом берегу реки Иртыш в г.Омске.",
):
    if isinstance(data_report, OneObjectDataReport):
        print("BUILD ONE OBJ DOC")
        return _build_one_object_report(data_report, project_name)
    else:
        return _build_multiple_objects_report(data_report, project_name)
    

def _build_multiple_objects_report(report: MultipleObjectsDataReport, project_name: str) -> str:
    objects = report.consumers_params
    objects_norms = report.consumers

    document = (
        _build_document_top(ignore_img=True)
        + _build_doc_header(project_name)
        + _build_document_objects_list(objects)
        + _build_objects_info_table(objects)
        # multiple objects data
        + _build_document_end()
    )

    return document


def _build_one_object_report(report: OneObjectDataReport, project_name: str):
    objects = [report.consumer_params]
    objects_norms = [report.consumer]

    document = (
        _build_document_top(ignore_img=True)
        + _build_doc_header(project_name)
        + _build_document_objects_list(objects)
        + _build_objects_info_table(objects)
        + _build_one_object_seconds_calculation(report)
        + _build_one_object_hours_max_calculation(report)
        + _build_one_object_hours_avg_calculation(report)
        + _build_one_object_heat_consumption_calculation(report)
        + _build_one_object_total_day_calculation(report)
        + _build_one_object_total_result_table(report)
        + _build_document_end()
    )

    return document



def _build_one_object_total_day_calculation(report: OneObjectDataReport) -> str:
    txt = "\\\\ \n"
    txt += "\\section*{\\textbf{Общий суточный расход:}} \\\\ \n"
    txt += f"{report.consumer.name} \\\\ \n"
    txt += (
        "$Q_u^{tot} = <a> \\cdot <b> \\cdot <c> / 1000 = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.avg_hot_and_cold_water_norms_per_day)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        # TODO: MAGIC NUMBER
        .replace("<c>", str(_r(4)))
        .replace("<d>", str(_r(report.total_day_report.Q_total)))
    )
    txt += "\\\\ \n"
    txt += (
        "$Q_u^{h} = <a> \\cdot <b> \\cdot <c> / 1000 = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.avg_hot_water_norms_per_day)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        # TODO: MAGIC NUMBER
        .replace("<c>", str(_r(4)))
        .replace("<d>", str(_r(report.total_day_report.Q_hot)))
    )
    txt += "\\\\ \n"
    txt += (
        "$Q_u^{c} = <a> \\cdot <b> \\cdot <c> / 1000 = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.avg_hot_and_cold_water_norms_per_day - report.consumer.avg_hot_water_norms_per_day)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        # TODO: MAGIC NUMBER
        .replace("<c>", str(_r(4)))
        .replace("<d>", str(_r(report.total_day_report.Q_cold)))
    )
    txt += "\\\\ \n"
    return txt


def _build_one_object_heat_consumption_calculation(report: OneObjectDataReport):
    txt = "\\\\ \n"
    txt += """
\\section*{\\textbf{Расход тепла}} \\\\ \n
Расход тепла QTh  (Qhhr), кВт, на приготовление горячей воды с учетом потерь тепла подающими и циркуляционными трубопроводами Qht следует определять \\\\ \n
\\noindent \n
а) в течение среднего часа  \\\\ \n
$Q^h_T = 1,16 \\cdot q^h_T \\cdot (t^h - t^c) + Q^{ht}$; \\\\ \n
\\noindent \n
б) в течение часа максимального водопотребления
$Q^h_{hr} = 1,16 \\cdot q^h_{hr} \\cdot (t^h - t^c) + Q^{ht}$; \\\\ \n
"""
    txt += "\\noindent \n"
    txt += f"{report.consumer.name} \\\\ \n"
    txt += "\\\\ \n"
    txt += (
        "$Q^h_T = 1,16 \\cdot <a> \\cdot (<b> - <c>) + <d> = <e>$; \\\\ \n"
        .replace("<a>", str(_r(report.hours_avg_report.q_hot)))
        # TODO: MAGIC NUMBER
        .replace("<b>", str(_r(61)))
        # TODO: MAGIC NUMBER
        .replace("<c>", str(_r(5)))
        .replace("<d>", str(_r(report.hours_max_report.q_hot * _d(0.3))))
        .replace("<e>", str(_r(report.heat_report.Q_avg_hour)))
    )
    txt += (
        "$Q^h_{hr} = 1,16 \\cdot <a> \\cdot (<b> - <c>) + <d> = <e>$; \\\\ \n"
        .replace("<a>", str(_r(report.hours_max_report.q_hot)))
        # TODO: MAGIC NUMBER
        .replace("<b>", str(_r(61)))
        # TODO: MAGIC NUMBER
        .replace("<c>", str(_r(5)))
        .replace("<d>", str(_r(report.hours_max_report.q_hot * _d(0.3))))
        .replace("<e>", str(_r(report.heat_report.Q_max_hour)))
    )

    txt += "\\\\ \n"

    return txt


def _build_one_object_hours_avg_calculation(report: OneObjectDataReport):
    txt = "\\\\ \n"

    txt += """
\\section*{\\textbf{Средний часовой расход воды}} \\\\ \n
Средний часовой расход воды qT (qTtot, qTh, qTc ), м3, за расчетное время водопотребления (сутки, смена) Т, ч, следует определять по формуле: \\\\ \n
$q_{T} = \\frac{\\sum_{1}^{i}{q_{u,i} \\cdot U_{i}}}{1000 \\cdot T} $ \\\\ \n
"""
    txt += "\\noindent \n"
    txt += f"{report.consumer.name} \\\\ \n"
    txt += "\\\\ \n"

    txt += (
        "$q_{T,0}^{tot} = \\frac{\\sum_{1}^{i}{<a> \\cdot <b>}}{1000 \\cdot <c>}  = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.avg_hot_and_cold_water_norms_per_day)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        .replace("<c>", str(_r(report.consumer.T)))
        .replace("<d>", str(_r(report.hours_avg_report.q_total)))
    )
    txt += "\\\\ \n"
    txt += (
        "$q_{T,0}^{h} = \\frac{\\sum_{1}^{i}{<a> \\cdot <b>}}{1000 \\cdot <c>}  = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.avg_hot_water_norms_per_day)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        .replace("<c>", str(_r(report.consumer.T)))
        .replace("<d>", str(_r(report.hours_avg_report.q_hot)))
    )
    txt += "\\\\ \n"
    txt += (
        "$q_{T,0}^{c} = \\frac{\\sum_{1}^{i}{<a> \\cdot <b>}}{1000 \\cdot <c>}  = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.avg_hot_and_cold_water_norms_per_day - report.consumer.avg_hot_water_norms_per_day)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        .replace("<c>", str(_r(report.consumer.T)))
        .replace("<d>", str(_r(report.hours_avg_report.q_cold)))
    )

    txt += "\\\\ \n"

    return txt


def _build_one_object_hours_max_calculation(report: OneObjectDataReport):
    txt = "\\\\ \n"

    txt += """
\\section*{\\textbf{Максимальный часовойрасход воды (стоков)}} \\\\ \n
\\noindent \n
Максимальный часовойрасход воды (стоков) qhr (qhrtot, qhhr, qhrc), м3, следует определять по формуле: \\\\ \n
$q_{hr} = 0,005 \\cdot q_{0,hr} \\cdot \\alpha_{hr}$ \\\\ \n
\\noindent \n
Вероятность использования санитарно-технических приборов ℎ для системы в целом следует определять по формуле \\\\ \n
$P_{hr} = \\frac{3600 \\cdot P \\cdot q_0}{q_{0,hr}}$ \\\\ \n
""" 
    txt += "\\noindent \n"
    txt += f"{report.consumer.name} \\\\ \n"
    txt += "\\\\ \n"
    txt += (
        "$P_{hr}^{tot} = \\frac{3600 \\cdot <a> \\cdot <b>}{<c>} = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.seconds_report.P_total)))
        .replace("<b>", str(_r(report.consumer.device_water_consumption_hot_and_cold_q0tot)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_and_cold_q0tot_hr)))
        .replace("<d>", str(_r(report.hours_max_report.P_total)))
    )
    txt += "\\\\ \n"
    txt += (
        "$P_{hr}^{h} = \\frac{3600 \\cdot <a> \\cdot <b>}{<c>} = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.seconds_report.P_hot)))
        .replace("<b>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0_hr)))
        .replace("<d>", str(_r(report.hours_max_report.P_hot)))
    )
    txt += "\\\\ \n"
    txt += (
        "$P_{hr}^{c} = \\frac{3600 \\cdot <a> \\cdot <b>}{<c>} = <d>$ \\\\ \n"
        .replace("<a>", str(_r(report.seconds_report.P_cold)))
        .replace("<b>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0_hr)))
        .replace("<d>", str(_r(report.hours_max_report.P_cold)))
    )
    txt += "\\\\ \n"
    txt += "По таблице Б.1 СП30.13330.2020 находим значение коэффициента $\\alpha$. \\\\ \n"
    txt += "\\\\ \n"
    txt += (
        "$P_{hr}^{tot} = <a> \\rightarrow \\alpha = <b> \\hspace{20px} q_{hr,0} = 0,005 \\cdot <c> \\cdot \\<d>$, м3/ч \\\\ \n"
        .replace("<a>", str(_r(report.hours_max_report.P_total)))
        .replace("<b>", str(_r(report.consumer.device_water_consumption_hot_and_cold_q0tot_hr)))
        .replace("<c>", str(_r(report.hours_max_report.alpha_total)))
        .replace("<d>", str(_r(report.hours_max_report.q_total)))
    )
    txt += "\\\\ \n"
    txt += (
        "$P_{hr}^{h} = <a> \\rightarrow \\alpha = <b> \\hspace{20px} q_{hr,0}^{h} = 0,005 \\cdot <c> \\cdot \\<d>$, м3/ч \\\\ \n"
        .replace("<a>", str(_r(report.hours_max_report.P_hot)))
        .replace("<b>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0_hr)))
        .replace("<c>", str(_r(report.hours_max_report.alpha_hot)))
        .replace("<d>", str(_r(report.hours_max_report.q_hot)))
    )
    txt += "\\\\ \n"
    txt += (
        "$P_{hr}^{c} = <a> \\rightarrow \\alpha = <b> \\hspace{20px} q_{hr,0}^{c} = 0,005 \\cdot <c> \\cdot \\<d>$, м3/ч \\\\ \n"
        .replace("<a>", str(_r(report.hours_max_report.P_cold)))
        .replace("<b>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0_hr)))
        .replace("<c>", str(_r(report.hours_max_report.alpha_cold)))
        .replace("<d>", str(_r(report.hours_max_report.q_cold)))
    )

    txt += "\\\\ \n"

    return txt


def _build_one_object_seconds_calculation(report: OneObjectDataReport):
    txt = "\\\\ \n"

    txt += """
\\section*{\\textbf{Общий секундный расход:}} \\\\ \n
\\noindent \n
Секундный расход воды различными приборами, обслуживающими разных водопотребителей, определяется по формуле 2 СП30.13330.2020 \\\\ \n
$q^{tot} = 5 \\cdot q_0 \\cdot \\alpha$, л/с \\\\ \n
\\noindent \n
Расчет начинаем с определения вероятности действия приборов различными потребителями: \\\\ \n
$P = q^{tot}_{hr,u} \\cdot U / (q_0 \\cdot N \\cdot 3600)$ \\\\ \n
\\\\ \n
\\noindent \n
"""
    txt += f"{report.consumer.name} \\\\ \n"
    txt += "\\\\ \n"
    txt += (
        "$P^{tot} = <a> \\cdot <b> / <c> \\cdot <d> \\cdot 3600 = <e>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.max_hot_and_cold_water_norms_per_hour)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_and_cold_q0tot)))
        .replace("<d>", str(_r(report.consumer_params.num_of_devices)))
        .replace("<e>", str(_r(report.seconds_report.P_total)))
    )
    txt += (
        "$P^{h} = <a> \\cdot <b> / <c> \\cdot <d> \\cdot 3600 = <e>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.max_hot_water_norms_per_hour)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0)))
        .replace("<d>", str(_r(report.consumer_params.num_of_devices_hot)))
        .replace("<e>", str(_r(report.seconds_report.P_hot)))
    )
    txt += (
        "$P^{h} = <a> \\cdot <b> / <c> \\cdot <d> \\cdot 3600 = <e>$ \\\\ \n"
        .replace("<a>", str(_r(report.consumer.max_hot_and_cold_water_norms_per_hour - report.consumer.max_hot_water_norms_per_hour)))
        .replace("<b>", str(_r(report.consumer_params.num_of_measurers)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0)))
        .replace("<d>", str(_r(report.consumer_params.num_of_devices - report.consumer_params.num_of_devices_hot)))
        .replace("<e>", str(_r(report.seconds_report.P_cold)))
    )
    txt += "\\\\ \n"
    txt += "Формула (3) СП30.13330.2020 По таблице Б.1 СП30.13330.2020 находим значение коэффициента $\\alpha$. \\\\ \n"
    txt += "\\\\ \n"
    txt += (
        "$P^{tot} = <a> \\rightarrow \\alpha = <b> \\hspace{20px} q^{tot} = 5 \\cdot <c> \\cdot <d> = <e>$, л/с \\\\ \n"
        .replace("<a>", str(_r(report.seconds_report.P_total)))
        .replace("<b>", str(_r(report.seconds_report.alpha_total)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_and_cold_q0tot)))
        .replace("<d>", str(_r(report.seconds_report.alpha_total)))
        .replace("<e>", str(_r(report.seconds_report.q_total)))
    )
    txt += (
        "$P^{h} = <a> \\rightarrow \\alpha = <b> \\hspace{20px} q^{h} = 5 \\cdot <c> \\cdot <d> = <e>$, л/с \\\\ \n"
        .replace("<a>", str(_r(report.seconds_report.P_hot)))
        .replace("<b>", str(_r(report.seconds_report.alpha_hot)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0)))
        .replace("<d>", str(_r(report.seconds_report.alpha_hot)))
        .replace("<e>", str(_r(report.seconds_report.q_hot)))
    )
    txt += (
        "$P^{c} = <a> \\rightarrow \\alpha = <b> \\hspace{20px} q^{c} = 5 \\cdot <c> \\cdot <d> = <e>$, л/с \\\\ \n"
        .replace("<a>", str(_r(report.seconds_report.P_cold)))
        .replace("<b>", str(_r(report.seconds_report.alpha_cold)))
        .replace("<c>", str(_r(report.consumer.device_water_consumption_hot_or_cold_q0)))
        .replace("<d>", str(_r(report.seconds_report.alpha_cold)))
        .replace("<e>", str(_r(report.seconds_report.q_cold)))
    )

    txt += "\\\\ \n"

    return txt


def _build_document_top(ignore_img: bool = False, images_path: str = './', header_image_name: str = "header.png"):
    txt = (
        "\\documentclass{article} \n"
        + "\\usepackage[T2A]{fontenc} \n"
        + "\\usepackage[russian,english]{babel} \n"
        + "\\usepackage[margin=1.5cm]{geometry} \n"
        + "\\usepackage{multirow} \n"
        + "\\usepackage{times} \n"
        + "\\usepackage{graphicx} \n"
        + (("\\graphicspath{ {" + images_path + "} } \n\n") if not ignore_img else "")
        + (("\\includegraphics[width=18cm, height=5cm]{" + header_image_name + "} \n\n") if not ignore_img else "")
        + "\\begin{document} \n"
    )

    return txt


def _build_doc_header(project_name: str) -> str:
    txt = (
        (
            "\\begin{center} \n"
            "\\section*{<project_name>}\\\\ \n"
            "\\end{center} \n"
            "\\begin{center} \n"
            "\\section*{Расчет расходов воды и стоков.}\\\\\\\\ \n"
            "\\end{center} \n"
            "Согласно задания на проектирование выполняем расчет расходов воды по СНиП 2.04.01-85 «Внутренний водопровод и канализация зданий».\\\\ \n\n"
        )
        .replace("<project_name>", project_name)
    )

    return txt


def _build_document_objects_list(objects: list[WaterConsumerParams]) -> str:
    txt = "\\begin{enumerate} \n"
    for ind, obj in enumerate(objects):
        txt += (
            f"\\item {obj.consumer_norms.name} - {obj.num_of_measurers} {obj.consumer_norms.measurer.value} \\\\ \n"
        )
    txt += "\\end{enumerate}\n"
    return txt


def _build_objects_info_table(objects: list[WaterConsumerParams]) -> str:
    # https://www.tablesgenerator.com/

    table = """
\\begin{table}[h] \n
\\begin{tabular}{|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|} \n
\\hline \n
    \\multicolumn{1}{|p{3cm}|}{ \n
        \\multirow{3}{3cm}{Водопотребители} \n
    }& \n
    \\multicolumn{1}{p{1cm}|}{ \n
        \\multirow{3}{1cm}{Изме ритель} \n
    }& \n
    \\multicolumn{1}{|p{1cm}|}{ \n
        \\multirow{3}{1cm}{Коли чество потре бите лей} \n
    }& \n
    \\multicolumn{4}{p{4cm}|}{Норма расхода воды, л}& \n
    \\multicolumn{2}{p{5cm}|}{Расход воды прибором, л/с (л/ч)} \\\\ \n
\\cline{4-9} \n
    \\multicolumn{1}{|p{1cm}|}{} & \n
    \\multicolumn{1}{p{1cm}|}{} & \n
    \\multicolumn{1}{p{1cm}|}{} & \n
    \\multicolumn{2}{p{2cm}|}{В сутки наибольшего потребления} & \n
    \\multicolumn{2}{p{2cm}|}{В час наибольшего потребления} & \n
    \\multicolumn{1}{p{3cm}|}{ \n
        \\multirow{2}{3cm}{Общий (холодной и горячей) $q^{tot}_o$ ($q^{tot}_{o, hr}$)} \n
    } & \n
    \\multicolumn{1}{p{2cm}|}{ \n
        \\multirow{2}{2cm}{Холодной или горячей $q^c_o$, $q^h_o$, $q^c_{o, hr}$, $q^h_{o, hr}$} \n
    } \\\\ \n
\\cline{4-7} \n
    \\multicolumn{1}{|p{1cm}|}{} & \n
    \\multicolumn{1}{p{1cm}|}{} & \n
    \\multicolumn{1}{p{1cm}|}{} & \n
    \\multicolumn{1}{p{1cm}|}{Общая (в том числе горя чей) $q^{tot}_u$} & \n
    \\multicolumn{1}{p{1cm}|}{Горя чей $q^h_u$} & \n
    \\multicolumn{1}{p{1cm}|}{Общая (в том числе горя чей) $q^{tot}_{hr, u}$} & \n
    \\multicolumn{1}{p{1cm}|}{Горя чей $q^{h}_{hr, u}$} & \n
    \\multicolumn{1}{p{1cm}|}{} & \n
    \\multicolumn{1}{p{1cm}|}{} \\\\ \n
\\hline
"""

    table_bottom = """
\\end{tabular} \n
\\end{table}\\textbf{} \n\n
"""

    table_row_base = """
\\multicolumn{1}{|p{3cm}|}{<a>} & \n 
\\multicolumn{1}{ p{1cm}|}{<b>} & \n 
\\multicolumn{1}{ p{1cm}|}{<c>} & \n 
\\multicolumn{1}{ p{1cm}|}{<d>} & \n
\\multicolumn{1}{ p{1cm}|}{<e>} & \n
\\multicolumn{1}{ p{1cm}|}{<f>} & \n
\\multicolumn{1}{ p{1cm}|}{<g>} & \n
\\multicolumn{1}{ p{3cm}|}{<h>} & \n 
\\multicolumn{1}{ p{2cm}|}{<i>}  \n \\\\ 
\\hline
"""

    print("BITCH")
    for obj in objects:
        try:
            table += (
                table_row_base
                .replace("<a>", obj.consumer_norms.name)
                .replace("<b>", obj.consumer_norms.measurer.value)
                .replace("<c>", str(obj.num_of_measurers))
                .replace("<d>", str(obj.consumer_norms.avg_hot_and_cold_water_norms_per_day))
                .replace("<e>", str(obj.consumer_norms.avg_hot_water_norms_per_day))
                .replace("<f>", str(obj.consumer_norms.max_hot_and_cold_water_norms_per_hour))
                .replace("<g>", str(obj.consumer_norms.max_hot_water_norms_per_hour))
                .replace("<h>", f"{obj.consumer_norms.device_water_consumption_hot_and_cold_q0tot} ({obj.consumer_norms.device_water_consumption_hot_and_cold_q0tot_hr})")
                .replace("<i>", f"{obj.consumer_norms.device_water_consumption_hot_or_cold_q0} ({obj.consumer_norms.device_water_consumption_hot_or_cold_q0_hr})")
            )
        except Exception as err:
            print(err.__class__, err)

    table += table_bottom
    print("BITCH END")
    
    txt = (
        "\\section*{Норма расхода воды}\\\\ \n"
        + table
    )
    return txt


def _build_sec_calculations() -> str:
    txt = (
        "\\begin{center} \n"
        "\\section*{Общий секундный расход:} \n"
        "\\end{center} \n"
        "Секундный расход воды  различными  приборами, обслуживающими разных водопотребителей, определяется по формуле 2 СНиП 2.04.01-85:\\\\ \n"
        "\\begin{center} \n"
        "$q^{tot} = 5 \\cdot q_0 \\cdot \\alpha$, л/с \n"
        "\\end{center} \n"
        "Расчет начинаем с определения вероятности действия приборов различными потребителями:\\\\ \n"
    )
    return txt


def _build_document_end() -> str:
    today = datetime.datetime.now().strftime("%m.%d.%Y")

    txt = (
        "\\vspace{2cm}\\\\ \n\n"
        "\\begin{tabular}{p{400pt}l}\n"
        "\\Large{Директор}     & \\Large{Исполнил}   \\\\ \n"
        "                      &                     \\\\ \n"
        "\\rule{40pt}{0.4pt}   & \\rule{40pt}{0.4pt} \\\\ \n"
        f"                     & {today}г.           \\\\ \n"
        "\\end{tabular}  \n\n"
        "\\end{document} \n"
    )

    return txt


def _build_one_object_total_result_table(report: OneObjectDataReport):
    table = """
\\\\ \n
\\begin{table}[h]
\\begin{tabular}{|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|m{1cm}|}
\\hline
    \\multicolumn{1}{|p{3cm}|}{
        \\multirow{3}{3cm}{Наименование системы}
    } &
    \\multicolumn{9}{|p{9cm}|}{Расчетный расход} \\\\
\\cline{2-10}
    \\multicolumn{1}{|p{3cm}|}{} & 
    \\multicolumn{3}{|p{3cm}|}{Общий расход воды} &
    \\multicolumn{3}{|p{3cm}|}{Расход холодной воды} &
    \\multicolumn{3}{|p{3cm}|}{Расход горячей воды} \\\\
\\cline{2-10}
    \\multicolumn{1}{|p{3cm}|}{} & 
    \\multicolumn{1}{|p{1cm}|}{м3/сут} & 
    \\multicolumn{1}{|p{1cm}|}{м3/ч} & 
    \\multicolumn{1}{|p{1cm}|}{л/с} & 
    \\multicolumn{1}{|p{1cm}|}{м3/сут} & 
    \\multicolumn{1}{|p{1cm}|}{м3/ч} & 
    \\multicolumn{1}{|p{1cm}|}{л/с} & 
    \\multicolumn{1}{|p{1cm}|}{м3/сут} & 
    \\multicolumn{1}{|p{1cm}|}{м3/ч} & 
    \\multicolumn{1}{|p{1cm}|}{л/с}  \\\\
\\hline
"""
    table_end = """
\\end{tabular}
\\end{table}
"""

    table_row_template = """
\\multicolumn{1}{|p{3cm}|}{<z>} & 
\\multicolumn{1}{|p{1cm}|}{<a>} & 
\\multicolumn{1}{|p{1cm}|}{<b>} & 
\\multicolumn{1}{|p{1cm}|}{<c>} & 
\\multicolumn{1}{|p{1cm}|}{<d>} & 
\\multicolumn{1}{|p{1cm}|}{<e>} & 
\\multicolumn{1}{|p{1cm}|}{<f>} & 
\\multicolumn{1}{|p{1cm}|}{<g>} & 
\\multicolumn{1}{|p{1cm}|}{<h>} & 
\\multicolumn{1}{|p{1cm}|}{<i>} \\\\
\\hline
"""

    table += (
        table_row_template
        .replace("<z>", "Хозяйственно-питьевой водопровод")
        .replace("<a>", str(_r(report.total_day_report.Q_total)))
        .replace("<b>", str(_r(report.hours_max_report.q_total)))
        .replace("<c>", str(_r(report.seconds_report.q_total)))
        .replace("<d>", str(_r(report.total_day_report.Q_hot)))
        .replace("<e>", str(_r(report.hours_max_report.q_hot)))
        .replace("<f>", str(_r(report.seconds_report.q_hot)))
        .replace("<g>", str(_r(report.total_day_report.Q_cold)))
        .replace("<h>", str(_r(report.hours_max_report.q_cold)))
        .replace("<i>", str(_r(report.seconds_report.q_cold)))
    )

    table += (
        table_row_template
        .replace("<z>", "Бытовая канализация")
        .replace("<a>", str(_r(report.total_day_report.Q_total)))
        .replace("<b>", str(_r(report.hours_max_report.q_total)))
        .replace("<c>", "")
        .replace("<d>", "")
        .replace("<e>", "")
        .replace("<f>", "")
        .replace("<g>", "")
        .replace("<h>", "")
        .replace("<i>", "")
    )

    table += table_end

    table += "\\\\ \n"

    return table