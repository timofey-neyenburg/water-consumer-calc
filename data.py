__all__ = [
    "APP_CONTEXT",
    "get_water_consumer_norm_by_name",
    "set_num_of_visitors"
]


import json
import os

from pathlib import Path

from settings import app_logger
from mathematics import WaterConsumerNorms, ConsuptionMeasurer


PROJECT_ROOT = str(Path(__file__).parent)


APP_CONTEXT = {
    "WIN_W": 1024,
    "WIN_H": 720,
    "LEFT_CHILD_WIN_W": 500,
    "CHOOSEN_CONSUMERS": {},
    "NUM_OF_VISITORS": 0,
    "CURRENT_CONSUMER": None,
    "CURRENT_PROJECT": None,
    "CURRENT_PROJECT_PATH": None,
    "CURRENT_WIN": "main",
    "LAST_SAVE": 0,
    "WATER_CONSUMERS": [
        WaterConsumerNorms(
            1, 
            "23 Бани: душевая кабина",
            ConsuptionMeasurer.ONE_INHABITANT,
            360, 200, 360, 200, 0.2, 0.14, 3
        ),
    ],
}

APP_CONTEXT["CURRENT_CONSUMER"] = APP_CONTEXT["WATER_CONSUMERS"][0]


def get_water_consumer_norm_by_name(name: str):
    index = [cons.name for cons in APP_CONTEXT["WATER_CONSUMERS"]].index(name)
    cons = APP_CONTEXT["WATER_CONSUMERS"][index]
    APP_CONTEXT["CURRENT_CONSUMER"] = cons


def set_num_of_visitors(d):
    APP_CONTEXT["NUM_OF_VISITORS"] = d


class UsersProjectsInfo:
    def __init__(
        self,
        users_projects_paths: list[str],
        last_opend_project: str | None = None,
    ):
        self.users_projects_paths = users_projects_paths
        self.last_opend_project = last_opend_project

    def _to_dict(self) -> dict:
        print(self)
        return {
            "users_projects_paths": self.users_projects_paths,
            "last_opend_project": self.last_opend_project,
        }
    
    @staticmethod
    def default() -> "UsersProjectsInfo":
        return UsersProjectsInfo(
            users_projects_paths=[],
        )
    
    @staticmethod
    def _from_dict(repr: dict) -> "UsersProjectsInfo":
        return UsersProjectsInfo(
            users_projects_paths=repr["users_projects_paths"],
            last_opend_project=repr["last_opend_project"],
        )
    
    def add_project(self, project_file_path: str):
        if project_file_path not in self.users_projects_paths:
            self.users_projects_paths.append(project_file_path)
        self.last_opend_project = project_file_path
        self.dump()

    def set_last_opend_project(self, project: str):
        self.last_opend_project = project
    
    def clear_paths(self):
        for path in self.users_projects_paths.copy():
            if not os.path.exists(path):
                self.users_projects_paths.remove(path)
    
    def dump(self):
        import json
        with open("./upi.json", "w") as f:
            json.dump(self._to_dict(), f, indent=4)

    @staticmethod
    def load() -> "UsersProjectsInfo":
        import json
        with open("./upi.json", "r") as f:
            raw_ = json.load(f)
        return UsersProjectsInfo._from_dict(raw_)

try:
    UPI = UsersProjectsInfo.load()
    UPI.clear_paths()
except Exception as err:
    print(f"unable to load profiles config: {err}")
    print("creating a default profiles config")
    UPI = UsersProjectsInfo.default()
    UPI.dump()



class ProjectContext:
    def __init__(self, path: str, data: dict) -> None:
        app_logger.error("PROJECT CONTEXT")
        self._path = path
        self._data = data
    
    def is_loaded(self):
        return "vars" in self._data

    @staticmethod
    def load(path: str):
        with open(path) as f:
            _data = json.load(f)
        return ProjectContext(path, _data)
    
    @staticmethod
    def new(path: str) -> "ProjectContext":
        app_logger.error("NEW PROJECT CONTEXT")
        _data = {
            "path": path,
            "last_var_num": 0,
            "vars": [],
            "opened_tabs_tags": {},
            "variants_data": {},
        }
        app_logger.error(f"prepared app context data: {_data}")
        p = ProjectContext(path, _data)
        p.dump()
        app_logger.error("saved project data")
        return p
    
    @property
    def path(self):
        return self._data["path"]

    @path.setter
    def path(self, v: str):
        self._data["path"] = v
    
    @property
    def last_var_num(self):
        return self._data["last_var_num"]

    @last_var_num.setter
    def last_var_num(self, v: int):
        self._data["last_var_num"] = v

    @property
    def vars(self):
        return self._data["vars"]

    @vars.setter
    def vars(self, vars: list[str]):
        self._data["vars"] = vars

    @property
    def opened_tabs_tags(self):
        return self._data["opened_tabs_tags"]

    @property
    def variants_data(self):
        return self._data["variants_data"]

    def add_variant(self, tag: str):
        if tag not in self._data["variants_data"]:
            self._data["variants_data"][tag] = {"objects": []}
            self.dump()
    
    def add_tab(self, tab_name: str, tab_id: int):
        self._data["opened_tabs_tags"][tab_name] = tab_id
        self.dump()
    
    def rm_tab(self, tab_name: str):
        if tab_name in self._data["opened_tabs_tags"]:
            del self._data["opened_tabs_tags"][tab_name]
    
    def add_variant_object(self, variant_tag: str, object_type: str, object_type_id: int, num_of_object_visitors: int):
        if variant_tag in self._data["variants_data"]:
            cons: WaterConsumerNorms = APP_CONTEXT["WATER_CONSUMERS"][object_type_id-1]
            self._data["variants_data"][variant_tag]["objects"].append({
                "num_of_object_visitors": num_of_object_visitors,
                "params": {
                    "id": cons.id,
                    "name": cons.name,
                },
            })
        self.dump()
    
    def dump(self):
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=4)