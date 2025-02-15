import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import light, rs485
from esphome.const import (
    CONF_ID,
    CONF_OUTPUT_ID,
    CONF_UPDATE_INTERVAL,
)
from .. import rs485_ns

DEPENDENCIES = ["rs485"]
RS485LightOutput = rs485_ns.class_("RS485LightOutput", light.LightOutput, cg.Component)

CONFIG_SCHEMA = (
    light.BINARY_LIGHT_SCHEMA.extend(
        {
            cv.GenerateID(CONF_OUTPUT_ID): cv.declare_id(RS485LightOutput),
        }
    )
    .extend(rs485.RS485_DEVICE_SCHEMA)
    .extend(cv.COMPONENT_SCHEMA)
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_OUTPUT_ID])
    light_var = cg.new_Pvariable(config[CONF_ID], var)
    cg.add(var.set_light(light_var))

    cg.add(cg.App.register_light(light_var))
    await cg.register_component(var, config)
    del config[CONF_UPDATE_INTERVAL]
    await cg.register_component(light_var, config)
    await light.setup_light_core_(light_var, var, config)

    await rs485.register_rs485_device(var, config)
