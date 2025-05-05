"""
СП 30.13330.2020
ВНУТРЕННИЙ ВОДОПРОВОД И КАНАЛИЗАЦИЯ ЗДАНИЙ
СНиП 2.04.01-85*

# 3.2 Обозначения и единицы измерения
В настоящем своде правил применены следующие обозначения и единицы измерения:

𝑞0_tot – общий расход воды, л/с, санитарно-техническим прибором (арматурой), принимаемый согласно 5.2;

𝑞0_ℎ – расход горячей воды, л/с, санитарно-техническим прибором (арматурой), принимаемый согласно 5.2;

𝑞0_c – расход холодной воды, л/с, санитарно-техническим прибором (арматурой), принимаемый согласно 5.2;

𝑞0_s – расход стоков от санитарно-технического прибора, л/с, принимаемый согласно таблице А.1;

𝑞_tot– общий максимальный расчетный расход воды, л/с, принимаемый согласно 5.3;

𝑞h – максимальный расчетный расход горячей воды, л/с, принимаемый согласно 5.3;

𝑞c – максимальный расчетный расход холодной воды, л/с, принимаемый согласно 5.3;

qs – максимальный расчетный расход сточных вод для стояков, л/с, принимаемый согласно 5.5;

qsL – максимальный расчетный расход сточных вод для горизонтальных отводящих трубопроводов, л/с, принимаемый согласно 5.7;

q0_ℎ𝑟_𝑡𝑜𝑡 – общий расход воды, л/ч, санитарно-техническим прибором, принимаемый согласно 5.8;

𝑞0_ℎ𝑟_ℎ – расход горячей воды, л/ч, санитарно-техническим прибором, принимаемый согласно 5.8;

𝑞0,ℎ𝑟 𝑐 – расход холодной воды, л/ч, санитарно-техническим прибором, принимаемый согласно 5.8;

𝑞ℎ𝑟,𝑢 𝑡𝑜𝑡 – общий расчетный расход воды, л, потребителем в час наибольшего водопотребления, принимаемый по таблице А.2;

𝑞ℎ𝑟,𝑢 ℎ – расчетный расход горячей воды, л, потребителем в час наибольшего водопотребления, принимаемый по таблице А.2;

𝑞ℎ𝑟,𝑢 𝑐 – расчетный расход холодной воды, л, потребителем в час наибольшего потребления, принимаемый по таблице А.2;

𝑞ℎ𝑟 𝑡𝑜𝑡 – общий максимальный часовой расход воды, м3, принимаемый согласно 5.10;

𝑞ℎ𝑟 ℎ – максимальный часовой расход горячей воды, м3, принимаемый согласно 5.10;

𝑞ℎ𝑟 𝑐 – максимальный часовой расход холодной воды, м³, принимаемый согласно

"""

from enum import Enum
import uuid
from pydantic import Field
from pydantic.dataclasses import dataclass


# ТаблицаА.1 – Расчетные расходы воды и стоков для санитарно-технических приборов
@dataclass
class DeviceWaterConsumptionNorms:
    id: int
    name: str  # Санитарные приборы
    water_flow_rate_lps_total: float  # Секундный расход воды, л/с - общий
    water_flow_rate_lps_cold: float  # Секундный расход воды, л/с - холодной
    water_flow_rate_lps_hot: float  # Секундный расход воды, л/с - горячей
    water_flow_rate_lph_total: float  # Часовой расход воды, л/ч - общий
    water_flow_rate_lph_cold: float  # Часовой расход воды, л/ч - холодной
    water_flow_rate_lph_hot: float  # Часовой расход воды, л/ч - горячей
    wastewater_discharge_lps: float  # Расход стоков от прибора, л/с
    min_nominal_diameter_mm_inlet: float  # Минимальные диаметры условного прохода, мм - подводки
    min_nominal_diameter_mm_outlet: float  # Минимальные диаметры условного прохода, мм - отвода

# ТаблицаА.2 – Расчетные расходы воды потребителями
class ConsuptionMeasurer(Enum):
    ONE_INHABITANT = 1
    ONE_BED = 2
    ONE_PERSON_PER_SHIFT = 3
    ONE_PLACE = 4
    ONE_KG_OF_DRY_CLOTHS = 5
    ONE_STUDENT_AND_ONE_TEACHER = 6
    ONE_DEVICE_PER_SHIFT = 7
    ONE_DISH = 8
    ONE_EMPLOYEE_ON_20_SQU_MET = 9
    PERCENT_OF_POOL_CAPACITY = 10
    ONE_DOUCH_PER_SHIFT = 11
    ONE_SQU_MET = 12


@dataclass
class WaterConsumerNorms:
    # Водопотребители
    name: str
    # Измеритель
    measurer: ConsuptionMeasurer
    # Нормы расхода воды (л) - в средние сутки - общая (в том числе горячей)
    avg_hot_and_cold_water_norms_per_day: float
    # Нормы расхода воды (л) - в средние сутки - горячей
    avg_hot_water_norms_per_day: float
    # Нормы расхода воды (л) - в час наибольшего водопотребления - общая (в том числе горячей)
    max_hot_and_cold_water_norms_per_hour: float
    # Нормы расхода воды (л) - в час наибольшего водопотребления - горячей
    max_hot_water_norms_per_hour: float
    # Расход воды прибором, л/с (л/ч) - общий (холодной И горячей)
    device_water_consumption_hot_and_cold: float
    # Расход воды прибором, л/с (л/ч) - холодной ИЛИ горячей
    device_water_consumption_hot_or_cold: float
    # T, ч
    T: float
    # id
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ResultWaterConsumption:
    meters_cubic_per_day: float
    meters_cubic_per_hour: float
    liters_per_second: float


@dataclass
class TotalObjectConsumption:
    # Хозяйственно-питьевой водопровод
    domestic_and_drinking_water_supply_general: ResultWaterConsumption # Общий расход воды
    domestic_and_drinking_water_supply_hot: ResultWaterConsumption # Расход холодной воды
    domestic_and_drinking_water_supply_cold: ResultWaterConsumption # Расход горячей воды
    # Бытовая канализация
    domestic_sewerage_general: ResultWaterConsumption # Общий расход воды
    domestic_sewerage_hot: ResultWaterConsumption # Расход холодной воды
    domestic_sewerage_cold: ResultWaterConsumption # Расход горячей воды


def calculate_consumption() -> TotalObjectConsumption:
    return TotalObjectConsumption(
        domestic_and_drinking_water_supply_general=ResultWaterConsumption(
            meters_cubic_per_day=-1, # idk how to calc
            meters_cubic_per_hour=0,
            liters_per_second=0
        ),
        domestic_and_drinking_water_supply_hot=ResultWaterConsumption(
            meters_cubic_per_day=-1, # idk how to calc
            meters_cubic_per_hour=0,
            liters_per_second=0
        ),
        domestic_and_drinking_water_supply_cold=ResultWaterConsumption(
            meters_cubic_per_day=-1, # idk how to calc
            meters_cubic_per_hour=0,
            liters_per_second=0
        ),
        domestic_sewerage_general=ResultWaterConsumption(
            meters_cubic_per_day=-1, # idk how to calc
            meters_cubic_per_hour=0,
            liters_per_second=0
        ),
        domestic_sewerage_hot=ResultWaterConsumption(
            meters_cubic_per_day=-1, # idk how to calc
            meters_cubic_per_hour=0,
            liters_per_second=0
        ),
        domestic_sewerage_cold=ResultWaterConsumption(
            meters_cubic_per_day=-1, # idk how to calc
            meters_cubic_per_hour=0,
            liters_per_second=0
        ),
    )


def calculate_max_per_sec_consumption():
    """
    5.3 Максимальный расчетный расход воды на расчетном участке сети 𝑞 (𝑞𝑡𝑜𝑡, 𝑞ℎ, 𝑞𝑐), л/с, следует определять по формуле:
    𝑞 = 5 𝑞0 𝑎, 
        где 𝑞0 (𝑞0 𝑡𝑜𝑡, 𝑞0 ℎ, 𝑞0 𝑐), – расход воды, л/с, значение которого следует определять согласно 5.2;
        𝑎 – коэффициент, определяемый по приложению Б в зависимости от общего числа приборов N на расчетном участке сети и вероятности их действия Р.
    При этом таблицей Б.1 следует руководствоваться при Р > 0,1 и N  200; при других значениях Р и N коэффициент  следует принимать по таблице Б.2.
    """


def calculate_device_activation_possibility():
    """
    5.4 Вероятность действия санитарно-технических приборов 𝑃 (𝑃𝑡𝑜𝑡, 𝑃ℎ, 𝑃с) на участках
    сети следует определять по формулам:
    а) при однотипных водопотребителях в здании, без учета изменения соотношения U/N
        𝑃 = 𝑞ℎ𝑟𝑢 𝑈 / (𝑞0 𝑁 ∙ 3600) или 𝑁𝑃 = 𝑞ℎ𝑟,𝑢 𝑈 / (𝑞0 ∙ 3600) ; 
    б) при отличающихся группах водопотребителей в здании:

    """