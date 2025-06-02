# https://telegra.ph/Datchik-kachestva-vozduha-EFEKTA-Smart-Air-Quality-Box--Zigbee-30-08-23
from enum import Enum
from typing import Final

from zigpy.profiles import zha
from zigpy.quirks import CustomCluster
from zigpy.quirks.v2 import (
    QuirkBuilder,
    ReportingConfig,
    SensorDeviceClass,
    SensorStateClass,
)
from zigpy.quirks.v2.homeassistant.number import NumberDeviceClass
import zigpy.types as t
from zigpy.zcl import ClusterType
from zigpy.zcl.foundation import ZCLAttributeDef
from zigpy.zcl.clusters.general import Basic, AnalogInput, OnOff
from zigpy.zcl.clusters.measurement import (
    PM25,
    CarbonDioxideConcentration,
    RelativeHumidity,
    TemperatureMeasurement,
    PressureMeasurement,
)
from zigpy.quirks.v2.homeassistant import (
    UnitOfTime,
    UnitOfTemperature,
    CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
)

EFEKTA = "EfektaLab"


class LocalSensorDeviceClass(Enum):
    PM4 = "pm4"
    PM_SIZE = "pm_size"


class VOCIndex(AnalogInput, CustomCluster):
    name: str = "VOC Index"
    ep_attribute: str = "voc_index"

    class AttributeDefs(AnalogInput.AttributeDefs):
        enable_voc: Final = ZCLAttributeDef(id=0x0220, type=t.Bool, access="rw")
        high_voc: Final = ZCLAttributeDef(id=0x0221, type=t.uint16_t, access="rw")
        low_voc: Final = ZCLAttributeDef(id=0x0222, type=t.uint16_t, access="rw")


class PMMeasurement(PM25, CustomCluster):
    class AttributeDefs(PM25.AttributeDefs):
        pm1: Final = ZCLAttributeDef(id=0x0601, type=t.Single, access="r")
        pm4: Final = ZCLAttributeDef(id=0x0605, type=t.Single, access="r")
        pm10: Final = ZCLAttributeDef(id=0x0602, type=t.Single, access="r")
        pm_size: Final = ZCLAttributeDef(id=0x0603, type=t.Single, access="r")
        aqi_25_index: Final = ZCLAttributeDef(id=0x0604, type=t.Single, access="r")
        enable_pm25: Final = ZCLAttributeDef(id=0x0220, type=t.Bool, access="rw")
        high_pm25: Final = ZCLAttributeDef(id=0x0221, type=t.uint16_t, access="rw")
        low_pm25: Final = ZCLAttributeDef(id=0x0222, type=t.uint16_t, access="rw")
        auto_clean_interval: Final = ZCLAttributeDef(id=0x0330, type=t.uint8_t, access="rw")
        manual_clean: Final = ZCLAttributeDef(id=0x0331, type=t.Bool, access="rw")


class CO2Measurement(CarbonDioxideConcentration, CustomCluster):
    class AttributeDefs(CarbonDioxideConcentration.AttributeDefs):
        reading_delay: Final = ZCLAttributeDef(id=0x0201, type=t.uint16_t, access="rw")
        alarm: Final = ZCLAttributeDef(id=0x0240, type=t.Bool, access="rw")
        light_indicator: Final = ZCLAttributeDef(id=0x0211, type=t.Bool, access="rw")
        light_indicator_level: Final = ZCLAttributeDef(id=0x0209, type=t.uint8_t, access="rw")
        forced_recalibration: Final = ZCLAttributeDef(id=0x0202, type=t.Bool, access="rw")
        manual_forced_recalibration: Final = ZCLAttributeDef(id=0x0207, type=t.uint16_t, access="rw")
        automatic_self_calibration: Final = ZCLAttributeDef(id=0x0402, type=t.Bool, access="rw")
        factory_reset_co2: Final = ZCLAttributeDef(id=0x0206, type=t.Bool, access="rw")
        enable_co2_gas: Final = ZCLAttributeDef(id=0x0220, type=t.Bool, access="rw")
        high_co2_gas: Final = ZCLAttributeDef(id=0x0221, type=t.uint16_t, access="rw")
        low_co2_gas: Final = ZCLAttributeDef(id=0x0222, type=t.uint16_t, access="rw")


class TempMeasurement(TemperatureMeasurement, CustomCluster):
    class AttributeDefs(TemperatureMeasurement.AttributeDefs):
        temperature_offset: Final = ZCLAttributeDef(id=0x0410, type=t.int16s, access="rw")


class RHMeasurement(RelativeHumidity, CustomCluster):
    class AttributeDefs(RelativeHumidity.AttributeDefs):
        humidity_offset: Final = ZCLAttributeDef(id=0x0210, type=t.int16s, access="rw")


(
    QuirkBuilder(EFEKTA, "EFEKTA_Smart_AQ_Box_R3")
    .replaces_endpoint(1, device_type=zha.DeviceType.SIMPLE_SENSOR)
    .replaces_endpoint(2, device_type=zha.DeviceType.SIMPLE_SENSOR)
    .replaces_endpoint(3, device_type=zha.DeviceType.SIMPLE_SENSOR)
    .replaces_endpoint(4, device_type=zha.DeviceType.SIMPLE_SENSOR)
    .replaces(Basic, endpoint_id=1)
    .replaces(OnOff, endpoint_id=1, cluster_type=ClusterType.Client)
    .replaces(CO2Measurement, endpoint_id=2)
    .replaces(PMMeasurement, endpoint_id=3)
    .replaces(VOCIndex, endpoint_id=4)
    .replaces(TempMeasurement, endpoint_id=4)
    .replaces(PressureMeasurement, endpoint_id=4)
    .replaces(RHMeasurement, endpoint_id=4)
    .sensor(
        VOCIndex.AttributeDefs.present_value.name,
        VOCIndex.cluster_id,
        endpoint_id=4,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.AQI,
        reporting_config=ReportingConfig(min_interval=30, max_interval=1800, reportable_change=1),
        translation_key="voc_index",
        fallback_name="VOC Index",
    )
    .switch(
        VOCIndex.AttributeDefs.enable_voc.name,
        VOCIndex.cluster_id,
        endpoint_id=4,
        translation_key="enable_voc",
        fallback_name="Enable VOC Control",
        unique_id_suffix="enable_voc",
    )
    .number(
        VOCIndex.AttributeDefs.high_voc.name,
        VOCIndex.cluster_id,
        endpoint_id=4,
        translation_key="high_voc",
        fallback_name="High VOC Border",
        unique_id_suffix="high_voc",
        min_value=0,
        max_value=500,
        device_class=SensorDeviceClass.AQI,
    )
    .number(
        VOCIndex.AttributeDefs.low_voc.name,
        VOCIndex.cluster_id,
        endpoint_id=4,
        translation_key="low_voc",
        fallback_name="Low VOC Border",
        unique_id_suffix="low_voc",
        min_value=0,
        max_value=500,
        device_class=SensorDeviceClass.AQI,
    )
    .number(
        TempMeasurement.AttributeDefs.temperature_offset.name,
        TempMeasurement.cluster_id,
        endpoint_id=4,
        translation_key="temperature_offset",
        fallback_name="Adjust temperature",
        unique_id_suffix="temperature_offset",
        min_value=-50,
        max_value=50,
        step=0.1,
        multiplier=0.1,
        device_class=NumberDeviceClass.TEMPERATURE,
        unit=UnitOfTemperature.CELSIUS,
        mode="box",
    )
    .number(
        RHMeasurement.AttributeDefs.humidity_offset.name,
        RHMeasurement.cluster_id,
        endpoint_id=4,
        translation_key="humidity_offset",
        fallback_name="Adjust humidity",
        unique_id_suffix="humidity_offset",
        min_value=-50,
        max_value=50,
        step=1,
        device_class=NumberDeviceClass.HUMIDITY,
        unit=PERCENTAGE,
        mode="box",
    )
    .number(
        CO2Measurement.AttributeDefs.reading_delay.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="reading_delay",
        fallback_name="Setting the sensor reading delay",
        unique_id_suffix="reading_delay",
        min_value=6,
        max_value=600,
        step=1,
        device_class=NumberDeviceClass.DURATION,
        unit=UnitOfTime.SECONDS,
    )
    .switch(
        CO2Measurement.AttributeDefs.alarm.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="alarm",
        fallback_name="Alarm",
        unique_id_suffix="alarm",
    )
    .switch(
        CO2Measurement.AttributeDefs.light_indicator.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="light_indicator",
        fallback_name="Enable or Disable light indicator",
        unique_id_suffix="light_indicator",
    )
    .number(
        CO2Measurement.AttributeDefs.light_indicator_level.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="light_indicator_level",
        fallback_name="Light indicator level",
        unique_id_suffix="light_indicator_level",
        min_value=0,
        max_value=100,
        step=1,
        unit=PERCENTAGE,
    )
    .command_button(
        CO2Measurement.AttributeDefs.forced_recalibration.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="forced_recalibration",
        fallback_name="Start FRC (Perform Forced Recalibration of the CO2 Sensor)",
        unique_id_suffix="forced_recalibration",
    )
    .number(
        CO2Measurement.AttributeDefs.manual_forced_recalibration.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="manual_forced_recalibration",
        fallback_name="Start Manual FRC (Perform Forced Recalibration of the CO2 Sensor)",
        unique_id_suffix="manual_forced_recalibration",
        min_value=0,
        max_value=5000,
        step=1,
        unit=CONCENTRATION_PARTS_PER_MILLION,
    )
    .command_button(
        CO2Measurement.AttributeDefs.automatic_self_calibration.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="automatic_self_calibration",
        fallback_name="Automatic self calibration",
        unique_id_suffix="automatic_self_calibration",
    )
    .command_button(
        CO2Measurement.AttributeDefs.factory_reset_co2.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="factory_reset_co2",
        fallback_name="Factory Reset CO2 sensor",
        unique_id_suffix="factory_reset_co2",
    )
    .switch(
        CO2Measurement.AttributeDefs.enable_co2_gas.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="enable_co2_gas",
        fallback_name="Enable CO2 Gas Control",
        unique_id_suffix="enable_co2_gas",
    )
    .number(
        CO2Measurement.AttributeDefs.high_co2_gas.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="high_co2_gas",
        fallback_name="High CO2 Gas Border",
        unique_id_suffix="high_co2_gas",
        min_value=400,
        max_value=5000,
        step=1,
        unit=CONCENTRATION_PARTS_PER_MILLION,
    )
    .number(
        CO2Measurement.AttributeDefs.low_co2_gas.name,
        CO2Measurement.cluster_id,
        endpoint_id=2,
        translation_key="low_co2_gas",
        fallback_name="Low CO2 Gas Border",
        unique_id_suffix="low_co2_gas",
        min_value=400,
        max_value=5000,
        step=1,
        unit=CONCENTRATION_PARTS_PER_MILLION,
    )
    .sensor(
        PMMeasurement.AttributeDefs.pm1.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM1,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="pm1",
        fallback_name="PM1",
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .sensor(
        PMMeasurement.AttributeDefs.pm4.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=LocalSensorDeviceClass.PM4,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="pm4",
        fallback_name="PM4",
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .sensor(
        PMMeasurement.AttributeDefs.pm10.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.PM10,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="pm10",
        fallback_name="PM10",
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .sensor(
        PMMeasurement.AttributeDefs.pm_size.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=LocalSensorDeviceClass.PM_SIZE,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="pm_size",
        fallback_name="Typical Particle Size",
        unit="µm",
    )
    .sensor(
        PMMeasurement.AttributeDefs.aqi_25_index.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        state_class=SensorStateClass.MEASUREMENT,
        device_class=SensorDeviceClass.AQI,
        reporting_config=ReportingConfig(min_interval=10, max_interval=120, reportable_change=1),
        translation_key="aqi_25_index",
        fallback_name="PM 2.5 INDEX",
        unit="PM2.5 Index",
    )
    .switch(
        PMMeasurement.AttributeDefs.enable_pm25.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        translation_key="enable_pm25",
        fallback_name="Enable PM2.5 Control",
        unique_id_suffix="enable_pm25",
    )
    .number(
        PMMeasurement.AttributeDefs.high_pm25.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        translation_key="high_pm25",
        fallback_name="High PM2.5 Border",
        unique_id_suffix="high_pm25",
        min_value=0,
        max_value=1000,
        step=1,
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .number(
        PMMeasurement.AttributeDefs.low_pm25.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        translation_key="low_pm25",
        fallback_name="Low PM2.5 Border",
        unique_id_suffix="low_pm25",
        min_value=0,
        max_value=1000,
        step=1,
        unit=CONCENTRATION_MICROGRAMS_PER_CUBIC_METER,
    )
    .number(
        PMMeasurement.AttributeDefs.auto_clean_interval.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        translation_key="auto_clean_interval",
        fallback_name="Auto Clean Interval",
        unique_id_suffix="auto_clean_interval",
        min_value=0,
        max_value=10,
        step=1,
        device_class=SensorDeviceClass.DURATION,
        unit=UnitOfTime.DAYS,
    )
    .command_button(
        PMMeasurement.AttributeDefs.manual_clean.name,
        PMMeasurement.cluster_id,
        endpoint_id=3,
        translation_key="manual_clean",
        fallback_name="Manual Clean",
        unique_id_suffix="manual_clean",
    )
    .add_to_registry()
)
