from fileinput import filename
import logging
from os import PathLike
import threading

from pathlib import Path

from data import PROJECT_ROOT
from settings import app_logger


DOC_TEMPLATE = r"""
\documentclass{article}
\usepackage[T2A]{fontenc}
\usepackage[russian,english]{babel}
\usepackage[margin=1.5cm]{geometry}

\begin{document}

    \section*{\textbf{Общий секундный расход:}} \\
    \textbf{Секундный расход воды различными приборами, обслуживающими разных водопотребителей, определяется по формуле (2) СП30.13330.2020} \\
    \\
        $q^{tot} = 5 \cdot q_0 \cdot \alpha$ \\
    \\
    \textbf{Расчет начинаем с определения вероятности действия приборов различными потребителями:} \\
    \textbf{Формула (3) СП30.13330.2020 По таблице Б.1 СП30.13330.2020 находим значение коэффициента \alpha.} \\
    \\
        $P = q^{tot}_{hr,u} \cdot U / (q_0 \cdot N \cdot 3600)$ \\
    \\
    <Название потребителя> \\
    <Название потребителя: приборы> \\
    \\
        ... ФОРМУЛЫ ... \\
    \\
    \section*{Максимальный часовой расход воды (стоков)}
    Максимальный часовой расход воды (стоков) $q_{hr} (q^{tot}_{hr}, q^{h}_{hr}, q^{h}_{cr})$ м3, следует определять по формуле: \\
    \\
        $q_{hr} = 0.005 \cdot q_{0, hr} \cdot \alpha_{hr}$ \\
    \\
    Вероятность использования санитарно-технических приборов $P_{hr}$ для системы в целом следует определять по формуле: \\
    \\
        $P_{hr} = (3600 \cdot P \cdot q_0) / (q_{0, hr})$ \\
    \\
    <Название потребителя> \\
    <Название потребителя: приборы> \\
    \\
        ... ФОРМУЛЫ ... \\
    \\
    \section*{Средний часовой расход воды}
    Средний часовой расход воды $q_{T} (q_{T}^{tot}, q_{T, h}, q_{T, c})$, м3, за расчетное время водопотребления (сутки, смена) Т, ч, следует определять по формуле: \\
    \\
        $q_{T} = \frac{\sum_1^i{q_{u,i}\cdot U_i}}{1000 \cdot T}$ \\
    \\
    <Название потребителя> \\
    \\
        ... ФОРМУЛЫ ... \\
    \\
    Расход тепла $Q_{T, h}  (Q_{h, hr})$, кВт, на приготовление горячей воды с учетом потерь тепла подающими и циркуляционными трубопроводами $Q_{h, t}$ следует определять: \\
    а) в течение среднего часа \\
    \\
        $Q_{T}^h = 1.16 \cdot q_T^h \cdot (t^h - t^c) + Q^{ht}$ \\
    \\
    б) в течение часа максимального водопотребления \\
    \\
        $Q_{hr}^{t} = 1.16 \cdot q_{hr}^h \cdot (t^h - t^c) + Q^{ht}$ \\
    \\
    <Название потребителя> \\
    \\
        ... ФОРМУЛЫ ... \\
    \\
    \section*{\textbf{Общий суточный расход:}} \\
    \\
        ... ФОРМУЛЫ ... \\
    \\

\end{document}
"""


def prepare_latex(filepath: str, use_thread: bool = True, **params):
    import os
    file_dir = Path(filepath).parent

    filename_without_extention = os.path.basename(filepath)
    if filename_without_extention.endswith(".tex"):
        filename_without_extention = filename_without_extention[:-4]

    if not filepath.endswith(".tex"):
        filepath += ".tex"

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
            f.write(format_string(DOC_TEMPLATE, params))

        # command = ['pdflatex', '--interaction=nonstopmode', filepath]
        # command = ["C:\\Program Files\\MiKTeX\\miktex\\bin\\x64\\pdflatex.exe", '--interaction=nonstopmode', temp_tex_filepath]
        command = [
            "C:\\Users\\neyen\\OneDrive\\Рабочий стол\\TinyTeX-1\\TinyTeX\\bin\\windows\\pdflatex.exe",
            '--interaction=nonstopmode',
            temp_tex_filepath
        ]

        app_logger.debug("starting latex compilation")
        run(
            command,
            stdout=stdout_,
            stderr=stderr_,
            cwd=LATEX_OUTPUT_FILES_TEMP_DIR,
            shell=True,
        )
        app_logger.debug("finished latex compilation")

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


def format_string(string: str, values: dict):
    return string


def build_document_text(
    project_name: str = "Предложение по застройке территории на правом берегу реки Иртыш в г.Омске.",
    objects: list[tuple[str, int, str]] = [("Жилая часть", 14507, "чел.")],
):
    txt = """
\\documentclass{article} \n\
\\usepackage[T2A]{fontenc} \n\
\\usepackage[russian,english]{babel} \n\
\\usepackage[margin=1.5cm]{geometry} \n\
\\usepackage{multirow} \n\
\\usepackage{times} \n\

\\begin{document} \n"""

    txt += (
        (
            "\\section*{<project_name>}\\\\ \n"
            "\\section*{Расчет расходов воды и стоков.}\\\\\\\\ \n"
            "Согласно задания на проектирование выполняем расчет расходов воды по СНиП 2.04.01-85 «Внутренний водопровод и канализация зданий».\\\\ \n"
        )
        .replace("<project_name>", project_name)
    )

    for ind, (name, num_of_measurers, measurer) in enumerate(objects):
        txt += (
            f"{ind+1}. {name} - {num_of_measurers} {measurer} \\\\ \n"
        )
    
    txt += "\\section*{Норма расхода воды}"

    # https://www.tablesgenerator.com/
    # \\begin{tabularx}{\\linewidth}{lllllllll} \n\
    txt += (
        """
\\begin{table}[h] \n\
\\begin{tabular}{p{2cm} llllllll} \n\
\\hline \n\
\\multicolumn{1}{p{2cm}}{
    \\multirow{3}{*}{Водопотребители}
} &
\\multicolumn{1}{l|}{
    \\multirow{3}{*}{Измеритель}
} &
\\multicolumn{1}{l|}{
    \\multirow{3}{*}{Количество потребителей}
} & 
\\multicolumn{4}{l|}{Норма расхода воды, л} &
\\multicolumn{2}{l|}{Расход воды прибором, л/с (л/ч)} \\\\ 
\\cline{4-9}  \n\
\\multicolumn{1}{|l|}{} &
\\multicolumn{1}{l|}{} & 
\\multicolumn{1}{l|}{} & 
\\multicolumn{2}{l|}{В сутки наибольшего потребления} & 
\\multicolumn{2}{l|}{В час наибольшего потребления} & 
\\multicolumn{1}{l|}{
    \\multirow{2}{*}{Общий (холодной и горячей) $q^{tot}_o$ ($q^{tot}_{o, hr}$)}
} & 
\\multicolumn{1}{l|}{
    \\multirow{2}{*}{Холодной или горячей $q^c_o$, $q^h_o$, $q^c_{o, hr}$, $q^h_{o, hr}$}
} \\\\ 
\\cline{4-7}  \n\
\\multicolumn{1}{|l|}{} & 
\\multicolumn{1}{l|}{} & 
\\multicolumn{1}{l|}{} & 
\\multicolumn{1}{l|}{Общая (в том числе горячей) $q^{tot}_u$} & 
\\multicolumn{1}{l|}{Горячей $q^h_u$} & 
\\multicolumn{1}{l|}{Общая (в том числе горячей) $q^{tot}_{hr, u}$} & 
\\multicolumn{1}{l|}{Горячей $q^{h}_{hr, u}$} & 
\\multicolumn{1}{l|}{} & 
\\multicolumn{1}{l|}{} \\\\ 
\\hline \n\
  & & & & & & & & \n
\\end{tabularx} \n\
\\end{table} \n\
"""
    )

    txt += "\\end{document} \n"

    return txt



# prepare_latex("C:\\Users\\neyen\\OneDrive\\Рабочий стол\\doc", use_thread=False)

with open("C:\\Users\\neyen\\OneDrive\\Рабочий стол\\e.tex", "w", encoding="utf-8") as f:
    f.write(build_document_text())