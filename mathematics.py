"""

https://acs-nnov.ru/assets/files/sp_30.13330.2020_vnutrennij_vodoprovod_i_kanalizaciya_zdanij_snip_2.04.01-85.pdf?ysclid=m9yhpdjgll865220296

СП 30.13330.2020
ВНУТРЕННИЙ ВОДОПРОВОД И КАНАЛИЗАЦИЯ ЗДАНИЙ
СНиП 2.04.01-85*

"""

import uuid
from decimal import Decimal, getcontext
from enum import Enum

from pydantic import Field
from pydantic.dataclasses import dataclass

from ml import aproximate_alpha


getcontext().prec = 8


class WateringConsumption(Enum):
    GRASS = Decimal(3)
    FOOTBALL_FIELD = Decimal(0.5)
    OTHER_SPORTS_BUILDINGS = Decimal(1.5)
    # 4-5??
    # TROTUARS_SQUARES_AND_FACTORY_ROADS = Decimal()
    ICE_RINK = Decimal(0.5)



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
    device_water_consumption_hot_and_cold_q0tot: float
    device_water_consumption_hot_and_cold_q0tot_hr: float
    # Расход воды прибором, л/с (л/ч) - холодной ИЛИ горячей
    device_water_consumption_hot_or_cold_q0: float
    device_water_consumption_hot_or_cold_q0_hr: float
    # T, ч
    T: float
    # id
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ResultWaterConsumption:
    meters_cubic_per_day: Decimal
    meters_cubic_per_hour: Decimal
    liters_per_second: Decimal


@dataclass
class SecondConsumptionReportData:
    # Probabilities
    P_total: Decimal
    P_hot: Decimal
    P_cold: Decimal
    # Water consumption
    q_total: Decimal
    q_hot: Decimal
    q_cold: Decimal


@dataclass
class MaxHourConsumptionReportData:
    # Probabilities
    P_total: Decimal
    P_hot: Decimal
    P_cold: Decimal
    # Water consumption
    q_total: Decimal
    q_hot: Decimal
    q_cold: Decimal


@dataclass
class AvgHourConsumptionReportData:
    # Water consumption
    q_total: Decimal
    q_hot: Decimal
    q_cold: Decimal


@dataclass
class TotalDayConsumptionReportData:
    # Water consumption
    Q_total: Decimal
    Q_hot: Decimal
    Q_cold: Decimal


@dataclass
class HeatConsumptionReportData:
    Q_avg_hour: Decimal
    Q_max_hour: Decimal


@dataclass
class GrassWateringReportData:
    Quc: Decimal


@dataclass
class TotalObjectConsumption:
    # Хозяйственно-питьевой водопровод
    domestic_and_drinking_water_supply_general: ResultWaterConsumption # Общий расход воды
    domestic_and_drinking_water_supply_hot: ResultWaterConsumption # Расход холодной воды
    domestic_and_drinking_water_supply_cold: ResultWaterConsumption # Расход горячей воды
    # Бытовая канализация
    domestic_sewerage_general: ResultWaterConsumption # Общий расход воды
    # domestic_sewerage_hot: ResultWaterConsumption # Расход холодной воды
    # domestic_sewerage_cold: ResultWaterConsumption # Расход горячей воды


@dataclass
class OneObjectDataReport:
    consumer: WaterConsumerNorms
    num_of_measureres: int
    num_of_devices: int
    num_of_devices_with_hot_water: int
    seconds_report: SecondConsumptionReportData
    hours_max_report: MaxHourConsumptionReportData
    hours_avg_report: AvgHourConsumptionReportData
    heat_report: HeatConsumptionReportData
    grass_watering_report: GrassWateringReportData
    total_day_report: TotalDayConsumptionReportData
    total_object_report: TotalObjectConsumption


def _d(v: int | float) -> Decimal:
    return Decimal(v)


def calculate_consumption_for_one_object(
    consumer: WaterConsumerNorms,
    num_of_measurers: int,
    num_of_devices: int,
    num_of_devices_with_hot_water: int) -> OneObjectDataReport:

    seconds_consumption = calculate_max_per_sec_consumption(
        consumer,
        num_of_measurers,
        num_of_devices,
        num_of_devices_with_hot_water
    )

    max_hour_consumption = calculate_max_hour_consumption(consumer, seconds_consumption)
    avg_hour_consumption = calculate_avg_hour_consumption(consumer, num_of_measurers)
    heat_consumption = calculate_heat_consumption(avg_hour_consumption, max_hour_consumption)
    total_day_consumption = calculate_total_day_consumption(consumer, num_of_measurers)
    grass_watering = calculate_grass_watering(num_of_measurers)

    total_object_consumption = calculate_total_object_consumption(
        grass_watering,
        total_day_consumption,
        max_hour_consumption,
        seconds_consumption
    )

    return OneObjectDataReport(
        consumer=consumer,
        num_of_devices=num_of_devices,
        num_of_measureres=num_of_measurers,
        num_of_devices_with_hot_water=num_of_devices_with_hot_water,
        seconds_report=seconds_consumption,
        hours_avg_report=avg_hour_consumption,
        hours_max_report=max_hour_consumption,
        heat_report=heat_consumption,
        total_day_report=total_day_consumption,
        grass_watering_report=grass_watering,
        total_object_report=total_object_consumption,
    )


def calculate_total_object_consumption(
    grass_watering: GrassWateringReportData,
    total_day_consumption: TotalDayConsumptionReportData,
    max_hour_consumption: MaxHourConsumptionReportData,
    seconds_consumption: SecondConsumptionReportData,
) -> TotalObjectConsumption:
    return TotalObjectConsumption(
        # Общий расход воды
        domestic_and_drinking_water_supply_general=ResultWaterConsumption(
            meters_cubic_per_day=total_day_consumption.Q_total + grass_watering.Quc,
            meters_cubic_per_hour=max_hour_consumption.q_total,
            liters_per_second=seconds_consumption.q_total,
        ),
        domestic_and_drinking_water_supply_hot=ResultWaterConsumption(
            meters_cubic_per_day=total_day_consumption.Q_hot + grass_watering.Quc,
            meters_cubic_per_hour=max_hour_consumption.q_hot,
            liters_per_second=seconds_consumption.q_hot,
        ),
        domestic_and_drinking_water_supply_cold=ResultWaterConsumption(
            meters_cubic_per_day=total_day_consumption.Q_cold,
            meters_cubic_per_hour=max_hour_consumption.q_cold,
            liters_per_second=seconds_consumption.q_cold,
        ),
        # Бытовая канализация
        domestic_sewerage_general=ResultWaterConsumption(
            meters_cubic_per_day=total_day_consumption.Q_total - grass_watering.Quc,
            meters_cubic_per_hour=max_hour_consumption.q_total,
            liters_per_second=Decimal(-1),
        ),
    )


def calculate_grass_watering(num_of_measurers: int) -> GrassWateringReportData:
    # TODO: WateringConsumption param definition
    # NOTE: do not do this for now
    # Quc = WateringConsumption.GRASS.value * _d(num_of_measurers) / _d(1000)
    Quc = _d(0)

    return GrassWateringReportData(Quc=Quc)


def calculate_total_day_consumption(
    consumer: WaterConsumerNorms,
    num_of_measurers: int) -> TotalDayConsumptionReportData:

    # TODO - fuck me - how to calculate it?

    working_hours = _d(4)

    Q_total = (
        _d(consumer.avg_hot_and_cold_water_norms_per_day)
        * num_of_measurers
        * working_hours
        / _d(1000)
    )
    Q_hot = (
        (
            _d(consumer.avg_hot_and_cold_water_norms_per_day) 
            - _d(consumer.avg_hot_water_norms_per_day)
        )
        * num_of_measurers
        * working_hours
        / _d(1000)
    )
    Q_cold = (
        (
            _d(consumer.avg_hot_and_cold_water_norms_per_day) 
            - _d(consumer.avg_hot_water_norms_per_day)
        )
        * num_of_measurers
        * working_hours
        / _d(1000)
    )


    return TotalDayConsumptionReportData(
        Q_total=Q_total,
        Q_hot=Q_hot,
        Q_cold=Q_cold,
    )


def calculate_heat_consumption(
    avg_hour_consumption: AvgHourConsumptionReportData,
    max_hour_consumption: MaxHourConsumptionReportData) -> HeatConsumptionReportData:

    Qht = (
        _d(1.16) 
        * avg_hour_consumption.q_hot 
        * _d(61 - 5)
        + max_hour_consumption.q_hot * _d(0.3)
    )
    Qhrt = (
        _d(1.16) 
        * max_hour_consumption.q_hot 
        * _d(61 - 5)
        + max_hour_consumption.q_hot * _d(0.3)
    )

    return HeatConsumptionReportData(
        Q_avg_hour=Qht,
        Q_max_hour=Qhrt,
    ) 


def calculate_avg_hour_consumption(
    consumer: WaterConsumerNorms,
    num_of_measurers: int,
) -> AvgHourConsumptionReportData:
    """

    5.11 Средний часовой расход воды 𝑞𝑇 (𝑞𝑇𝑡𝑜𝑡, 𝑞𝑇ℎ, 𝑞𝑇𝑐 ), м3, за расчетное время водопотребления (сутки, смена) Т, ч, следует определять по формуле:
    ...

    """

    qT_tot = (
        _d(consumer.avg_hot_and_cold_water_norms_per_day)
        * _d(consumer.T)
        * num_of_measurers
        / 1000
    )
    qT_h = (
        _d(consumer.avg_hot_water_norms_per_day)
        * _d(consumer.T)
        * num_of_measurers
        / 1000
    )
    qT_c = (
        (
            _d(consumer.avg_hot_and_cold_water_norms_per_day) 
            - _d(consumer.avg_hot_water_norms_per_day)
        )
        * _d(consumer.T)
        * num_of_measurers
        / 1000
    )

    return AvgHourConsumptionReportData(
        q_total=qT_tot,
        q_hot=qT_h,
        q_cold=qT_c,
    )


def calculate_max_hour_consumption(
    consumer: WaterConsumerNorms,
    second_consumption: SecondConsumptionReportData,
) -> MaxHourConsumptionReportData:

    """

    Вероятность использования санитарно-технических приборов 𝑃ℎ𝑟 для системы в целом следует определять по формуле:
    ...
    Максимальный часовой расход воды (стоков) 𝑞ℎ𝑟 (𝑞ℎ𝑟𝑡𝑜𝑡, 𝑞ℎℎ𝑟, 𝑞ℎ𝑐𝑟), м3, следует определять по формуле:
    ...

    """

    Phr_tot = (
        (
            3600
            * second_consumption.P_total
            * _d(consumer.device_water_consumption_hot_and_cold_q0tot)
        )
        /
        (
            _d(consumer.device_water_consumption_hot_and_cold_q0tot_hr)
        )
    )
    Phr_c = (
        (
            3600
            * second_consumption.P_cold
            * _d(consumer.device_water_consumption_hot_or_cold_q0)
        )
        /
        (
            _d(consumer.device_water_consumption_hot_or_cold_q0_hr)
        )
    )
    Phr_h = (
        (
            3600
            * second_consumption.P_total
            * _d(consumer.device_water_consumption_hot_or_cold_q0)
        )
        /
        (
            _d(consumer.device_water_consumption_hot_or_cold_q0_hr)
        )
    )

    alpha_hr_tot = aproximate_alpha(Phr_tot)
    alpha_hr_h = aproximate_alpha(Phr_h)
    alpha_hr_c = aproximate_alpha(Phr_c)

    qhr_tot = _d(0.005) * _d(consumer.device_water_consumption_hot_and_cold_q0tot_hr) * alpha_hr_tot
    qhr_c = _d(0.005) * _d(consumer.device_water_consumption_hot_or_cold_q0_hr) * alpha_hr_c
    qhr_h = _d(0.005) * _d(consumer.device_water_consumption_hot_or_cold_q0_hr) * alpha_hr_h

    return MaxHourConsumptionReportData(
        P_total=Phr_tot,
        P_hot=Phr_h,
        P_cold=Phr_c,
        q_total=qhr_tot,
        q_hot=qhr_h,
        q_cold=qhr_c,
    )


def calculate_max_per_sec_consumption(
    consumer: WaterConsumerNorms,
    num_of_measurers: int,
    num_of_devices: int,
    num_of_devices_with_hot_water: int) -> SecondConsumptionReportData:

    """ 

    Секундный расход воды  различными  приборами, обслуживающими разных водопотребителей, определяется по формуле 2 СП30.13330.2020:
    q^tot = 5 x q_0 x alpha, л/с
    Расчет начинаем с определения вероятности действия приборов различными потребителями:
    P= q^tot_{hr,u}  х  U / (q_0 х N x 3600)

    """

    P_tot = (
        (
            _d(consumer.max_hot_and_cold_water_norms_per_hour) 
            * _d(num_of_measurers)
        )
        / 
        (
            _d(consumer.device_water_consumption_hot_and_cold_q0tot)
            * _d(num_of_devices)
            * 3600
        )
    )
    P_h = (
        (
            _d(consumer.max_hot_water_norms_per_hour) 
            * _d(num_of_measurers)
        )
        / 
        (
            _d(consumer.device_water_consumption_hot_or_cold_q0)
            * _d(num_of_devices_with_hot_water)
            * 3600
        )
    )
    P_c = (
        (
            (
            _d(consumer.max_hot_and_cold_water_norms_per_hour)
            - _d(consumer.max_hot_water_norms_per_hour)
            )
            * _d(num_of_measurers)
        )
        / 
        (
            _d(consumer.device_water_consumption_hot_or_cold_q0)
            * (_d(num_of_devices) - _d(num_of_devices_with_hot_water))
            * 3600
        )
    )

    alpha_tot = aproximate_alpha(P_tot)
    alpha_h = aproximate_alpha(P_h)
    alpha_c = aproximate_alpha(P_c)

    q_tot = _d(5) * _d(consumer.device_water_consumption_hot_and_cold_q0tot) * alpha_tot
    q_h = _d(5) * _d(consumer.device_water_consumption_hot_or_cold_q0) * alpha_h
    q_c = _d(5) * _d(consumer.device_water_consumption_hot_or_cold_q0) * alpha_c

    return SecondConsumptionReportData(
        P_total=P_tot, P_hot=P_h, P_cold=P_c,
        q_total=q_tot, q_hot=q_h, q_cold=q_c,
    )


def calculate_device_activation_possibility():
    """ """