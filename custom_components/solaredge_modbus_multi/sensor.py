import logging
import re

from typing import Optional, Dict, Any
from datetime import datetime

from homeassistant.core import HomeAssistant

from homeassistant.core import callback
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from homeassistant.const import (
    CONF_NAME,
    ENERGY_KILO_WATT_HOUR,
    POWER_WATT, POWER_KILO_WATT, POWER_VOLT_AMPERE, POWER_VOLT_AMPERE_REACTIVE,
    ELECTRIC_CURRENT_AMPERE, ELECTRIC_POTENTIAL_VOLT,
    PERCENTAGE, TEMP_CELSIUS, FREQUENCY_HERTZ,
)

from homeassistant.components.sensor import (
    STATE_CLASS_TOTAL_INCREASING,
    STATE_CLASS_MEASUREMENT,
    SensorDeviceClass,
    SensorEntity,
)

from .const import (
    DOMAIN,
    SUNSPEC_NOT_IMPL_UINT16, SUNSPEC_NOT_IMPL_INT16, SUNSPEC_NOT_IMPL_UINT32,
    SUNSPEC_NOT_ACCUM_ACC32, SUNSPEC_ACCUM_LIMIT, 
    DEVICE_STATUS, DEVICE_STATUS_DESC,
    VENDOR_STATUS, SUNSPEC_DID, METER_EVENTS,
    ENERGY_VOLT_AMPERE_HOUR, ENERGY_VOLT_AMPERE_REACTIVE_HOUR,
)

from .helpers import (
    update_accum,
    scale_factor,
    watts_to_kilowatts
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    hub = hass.data[DOMAIN][config_entry.entry_id]

    entities = []
        
    for inverter in hub.inverters:
        entities.append(Manufacturer(inverter, config_entry))
        entities.append(Model(inverter, config_entry))
        entities.append(Version(inverter, config_entry))
        entities.append(SerialNumber(inverter, config_entry))
        entities.append(DeviceAddress(inverter, config_entry))
        entities.append(SunspecDID(inverter, config_entry))
        entities.append(ACCurrentSensor(inverter, config_entry))
        entities.append(ACCurrentSensor(inverter, config_entry, 'A'))
        entities.append(ACCurrentSensor(inverter, config_entry, 'B'))
        entities.append(ACCurrentSensor(inverter, config_entry, 'C'))
        entities.append(VoltageSensor(inverter, config_entry, 'AB'))
        entities.append(VoltageSensor(inverter, config_entry, 'BC'))
        entities.append(VoltageSensor(inverter, config_entry, 'CA'))
        entities.append(VoltageSensor(inverter, config_entry, 'AN'))
        entities.append(VoltageSensor(inverter, config_entry, 'BN'))
        entities.append(VoltageSensor(inverter, config_entry, 'CN'))
        entities.append(ACPower(inverter, config_entry))
        entities.append(ACFrequency(inverter, config_entry))
        entities.append(ACVoltAmp(inverter, config_entry))
        entities.append(ACVoltAmpReactive(inverter, config_entry))
        entities.append(ACPowerFactor(inverter, config_entry))
        entities.append(ACEnergy(inverter, config_entry))
        entities.append(DCCurrent(inverter, config_entry))
        entities.append(DCVoltage(inverter, config_entry))
        entities.append(DCPower(inverter, config_entry))
        entities.append(HeatSinkTemperature(inverter, config_entry))
        entities.append(Status(inverter,config_entry))
        entities.append(StatusText(inverter,config_entry))
        entities.append(StatusVendor(inverter, config_entry))

    for meter in hub.meters:
        entities.append(Manufacturer(meter, config_entry))
        entities.append(Model(meter, config_entry))
        entities.append(Option(meter, config_entry))
        entities.append(Version(meter, config_entry))
        entities.append(SerialNumber(meter, config_entry))
        entities.append(DeviceAddress(meter, config_entry))
        entities.append(DeviceAddressParent(meter, config_entry))
        entities.append(SunspecDID(meter, config_entry))
        entities.append(MeterEvents(meter, config_entry))
        entities.append(ACCurrentSensor(meter, config_entry))
        entities.append(ACCurrentSensor(meter, config_entry, 'A'))
        entities.append(ACCurrentSensor(meter, config_entry, 'B'))
        entities.append(ACCurrentSensor(meter, config_entry, 'C'))
        entities.append(VoltageSensor(meter, config_entry, 'LN'))
        entities.append(VoltageSensor(meter, config_entry, 'AN'))
        entities.append(VoltageSensor(meter, config_entry, 'BN'))
        entities.append(VoltageSensor(meter, config_entry, 'CN'))
        entities.append(VoltageSensor(meter, config_entry, 'LL'))
        entities.append(VoltageSensor(meter, config_entry, 'AB'))
        entities.append(VoltageSensor(meter, config_entry, 'BC'))
        entities.append(VoltageSensor(meter, config_entry, 'CA'))
        entities.append(ACFrequency(meter, config_entry))
        entities.append(ACPower(meter, config_entry))
        entities.append(ACPower(meter, config_entry, 'A'))
        entities.append(ACPower(meter, config_entry, 'B'))
        entities.append(ACPower(meter, config_entry, 'C'))
        entities.append(ACVoltAmp(meter, config_entry))
        entities.append(ACVoltAmp(meter, config_entry, 'A'))
        entities.append(ACVoltAmp(meter, config_entry, 'B'))
        entities.append(ACVoltAmp(meter, config_entry, 'C'))
        entities.append(ACVoltAmpReactive(meter, config_entry))
        entities.append(ACVoltAmpReactive(meter, config_entry, 'A'))
        entities.append(ACVoltAmpReactive(meter, config_entry, 'B'))
        entities.append(ACVoltAmpReactive(meter, config_entry, 'C'))
        entities.append(ACPowerFactor(meter, config_entry))
        entities.append(ACPowerFactor(meter, config_entry, 'A'))
        entities.append(ACPowerFactor(meter, config_entry, 'B'))
        entities.append(ACPowerFactor(meter, config_entry, 'C'))
        entities.append(ACEnergy(meter, config_entry, 'Exported'))
        entities.append(ACEnergy(meter, config_entry, 'Exported_A'))
        entities.append(ACEnergy(meter, config_entry, 'Exported_B'))
        entities.append(ACEnergy(meter, config_entry, 'Exported_C'))
        entities.append(ACEnergy(meter, config_entry, 'Imported'))
        entities.append(ACEnergy(meter, config_entry, 'Imported_A'))
        entities.append(ACEnergy(meter, config_entry, 'Imported_B'))
        entities.append(ACEnergy(meter, config_entry, 'Imported_C'))

        #"EXPORTED_VA": ["Exported VAh", "exportedva", ENERGY_VOLT_AMPERE_HOUR, None, None],
        #"EXPORTED_VA_A": ["Exported A VAh", "exportedvaa", ENERGY_VOLT_AMPERE_HOUR, None, None],
        #"EXPORTED_VA_B": ["Exported B VAh", "exportedvab", ENERGY_VOLT_AMPERE_HOUR, None, None],
        #"EXPORTED_VA_C": ["Exported C VAh", "exportedvac", ENERGY_VOLT_AMPERE_HOUR, None, None],

        #"IMPORTED_VA": ["Imported VAh", "importedva", ENERGY_VOLT_AMPERE_HOUR, None, None],
        #"IMPORTED_VA_A": ["Imported A VAh", "importedvaa", ENERGY_VOLT_AMPERE_HOUR, None, None],
        #"IMPORTED_VA_B": ["Imported B VAh", "importedvab", ENERGY_VOLT_AMPERE_HOUR, None, None],
        #"IMPORTED_VA_C": ["Imported C VAh", "importedvac", ENERGY_VOLT_AMPERE_HOUR, None, None],

        #"IMPORT_varh_Q1": ["Imported varh Q1", "importvarhq1", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q1_A": ["Imported varh Q1 A", "importvarhq1a", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q1_B": ["Imported varh Q1 B", "importvarhq1b", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q1_C": ["Imported varh Q1 C", "importvarhq1c", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q2": ["Imported varh Q2", "importvarhq2", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q2_A": ["Imported varh Q2 A", "importvarhq2a", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q2_B": ["Imported varh Q2 B", "importvarhq2b", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"IMPORT_varh_Q2_C": ["Imported varh Q2 C", "importvarhq2c", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q3": ["Imported varh Q3", "importvarhq3", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q3_A": ["Exported varh Q3 A", "importvarhq3a", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q3_B": ["Exported varh Q3 B", "importvarhq3b", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q3_C": ["Exported varh Q3 C", "importvarhq3c", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q4": ["Exported varh Q4", "importvarhq4", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q4_A": ["Exported varh Q4 A", "importvarhq4a", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q4_B": ["Exported varh Q4 B", "importvarhq4b", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],
        #"EXPORT_varh_Q4_C": ["Exported varh Q4 C", "importvarhq4c", ENERGY_VOLT_AMPERE_REACTIVE_HOUR, None, None],

    for battery in hub.batteries:
        entities.append(Manufacturer(battery, config_entry))
        entities.append(Model(battery, config_entry))
        entities.append(Version(battery, config_entry))
        entities.append(SerialNumber(battery, config_entry))
        entities.append(DeviceAddress(battery, config_entry))
        entities.append(DeviceAddressParent(battery, config_entry))

    if entities:
        async_add_entities(entities)


class SolarEdgeSensorBase(SensorEntity):

    should_poll = False

    def __init__(self, platform, config_entry):
        """Initialize the sensor."""
        self._platform = platform
        self._config_entry = config_entry

    @property
    def device_info(self):
        return self._platform.device_info

    @property
    def config_entry_id(self):
        return self._config_entry.entry_id

    @property
    def config_entry_name(self):
        return self._config_entry.data['name']

    @property
    def available(self) -> bool:
        return self._platform.online

    async def async_added_to_hass(self):
        self._platform.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self):
        self._platform.remove_callback(self.async_write_ha_state)


class SerialNumber(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_serial_number"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Serial Number"

    @property
    def native_value(self):
        return self._platform.serial

class Manufacturer(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_manufacturer"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Manufacturer"

    @property
    def native_value(self):
        return self._platform.manufacturer

class Model(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_model"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Model"

    @property
    def native_value(self):
        return self._platform.model

class Option(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_option"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Option"
            
    @property
    def entity_registry_enabled_default(self) -> bool:
        if len(self._platform.option) == 0:
            return False
        else:
            return True

    @property
    def native_value(self):
        if len(self._platform.option) > 0:
            return self._platform.option
        else:
            return None

class Version(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_version"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Version"

    @property
    def native_value(self):
        return self._platform.fw_version

class DeviceAddress(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_device_id"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Device ID"

    @property
    def native_value(self):
        return self._platform.device_address

class DeviceAddressParent(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_parent_device_id"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Parent Device ID"

    @property
    def native_value(self):
        return self._platform.inverter_unit_id

class SunspecDID(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_sunspec_device_id"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Sunspec Device ID"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['C_SunSpec_DID'] == SUNSPEC_NOT_IMPL_UINT16):
                return None
            
            else:
                return self._platform.decoded_model['C_SunSpec_DID']
        
        except TypeError:
            return None
                
    @property
    def extra_state_attributes(self):
        try:
            if self._platform.decoded_model['C_SunSpec_DID'] in SUNSPEC_DID:
                return {"description": SUNSPEC_DID[self._platform.decoded_model['C_SunSpec_DID']]}
            
            else:
                return None
        
        except KeyError:
            return None

class ACCurrentSensor(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.CURRENT
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase
        
        if self._platform.decoded_model['C_SunSpec_DID'] in [101,102,103]:
            self.SUNSPEC_NOT_IMPL = SUNSPEC_NOT_IMPL_UINT16
        elif self._platform.decoded_model['C_SunSpec_DID'] in [201,202,203,204]:
            self.SUNSPEC_NOT_IMPL = SUNSPEC_NOT_IMPL_INT16
        else:
            raise RuntimeError("ACCurrentSensor: Unknown C_SunSpec_DID {self._platform.decoded_model['C_SunSpec_DID']}")

    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_current"
        else:
            return f"{self._platform.model}_{self._platform.serial}_ac_current_{self._phase.lower()}"

    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC Current"
        else:
            return f"{self._platform._device_info['name']} AC Current {self._phase.upper()}"

    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_Current"
        else:
            model_key = f"AC_Current_{self._phase.upper()}"

        try:
            if (self._platform.decoded_model[model_key] == self.SUNSPEC_NOT_IMPL or
                self._platform.decoded_model['AC_Current_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
            
            else:
                return scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_Current_SF'])
        
        except TypeError:
            return None

class VoltageSensor(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.VOLTAGE
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = ELECTRIC_POTENTIAL_VOLT

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase

        if self._platform.decoded_model['C_SunSpec_DID'] in [101,102,103]:
            self.SUNSPEC_NOT_IMPL = SUNSPEC_NOT_IMPL_UINT16
        elif self._platform.decoded_model['C_SunSpec_DID'] in [201,202,203,204]:
            self.SUNSPEC_NOT_IMPL = SUNSPEC_NOT_IMPL_INT16
        else:
            raise RuntimeError("ACCurrentSensor: Unknown C_SunSpec_DID {self._platform.decoded_model['C_SunSpec_DID']}")


    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_voltage"
        else:
            return f"{self._platform.model}_{self._platform.serial}_ac_voltage_{self._phase.lower()}"


    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC Voltage"
        else:
            return f"{self._platform._device_info['name']} AC Voltage {self._phase.upper()}"

    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_Voltage"
        else:
            model_key = f"AC_Voltage_{self._phase.upper()}"
                
        try:
            if (self._platform.decoded_model[model_key] == self.SUNSPEC_NOT_IMPL or
                self._platform.decoded_model['AC_Voltage_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
            
            else:
                value = scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_Voltage_SF'])
                return round(value, abs(self._platform.decoded_model['AC_Voltage_SF']))
        
        except TypeError:
            return None

class ACPower(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.POWER
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = POWER_WATT
    icon = 'mdi:solar-power'

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase

    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_power"
        else:
            return f"{self._platform.model}_{self._platform.serial}_ac_power_{self._phase.lower()}"

    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC Power"
        else:
            return f"{self._platform._device_info['name']} AC Power {self._phase.upper()}"

    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_Power"
        else:
            model_key = f"AC_Power_{self._phase.upper()}"

        try:
            if (self._platform.decoded_model[model_key] == SUNSPEC_NOT_IMPL_INT16 or
                self._platform.decoded_model['AC_Power_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_Power_SF'])
                return round(value, abs(self._platform.decoded_model['AC_Power_SF']))
                
        except TypeError:
            return None

class ACFrequency(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.FREQUENCY
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = FREQUENCY_HERTZ

    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""

    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_ac_frequency"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} AC Frequency"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['AC_Frequency'] == SUNSPEC_NOT_IMPL_UINT16 or
                self._platform.decoded_model['AC_Frequency_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model['AC_Frequency'], self._platform.decoded_model['AC_Frequency_SF'])
                return round(value, abs(self._platform.decoded_model['AC_Frequency_SF']))
                
        except TypeError:
            return None

class ACVoltAmp(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.APPARENT_POWER
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = POWER_VOLT_AMPERE

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase

    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_va"
        else:
            return f"{self._platform.model}_{self._platform.serial}_ac_va_{self._phase.lower()}"

    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC VA"
        else:
            return f"{self._platform._device_info['name']} AC VA {self._phase.upper()}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        return False

    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_VA"
        else:
            model_key = f"AC_VA_{self._phase.upper()}"

        try:
            if (self._platform.decoded_model[model_key] == SUNSPEC_NOT_IMPL_INT16 or
                self._platform.decoded_model['AC_VA_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_VA_SF'])
                return round(value, abs(self._platform.decoded_model['AC_VA_SF']))
                
        except TypeError:
            return None

class ACVoltAmpReactive(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.REACTIVE_POWER
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = POWER_VOLT_AMPERE_REACTIVE

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase

    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_var"
        else:
            return f"{self._platform.model}_{self._platform.serial}_ac_var_{self._phase.lower()}"

    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC var"
        else:
            return f"{self._platform._device_info['name']} AC var {self._phase.upper()}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        return False

    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_var"
        else:
            model_key = f"AC_var_{self._phase.upper()}"

        try:
            if (self._platform.decoded_model[model_key] == SUNSPEC_NOT_IMPL_INT16 or
                self._platform.decoded_model['AC_var_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_var_SF'])
                return round(value, abs(self._platform.decoded_model['AC_var_SF']))
                
        except TypeError:
            return None

class ACPowerFactor(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.POWER_FACTOR
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = PERCENTAGE

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase

    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_pf"
        else:
            return f"{self._platform.model}_{self._platform.serial}_ac_pf_{self._phase.lower()}"

    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC PF"
        else:
            return f"{self._platform._device_info['name']} AC PF {self._phase.upper()}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        return False

    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_PF"
        else:
            model_key = f"AC_PF_{self._phase.upper()}"

        try:
            if (self._platform.decoded_model[model_key] == SUNSPEC_NOT_IMPL_INT16 or
                self._platform.decoded_model['AC_PF_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_PF_SF'])
                return round(value, abs(self._platform.decoded_model['AC_PF_SF']))
                
        except TypeError:
            return None

class ACEnergy(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.ENERGY
    state_class = STATE_CLASS_TOTAL_INCREASING
    native_unit_of_measurement = ENERGY_KILO_WATT_HOUR

    def __init__(self, platform, config_entry, phase: str = None):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        self._phase = phase
        self.last = None

        if self._platform.decoded_model['C_SunSpec_DID'] in [101,102,103]:
            self.SUNSPEC_NOT_IMPL = SUNSPEC_NOT_IMPL_UINT16
        elif self._platform.decoded_model['C_SunSpec_DID'] in [201,202,203,204]:
            self.SUNSPEC_NOT_IMPL = SUNSPEC_NOT_IMPL_INT16
        else:
            raise RuntimeError("ACEnergy: Unknown C_SunSpec_DID {self._platform.decoded_model['C_SunSpec_DID']}")

    @property
    def icon(self) -> str:
        if self._phase is None:
            return None
            
        elif re.match('import', self._phase.lower()):
            return 'mdi:transmission-tower-export'
            
        elif re.match('export', self._phase.lower()):
            return 'mdi:transmission-tower-import'
        
        else:
            return None

    @property
    def unique_id(self) -> str:
        if self._phase == None:
            return f"{self._platform.model}_{self._platform.serial}_ac_energy_kwh"
        else:
            return f"{self._platform.model}_{self._platform.serial}_{self._phase.lower()}_kwh"
    
    @property
    def name(self) -> str:
        if self._phase == None:
            return f"{self._platform._device_info['name']} AC Energy kWh"
        else:
            return f"{self._platform._device_info['name']} {self._phase} kWh"
    
    @property
    def native_value(self):
        if self._phase == None:
            model_key = "AC_Energy_WH"
        else:
            model_key = f"AC_Energy_WH_{self._phase}"

        try:
            if (self._platform.decoded_model[model_key] == SUNSPEC_NOT_ACCUM_ACC32 or
                self._platform.decoded_model[model_key] > SUNSPEC_ACCUM_LIMIT or
                self._platform.decoded_model['AC_Energy_WH_SF'] == self.SUNSPEC_NOT_IMPL
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model[model_key], self._platform.decoded_model['AC_Energy_WH_SF'])
                value_kw = watts_to_kilowatts(value)
                
                try:
                    return update_accum(self, value, value_kw)
                except:
                    return None
                
        except TypeError:
            return None

class DCCurrent(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.CURRENT
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = ELECTRIC_CURRENT_AMPERE
    icon = 'mdi:current-dc'

    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""

    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_dc_current"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} DC Current"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_DC_Current'] == SUNSPEC_NOT_IMPL_UINT16 or
                self._platform.decoded_model['I_DC_Current_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model['I_DC_Current'], self._platform.decoded_model['I_DC_Current_SF'])
                return round(value, abs(self._platform.decoded_model['I_DC_Current_SF']))
        
        except TypeError:
            return None  

class DCVoltage(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.VOLTAGE
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = ELECTRIC_POTENTIAL_VOLT

    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""

    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_dc_voltage"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} DC Voltage"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_DC_Voltage'] == SUNSPEC_NOT_IMPL_UINT16 or
                self._platform.decoded_model['I_DC_Voltage_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model['I_DC_Voltage'], self._platform.decoded_model['I_DC_Voltage_SF'])
                return round(value, abs(self._platform.decoded_model['I_DC_Voltage_SF']))
        
        except TypeError:
            return None  

class DCPower(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.POWER
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = POWER_WATT
    icon = 'mdi:solar-power'

    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""

    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_dc_power"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} DC Power"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_DC_Power'] == SUNSPEC_NOT_IMPL_INT16 or
                self._platform.decoded_model['I_DC_Power_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model['I_DC_Power'], self._platform.decoded_model['I_DC_Power_SF'])
                return round(value, abs(self._platform.decoded_model['I_DC_Power_SF']))
        
        except TypeError:
            return None  

class HeatSinkTemperature(SolarEdgeSensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    state_class = STATE_CLASS_MEASUREMENT
    native_unit_of_measurement = TEMP_CELSIUS

    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""

    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_temp_sink"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Temp Sink"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_Temp_Sink'] == SUNSPEC_NOT_IMPL_INT16 or
                self._platform.decoded_model['I_Temp_SF'] == SUNSPEC_NOT_IMPL_INT16
            ):
                return None
    
            else:
                value = scale_factor(self._platform.decoded_model['I_Temp_Sink'], self._platform.decoded_model['I_Temp_SF'])
                return round(value, abs(self._platform.decoded_model['I_Temp_SF']))
        
        except TypeError:
            return None  

class Status(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_status"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Status"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_Status'] == SUNSPEC_NOT_IMPL_INT16):
                return None
            
            else:
                return self._platform.decoded_model['I_Status']
        
        except TypeError:
            return None
                
    @property
    def extra_state_attributes(self):
        try:
            if self._platform.decoded_model['I_Status'] in DEVICE_STATUS_DESC:
                return {"description": DEVICE_STATUS_DESC[self._platform.decoded_model['I_Status']]}
            
            else:
                return None
        
        except KeyError:
            return None

class StatusText(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_status_text"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Status Text"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_Status'] == SUNSPEC_NOT_IMPL_INT16):
                return None
            
            else:
                return DEVICE_STATUS[self._platform.decoded_model['I_Status']]
        
        except TypeError:
            return None
        
        except KeyError:
            return None

class StatusVendor(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_status_vendor"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Status Vendor"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_Status_Vendor'] == SUNSPEC_NOT_IMPL_INT16):
                return None
            
            else:
                return self._platform.decoded_model['I_Status_Vendor']
        
        except TypeError:
            return None
                
    @property
    def extra_state_attributes(self):
        try:
            if self._platform.decoded_model['I_Status_Vendor'] in VENDOR_STATUS:
                return {"description": VENDOR_STATUS[self._platform.decoded_model['I_Status_Vendor']]}
            
            else:
                return None
        
        except KeyError:
            return None

class StatusVendorText(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_status_vendor"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Status Vendor"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['I_Status_Vendor'] == SUNSPEC_NOT_IMPL_INT16):
                return None
            
            else:
                return self._platform.decoded_model['I_Status_Vendor']
        
        except TypeError:
            return None
                
    @property
    def extra_state_attributes(self):
        try:
            if self._platform.decoded_model['I_Status_Vendor'] in VENDOR_STATUS:
                return {"description": VENDOR_STATUS[self._platform.decoded_model['I_Status_Vendor']]}
            
            else:
                return None
        
        except KeyError:
            return None

class MeterEvents(SolarEdgeSensorBase):
    entity_category = EntityCategory.DIAGNOSTIC
    
    def __init__(self, platform, config_entry):
        super().__init__(platform, config_entry)
        """Initialize the sensor."""
        
    @property
    def unique_id(self) -> str:
        return f"{self._platform.model}_{self._platform.serial}_meter_events"

    @property
    def name(self) -> str:
        return f"{self._platform._device_info['name']} Meter Events"

    @property
    def native_value(self):
        try:
            if (self._platform.decoded_model['M_Events'] == SUNSPEC_NOT_IMPL_UINT32):
                return None
            
            else:
                return self._platform.decoded_model['M_Events']
        
        except TypeError:
            return None
                
    @property
    def extra_state_attributes(self):
        try:
            m_events_active = []
            if int(str(self._platform.decoded_model['M_Events']),16) == 0x0:
                return {"description": str(m_events_active)}
            else:
                for i in range(2,31):
                    if (int(str(self._platform.decoded_model['M_Events']),16) & (1 << i)):
                        m_events_active.append(METER_EVENTS[i])
                return {"description": str(m_events_active)}
        
        except KeyError:
            return None
