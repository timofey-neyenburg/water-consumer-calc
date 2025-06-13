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


def prepare_latex(
    filepath: str,
    project_ctx: ProjectContext,
    variant: str,
    use_thread: bool = True,
):
    import os

    def _run(text: str):
        ...

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

    document_text = build_document_text(data_report) # type:ignore

    if use_thread:
        threading.Thread(target=_run, args=(document_text,), daemon=True).start()
    else:
        _run(document_text)
    

