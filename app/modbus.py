from pyModbusTCP.client import ModbusClient
import logging

ip_address = '10.50.17.49'
port = 502
c = ModbusClient(host=ip_address, port=port, auto_open=True, debug=True)

def control_lights(address, state):
    try:
        logging.debug(f"Control Lights: Address: {address}, State: {state}")
        c.write_single_coil(address, state)
    except Exception as e:
        logging.error("Error in control_lights:", exc_info=True)

def turn_off_lights(start_address, end_address):
    for address in range(start_address, end_address + 1):
        control_lights(address, False)
        logging.debug(f"Turning off address: {address}")

def read_coils_status(offset_value, selected):
    try:
        coils_l = c.read_holding_registers(offset_value, 5)
        if coils_l:
            logging.debug(f"Read Coils Status: {coils_l}")
            greenv, whitev, bluev, yellowv, redv = coils_l
            logging.debug(f'selected: {selected}')
            logging.debug(f'Green ad #{offset_value}: {greenv}')
            logging.debug(f'White ad #{offset_value + 1}: {whitev}')
            logging.debug(f'Blue ad #{offset_value + 2}: {bluev}')
            logging.debug(f'Yellow ad #{offset_value + 3}: {yellowv}')
            logging.debug(f'Red ad #{offset_value + 4}: {redv}')
            return {
                'green': greenv,
                'white': whitev,
                'blue': bluev,
                'yellow': yellowv,
                'red': redv
            }
        else:
            logging.warning("Failed to read coils (no response)")
    except Exception as e:
        logging.error("Error in read_coils_status:", exc_info=True)
    return None
