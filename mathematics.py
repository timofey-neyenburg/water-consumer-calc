"""

https://acs-nnov.ru/assets/files/sp_30.13330.2020_vnutrennij_vodoprovod_i_kanalizaciya_zdanij_snip_2.04.01-85.pdf?ysclid=m9yhpdjgll865220296

СП 30.13330.2020
ВНУТРЕННИЙ ВОДОПРОВОД И КАНАЛИЗАЦИЯ ЗДАНИЙ
СНиП 2.04.01-85*

"""

from typing import Literal
import uuid
from decimal import Decimal, getcontext
from enum import Enum

from pydantic import Field
from pydantic.dataclasses import dataclass

# from ml import aproximate_alpha

def aproximate_alpha(v: Decimal) -> Decimal:
    return v


# def approximate(NP: Decimal, less_200: bool = True) -> Decimal:
#     if less_200:
#         model = TwoVariableApproximator(nn.ReLU)                                                # type:ignore
#     else:
#         model = AlphaOneDimensionalApproximator(nn.ReLU)                                                # type:ignore

#     model.load_state_dict(torch.load(CONF.MODEL_PATH))                                      # type:ignore
#     model.eval()

#     with torch.no_grad():                                                                   # type:ignore
#         inp = torch.tensor(float(NP), dtype=torch.float32)                                         # type:ignore
#         v = model(inp).squeeze(1).float()                                                # type:ignore
    
#     return Decimal(v)
 
# aproximate_alpha = lambda v: approximate(v, N < 200)                                      # type:ignore

getcontext().prec = 8


### Common structures for one object and multiple objects ###


class WateringConsumption(Enum):
    GRASS = Decimal(3)
    FOOTBALL_FIELD = Decimal(0.5)
    OTHER_SPORTS_BUILDINGS = Decimal(1.5)
    # 4-5??
    # TROTUARS_SQUARES_AND_FACTORY_ROADS = Decimal()
    ICE_RINK = Decimal(0.5)


class ConsuptionMeasurer(Enum):
    ONE_INHABITANT = "жит."
    ONE_BED = "кров."
    ONE_PERSON_PER_SHIFT = "человек в смене"
    ONE_PLACE = "мест."
    ONE_KG_OF_DRY_CLOTHS = "кг. сухой одежды"
    ONE_STUDENT_AND_ONE_TEACHER = "студент и учитель"
    ONE_DEVICE_PER_SHIFT = "устройство в смене"
    ONE_DISH = "посуда"
    ONE_EMPLOYEE_ON_20_SQU_MET = "рабочий на 20 м.кв."
    PERCENT_OF_POOL_CAPACITY = "процент объема бассейна"
    ONE_DOUCH_PER_SHIFT = "душ на смену"
    ONE_SQU_MET = "м. кв."


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

    def upd_id(self):
        self.id = str(uuid.uuid4())


### Reports for one object ###


@dataclass
class WaterConsumerParams:
    consumer_norms: WaterConsumerNorms
    num_of_devices: int
    num_of_devices_hot: int
    num_of_measurers: int
    temp_hot: int
    temp_cold: int
    work_hours: int


@dataclass
class ResultWaterConsumption:
    meters_cubic_per_day: Decimal
    meters_cubic_per_hour: Decimal
    liters_per_second: Decimal


@dataclass
class SecondConsumptionReportData:
    # alphas
    alpha_total: Decimal
    alpha_hot: Decimal
    alpha_cold: Decimal
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
    # alphas
    alpha_total: Decimal
    alpha_hot: Decimal
    alpha_cold: Decimal
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
    consumer_params: WaterConsumerParams
    seconds_report: SecondConsumptionReportData
    hours_max_report: MaxHourConsumptionReportData
    hours_avg_report: AvgHourConsumptionReportData
    heat_report: HeatConsumptionReportData
    grass_watering_report: GrassWateringReportData
    total_day_report: TotalDayConsumptionReportData
    total_object_report: TotalObjectConsumption


### Reports for multiple objects ###


@dataclass
class MultipleObjectsNP:
    NP_total: Decimal
    NP_hot: Decimal
    NP_cold: Decimal


@dataclass
class MultipleObjectsAlphas:
    alhpha_total: Decimal
    alhpha_hot: Decimal
    alhpha_cold: Decimal


@dataclass
class MultipleObjectsQs:
    q_total: Decimal
    q_hot: Decimal
    q_cold: Decimal


@dataclass
class MultipleObjectsSecondsConsumptionDataReport:
    consumer_params: list[WaterConsumerParams]
    NPs_tot: list[Decimal]
    NPs_c: list[Decimal]
    NPs_h: list[Decimal]
    NPs_tot_sum: Decimal
    NPs_c_sum: Decimal
    NPs_h_sum: Decimal
    alpha_h: Decimal
    alpha_c: Decimal
    alpha_tot: Decimal
    q_tot: Decimal
    q_h: Decimal
    q_c: Decimal
    q0_tot: Decimal
    q0_h: Decimal
    q0_c: Decimal


@dataclass
class MultipleObjectsTotalHoursConsumptionDataReport:
    consumer_params: list[WaterConsumerParams]
    NPhrs_tot: list[Decimal]
    NPhrs_c: list[Decimal]
    NPhrs_h: list[Decimal]
    NPhrs_tot_sum: Decimal
    NPhrs_c_sum: Decimal
    NPhrs_h_sum: Decimal
    alpha_hr_h: Decimal
    alpha_hr_c: Decimal
    alpha_hr_tot: Decimal
    qhr_tot: Decimal
    qhr_h: Decimal
    qhr_c: Decimal
    q0hr_tot: Decimal
    q0hr_c: Decimal
    q0hr_h: Decimal


@dataclass
class MultipleObjectsTotalDayConsumptionDataReport:
    consumer_params: list[WaterConsumerParams]
    Qu_tots: list[Decimal]
    Qu_hs: list[Decimal]
    Qu_cs: list[Decimal]
    Qu_total: Decimal
    Qu_hot: Decimal
    Qu_cold: Decimal


@dataclass
class MultipleObjectsHeatConsumptionDataReport:
    Q_avg_hour: Decimal
    Q_max_hour: Decimal


@dataclass
class MultipleObjectsDataReport:
    seconds_consumption: MultipleObjectsSecondsConsumptionDataReport
    hours_consumption: MultipleObjectsTotalHoursConsumptionDataReport
    day_consumption: MultipleObjectsTotalDayConsumptionDataReport
    heat_consumption: MultipleObjectsHeatConsumptionDataReport
    consumers_params: list[WaterConsumerParams]


### Multiple objects calculations ###

def calculate_multiple_objects_heat_consumption(
    consumers_params: list[WaterConsumerParams],
    hour_consumption: MultipleObjectsTotalHoursConsumptionDataReport,
    day_consumption: MultipleObjectsTotalDayConsumptionDataReport,
):
    temp_diff = _d(consumers_params[0].temp_hot) - _d(consumers_params[0].temp_cold)

    Qht = (
        _d(1.16) 
        * day_consumption.Qu_hot
        * temp_diff
        + hour_consumption.qhr_h * _d(0.3)
    )
    Qhrt = (
        _d(1.16) 
        * hour_consumption.qhr_h
        * temp_diff
        + hour_consumption.qhr_h * _d(0.3)
    )

    return MultipleObjectsHeatConsumptionDataReport(
        Q_avg_hour=Qht,
        Q_max_hour=Qhrt,
    ) 

def calculate_multiple_objects_day_consumption(
    consumers_params: list[WaterConsumerParams],
):
    Q_tots: list[Decimal] = []
    Q_hs: list[Decimal] = []
    Q_cs: list[Decimal] = []

    for ind, consumer in enumerate(consumers_params):
        Q_total = (
            _d(consumer.consumer_norms.avg_hot_and_cold_water_norms_per_day)
            * consumer.num_of_measurers
            / _d(1000)
        )
        Q_hot = (
            _d(consumer.consumer_norms.avg_hot_water_norms_per_day)
            * consumer.num_of_measurers
            / _d(1000)
        )
        Q_cold = (
            (
                _d(consumer.consumer_norms.avg_hot_and_cold_water_norms_per_day) 
                - _d(consumer.consumer_norms.avg_hot_water_norms_per_day)
            )
            * consumer.num_of_measurers
            / _d(1000)
        )

        Q_tots.append(Q_total)
        Q_hs.append(Q_hot)
        Q_cs.append(Q_cold)
    
    Q_tot_sum = _d(sum(Q_tots))
    Q_h_sum = _d(sum(Q_tots))
    Q_c_sum = _d(sum(Q_tots))

    return MultipleObjectsTotalDayConsumptionDataReport(
        consumer_params=consumers_params,
        Qu_tots=Q_tots,
        Qu_hs=Q_hs,
        Qu_cs=Q_cs,
        Qu_total=Q_tot_sum,
        Qu_hot=Q_h_sum,
        Qu_cold=Q_c_sum,
    )

def calculate_multiple_objects_hour_consumption(
    seconds_consumption: MultipleObjectsSecondsConsumptionDataReport,
    consumers_params: list[WaterConsumerParams],
):
    NPhr_tots: list[Decimal] = []
    NPhr_hs: list[Decimal] = []
    NPhr_cs: list[Decimal] = []

    NPhr_tot_0 = 0
    NPhr_hot_0 = 0
    NPhr_cold_0 = 0

    for ind, consumer in enumerate(consumers_params):
        nPhr_tot = (
            (3600 * seconds_consumption.NPs_tot[ind] * _d(consumer.consumer_norms.device_water_consumption_hot_and_cold_q0tot))
            /
            (_d(consumer.consumer_norms.device_water_consumption_hot_and_cold_q0tot_hr))
        )
        nPhr_c = (
            (3600 * seconds_consumption.NPs_c[ind] * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0))
            /
            (_d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0_hr))
        )
        nPhr_h = (
            (3600 * seconds_consumption.NPs_h[ind] * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0))
            /
            (_d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0_hr))
        )        

        NPhr_cs.append(nPhr_c)
        NPhr_hs.append(nPhr_h)
        NPhr_tots.append(nPhr_tot)

        NPhr_tot_0 += nPhr_tot * _d(consumer.consumer_norms.device_water_consumption_hot_and_cold_q0tot_hr)
        NPhr_hot_0 += nPhr_h * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0_hr)
        NPhr_cold_0 += nPhr_c * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0_hr)

    NPhr_tot_sum = _d(sum(NPhr_tots))
    NPhr_h_sum = _d(sum(NPhr_hs))
    NPhr_c_sum = _d(sum(NPhr_cs))
    
    alpha_hr_tot = aproximate_alpha(NPhr_tot_sum)
    alpha_hr_h = aproximate_alpha(NPhr_h_sum)
    alpha_hr_c = aproximate_alpha(NPhr_c_sum)

    q0hr_tot = NPhr_tot_0 / NPhr_tot_sum
    q0hr_c = NPhr_cold_0 / NPhr_c_sum
    q0hr_h = NPhr_hot_0 / NPhr_h_sum

    qhr_tot = _d(0.005) * NPhr_tot_sum * alpha_hr_tot
    qhr_c = _d(0.005) * NPhr_c_sum * alpha_hr_c
    qhr_h = _d(0.005) * NPhr_h_sum * alpha_hr_h

    return MultipleObjectsTotalHoursConsumptionDataReport(
        consumer_params=consumers_params,
        NPhrs_tot=NPhr_tots,
        NPhrs_c=NPhr_cs,
        NPhrs_h=NPhr_hs,
        NPhrs_tot_sum=NPhr_tot_sum,
        NPhrs_c_sum=NPhr_c_sum,
        NPhrs_h_sum=NPhr_h_sum,
        alpha_hr_h=alpha_hr_h,
        alpha_hr_c=alpha_hr_c,
        alpha_hr_tot=alpha_hr_tot,
        qhr_tot=qhr_tot,
        qhr_c=qhr_c,
        qhr_h=qhr_h,
        q0hr_tot=q0hr_tot,
        q0hr_c=q0hr_c,
        q0hr_h=q0hr_h,
    )

def calculate_multiple_objects_seconds_consumption(consumers_params: list[WaterConsumerParams]):
    NP_tots: list[Decimal] = []
    NP_hs: list[Decimal] = []
    NP_cs: list[Decimal] = []

    NP_tot_0 = 0
    NP_hot_0 = 0
    NP_cold_0 = 0
    
    for consumer in consumers_params:
        nP_tot = (
            (_d(consumer.consumer_norms.max_hot_and_cold_water_norms_per_hour) * _d(consumer.num_of_measurers))
            / 
            (_d(consumer.consumer_norms.device_water_consumption_hot_and_cold_q0tot) * _d(consumer.num_of_devices) * 3600)
        )
        nP_h = (
            (_d(consumer.consumer_norms.max_hot_water_norms_per_hour) * _d(consumer.num_of_measurers))
            / 
            (_d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0) * _d(consumer.num_of_devices_hot) * 3600)
        )
        nP_c = (
            ((_d(consumer.consumer_norms.max_hot_and_cold_water_norms_per_hour) - _d(consumer.consumer_norms.max_hot_water_norms_per_hour)) * _d(consumer.num_of_measurers))
            / 
            (_d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0) * (_d(consumer.num_of_devices) - _d(consumer.num_of_devices_hot)) * 3600)
        )

        NP_cs.append(nP_c)
        NP_hs.append(nP_h)
        NP_tots.append(nP_tot)

        NP_tot_0 += nP_tot * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0)
        NP_hot_0 += nP_h * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0)
        NP_cold_0 += nP_c * _d(consumer.consumer_norms.device_water_consumption_hot_or_cold_q0)
    
    NP_tot_sum = _d(sum(NP_tots))
    NP_h_sum = _d(sum(NP_hs))
    NP_c_sum = _d(sum(NP_cs))
    
    alpha_tot = aproximate_alpha(NP_tot_sum)
    alpha_h = aproximate_alpha(NP_h_sum)
    alpha_c = aproximate_alpha(NP_c_sum)

    q0_tot = NP_tot_0 / NP_tot_sum
    q0_c = NP_cold_0 / NP_c_sum
    q0_h = NP_hot_0 / NP_h_sum

    q_tot = _d(5) * q0_tot * alpha_tot
    q_h = _d(5) * q0_h * alpha_h
    q_c = _d(5) * q0_c * alpha_c
    
    return MultipleObjectsSecondsConsumptionDataReport(
        consumer_params=consumers_params,
        NPs_tot= NP_tots,
        NPs_c= NP_cs,
        NPs_h= NP_hs,
        NPs_tot_sum=NP_tot_sum,
        NPs_c_sum=NP_h_sum,
        NPs_h_sum=NP_c_sum,
        alpha_tot=alpha_tot,
        alpha_h=alpha_h,
        alpha_c=alpha_c,
        q_tot=q_tot,
        q_h=q_h,
        q_c=q_c,
        q0_tot=q_tot,
        q0_h=q_h,
        q0_c=q_c,
    )


def calculate_consumption_for_multiple_objects(consumers_params: list[WaterConsumerParams]) -> MultipleObjectsDataReport:
    seconds_report = calculate_multiple_objects_seconds_consumption(consumers_params)
    hours_report = calculate_multiple_objects_hour_consumption(seconds_report, consumers_params)
    day_report = calculate_multiple_objects_day_consumption(consumers_params)
    heat_report = calculate_multiple_objects_heat_consumption(consumers_params, hours_report, day_report)

    return MultipleObjectsDataReport(
        seconds_consumption=seconds_report,
        hours_consumption=hours_report,
        day_consumption=day_report,
        heat_consumption=heat_report,
        consumers_params=consumers_params,
    )


### One object calculations ###


def calculate_consumption_for_one_object(consumer_params: WaterConsumerParams) -> OneObjectDataReport:
    seconds_consumption = calculate_max_per_sec_consumption(
        consumer_params.consumer_norms,
        consumer_params.num_of_measurers,
        consumer_params.num_of_devices,
        consumer_params.num_of_devices_hot,
    )

    max_hour_consumption = calculate_max_hour_consumption(consumer_params.consumer_norms, seconds_consumption)
    avg_hour_consumption = calculate_avg_hour_consumption(consumer_params, consumer_params.consumer_norms, consumer_params.num_of_measurers)
    heat_consumption = calculate_heat_consumption(consumer_params, avg_hour_consumption, max_hour_consumption)
    total_day_consumption = calculate_total_day_consumption(consumer_params, consumer_params.num_of_measurers)
    grass_watering = calculate_grass_watering(consumer_params.num_of_measurers)

    total_object_consumption = calculate_total_object_consumption(
        grass_watering,
        total_day_consumption,
        max_hour_consumption,
        seconds_consumption
    )

    return OneObjectDataReport(
        consumer=consumer_params.consumer_norms,
        consumer_params=consumer_params,
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
    consumer_params: WaterConsumerParams,
    num_of_measurers: int) -> TotalDayConsumptionReportData:

    if consumer_params.consumer_norms.T == 24:
        working_shifts = _d(1)
    else:
        working_shifts = _d(consumer_params.work_hours) / _d(consumer_params.consumer_norms.T)

    Q_total = (
        _d(consumer_params.consumer_norms.avg_hot_and_cold_water_norms_per_day)
        * num_of_measurers
        * working_shifts
        / _d(1000)
    )
    Q_hot = (
        (
            _d(consumer_params.consumer_norms.avg_hot_water_norms_per_day)
        )
        * num_of_measurers
        * working_shifts
        / _d(1000)
    )
    Q_cold = (
        (
            _d(consumer_params.consumer_norms.avg_hot_and_cold_water_norms_per_day) 
            - _d(consumer_params.consumer_norms.avg_hot_water_norms_per_day)
        )
        * num_of_measurers
        * working_shifts
        / _d(1000)
    )


    return TotalDayConsumptionReportData(
        Q_total=Q_total,
        Q_hot=Q_hot,
        Q_cold=Q_cold,
    )


def calculate_heat_consumption(
    consumer_params: WaterConsumerParams,
    avg_hour_consumption: AvgHourConsumptionReportData,
    max_hour_consumption: MaxHourConsumptionReportData) -> HeatConsumptionReportData:

    temp_diff = _d(consumer_params.temp_hot) - _d(consumer_params.temp_cold)

    Qht = (
        _d(1.16) 
        * avg_hour_consumption.q_hot 
        * temp_diff
        + max_hour_consumption.q_hot * _d(0.3)
    )
    Qhrt = (
        _d(1.16) 
        * max_hour_consumption.q_hot 
        * temp_diff
        + max_hour_consumption.q_hot * _d(0.3)
    )

    return HeatConsumptionReportData(
        Q_avg_hour=Qht,
        Q_max_hour=Qhrt,
    ) 


def calculate_avg_hour_consumption(
    consumer_params: WaterConsumerParams,
    consumer: WaterConsumerNorms,
    num_of_measurers: int,
) -> AvgHourConsumptionReportData:
    if consumer_params.consumer_norms.T == 24:
        working_shifts = _d(1)
    else:
        working_shifts = _d(consumer_params.work_hours) / _d(consumer_params.consumer_norms.T)

    # TODO: ask and check
    
    qT_tot = (
        _d(consumer.avg_hot_and_cold_water_norms_per_day)
        * num_of_measurers
        / (1000 * _d(consumer.T) * working_shifts)
    )
    qT_h = (
        _d(consumer.avg_hot_water_norms_per_day)
        * num_of_measurers
        / (1000 * _d(consumer.T) * working_shifts)
    )
    qT_c = (
        (
            _d(consumer.avg_hot_and_cold_water_norms_per_day) 
            - _d(consumer.avg_hot_water_norms_per_day)
        )
        * num_of_measurers
        / (1000 * _d(consumer.T) * working_shifts)
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
            * second_consumption.P_hot
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
        alpha_total=alpha_hr_tot, alpha_cold=alpha_hr_c, alpha_hot=alpha_hr_h,
        P_total=Phr_tot, P_hot=Phr_h, P_cold=Phr_c,
        q_total=qhr_tot, q_hot=qhr_h, q_cold=qhr_c,
    )


def calculate_max_per_sec_consumption(
    consumer: WaterConsumerNorms,
    num_of_measurers: int,
    num_of_devices: int,
    num_of_devices_with_hot_water: int) -> SecondConsumptionReportData:

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
        alpha_total=alpha_tot, alpha_cold=alpha_c, alpha_hot=alpha_h,
        P_total=P_tot, P_hot=P_h, P_cold=P_c,
        q_total=q_tot, q_hot=q_h, q_cold=q_c,
    )


def _d(v: int | float | Decimal | Literal[0]) -> Decimal:
    return Decimal(v)

def _r(v: int | float | Decimal | Literal[0]) -> Decimal | float:
    return round(v, 3)