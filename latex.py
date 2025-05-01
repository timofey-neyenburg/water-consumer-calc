import datetime
from fileinput import filename
import logging
from os import PathLike
import threading

from pathlib import Path

from data import PROJECT_ROOT
from mathematics import WaterConsumerNorms
from settings import app_logger



def _build_document_top(images_path: str = './', header_image_name: str = "header.png"):
    txt = (
        "\\documentclass{article} \n"
        "\\usepackage[T2A]{fontenc} \n"
        "\\usepackage[russian,english]{babel} \n"
        "\\usepackage[margin=1.5cm]{geometry} \n"
        "\\usepackage{multirow} \n"
        "\\usepackage{times} \n"
        "\\usepackage{graphicx} \n"
        "\\graphicspath{ {" + images_path + "} } \n\n"
        "\\includegraphics[width=18cm, height=5cm]{" + header_image_name + "} \n\n"
        "\\begin{document} \n"
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


def _build_document_objects_list(objects: list[tuple[str, int, str]]) -> str:
    txt = ""
    for ind, (name, num_of_measurers, measurer) in enumerate(objects):
        txt += (
            f"{ind+1}. {name} - {num_of_measurers} {measurer} \\\\ \n"
        )
    txt += "\n"
    return txt


def _build_objects_info_table(objects: list[WaterConsumerNorms]) -> str:
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

    for obj in objects:
        table += """
\\multicolumn{1}{|p{3cm}|}{<name>} & \n 
\\multicolumn{1}{ p{1cm}|}{<>} & \n 
\\multicolumn{1}{ p{1cm}|}{<>} & \n 
\\multicolumn{1}{ p{1cm}|}{<>} & \n
\\multicolumn{1}{ p{1cm}|}{<>} & \n
\\multicolumn{1}{ p{1cm}|}{<>} & \n
\\multicolumn{1}{ p{1cm}|}{<>} & \n
\\multicolumn{1}{ p{3cm}|}{<>} & \n 
\\multicolumn{1}{ p{2cm}|}{<>}  \n \\\\ 
\\hline
""".replace("<name>", obj.name)

    table += table_bottom
    
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
        "$q^{tot} = 5 \\cdot q_0 \\cdot \\varalpha$, л/с \n"
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


def build_document_text(
    project_name: str = "Предложение по застройке территории на правом берегу реки Иртыш в г.Омске.",
    objects: list[tuple[str, int, str]] = [("Жилая часть", 14507, "чел.")],
    norms: list[WaterConsumerNorms] = [],
):
    document = (
        _build_document_top()
        + _build_doc_header(project_name)
        + _build_document_objects_list(objects)
        + _build_objects_info_table(norms)
        + _build_sec_calculations()
        + _build_document_end()
    )

    return document


def prepare_latex(filepath: str, use_thread: bool = True, **params):
    import os
    file_dir = Path(filepath).parent

    filename_without_extention = os.path.basename(filepath)
    if filename_without_extention.endswith(".tex"):
        filename_without_extention = filename_without_extention[:-4]

    if not filepath.endswith(".tex"):
        filepath += ".tex"
    
    document_text = build_document_text()

    def _run():
        from subprocess import run, DEVNULL
        from sys import stdout, stderr
        from shutil import move

        if app_logger.level == logging.DEBUG:
            stdout_ = stdout
            stderr_ = stderr
        else:
            stdout_ = DEVNULL
            stderr_ = DEVNULL
        
        LATEX_OUTPUT_FILES_TEMP_DIR: PathLike = Path(PROJECT_ROOT) / "tex_temp"
        if not os.path.exists(LATEX_OUTPUT_FILES_TEMP_DIR):
            os.makedirs(LATEX_OUTPUT_FILES_TEMP_DIR)

        temp_tex_filepath = str(LATEX_OUTPUT_FILES_TEMP_DIR / f"{filename_without_extention}.tex")
        with open(temp_tex_filepath, "w", encoding="utf-8") as f:
            f.write(document_text)

        # command = ['pdflatex', '--interaction=nonstopmode', filepath]
        # command = ["C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe", '--interaction=nonstopmode', temp_tex_filepath]
        command = [
            r".\bin\windows\pdflatex.exe",
            '--interaction=nonstopmode',
            temp_tex_filepath
        ]
        print(command)

        app_logger.debug("starting latex compilation")
        r = run(
            command,
            stdout=stdout_,
            stderr=stderr_,
            # cwd=LATEX_OUTPUT_FILES_TEMP_DIR,
            cwd=r".\assets\tex-minimal",
            shell=True,
        )
        app_logger.debug("finished latex compilation")
        print("ERROR" if r.returncode == 1 else "OK")
        return

        app_logger.debug("moving pdf file")
        move(
            LATEX_OUTPUT_FILES_TEMP_DIR / f"{filename_without_extention}.pdf",
            file_dir / f"{filename_without_extention}.pdf",
        )
        app_logger.debug("done moving pdf file")

        app_logger.debug("removing trash files")
        for file in os.listdir(LATEX_OUTPUT_FILES_TEMP_DIR):
            if file.endswith((".log", ".aux", ".tex")):
                os.remove(LATEX_OUTPUT_FILES_TEMP_DIR / file)
        app_logger.debug("done trash files")


    if use_thread:
        threading.Thread(target=_run, daemon=True).start()
    else:
        _run()


with open("C:\\Users\\neyen\\OneDrive\\Рабочий стол\\e.tex", "w", encoding="utf-8") as f:
    f.write(build_document_text())
# prepare_latex("C:\\Users\\neyen\\OneDrive\\Рабочий стол\\e.tex", use_thread=False)