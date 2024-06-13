from flask import Blueprint, request, jsonify
from flask_login import login_required
import threading
import logging
from ..modbus import control_lights, turn_off_lights, read_coils_status
from ..modbus5607 import control_lights5607, turn_off_lights5607, read_coils_status5607
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

api_bp = Blueprint('api', __name__)

values_map = {
    "5605 Building": (0, 170),
    "Tire FG": (0, 4),
    "Tire Subs": (5, 9),
    "Pump FG": (10, 14),
    "Pump Subs": (15, 19),
    "Omni FG": (20, 24),
    "Omni Subs": (25, 29),
    "Sidewash FG": (30, 34),
    "Arches": (35, 39),
    "Top Clean": (40, 44),
    "Wraps": (45, 49),
    "Subassembly": (50, 54),
    "Brushes-Weights": (55, 59),
    "RW03": (60, 64),
    "RW04": (65, 69),
    "Wash Tank 1": (70, 74),
    "CTBPYTH": (75, 79),
    "Fastems (H1,H2,H3)": (80, 84),
    "Manual MS": (85, 89),
    "AW001-AW002": (90, 94),
    "AW003-AW004": (95, 99),
    "AW005-AW006": (100, 104),
    "AW007-AW008": (105, 109),
    "AW009-AW010": (110, 114),
    "AW011-AW012": (115, 119),
    "AW013-AW014": (120, 124),
    "AW015-AW016": (125, 129),
    "TIG": (130, 134)
}

values_map_5607 = {
    "5607 Building": (0, 170),
    "RW01": (0, 4),
    "RW02": (5, 9),
    "RW08": (10, 14),
    "RW05": (15, 19),
    "RW06E": (20, 24),
    "RW06W": (25, 29),
    "BLOWER": (30, 34),
    "Cloth": (35, 39),
    "ConvAssy": (40, 44),
    "Final": (45, 49),
    "Rollers": (50, 54),
    "Stargate": (55, 59),
    "SP-A": (60, 64),
    "SP-B": (65, 69),
    "SP-C": (70, 74),
    "Paint-Oven": (75, 79),
    "Wash Tank 2": (80, 84),
    "Exit Weld Booth": (85, 89),
    "Entrance Weld Booth": (90, 94),
    "SW001-SW002": (95, 99),
    "SW003-SW004": (100, 104),
    "SW005-SW006": (105, 109),
    "SW007": (110, 114)
}

@api_bp.route('/api/control_5605', methods=['POST'])
@login_required
def control5605():
    data = request.json
    address = data.get('address')
    state = data.get('state')
    selected_value = data.get('selected')
    logging.debug(f"Control request: Address: {address}, State: {state}, Selected: {selected_value}")

    if selected_value == "5605 Building":
        start_address, end_address = values_map[selected_value]
        if address == -1:
            threading.Thread(target=turn_off_lights, args=(start_address, end_address)).start()
        else:
            for addr in range(start_address, end_address + 1):
                if addr % 5 == address:
                    threading.Thread(target=control_lights, args=(addr, state)).start()
    else:
        if address == -1:
            start_address, end_address = values_map[selected_value]
            threading.Thread(target=turn_off_lights, args=(start_address, end_address)).start()
        elif address is not None and state is not None:
            if selected_value in values_map:
                start_address, end_address = values_map[selected_value]
                real_address = start_address + (address % 5)
                threading.Thread(target=control_lights, args=(real_address, state)).start()

    logging.debug(f"Control request processed: Address: {address}, State: {state}, Selected: {selected_value}")
    return jsonify(success=True)

@api_bp.route('/api/status_5605', methods=['GET'])
@login_required
def status5605():
    selected_value = request.args.get('selected')
    logging.debug(f"Selected value: {selected_value}")

    if selected_value in values_map:
        start_address = values_map[selected_value][0]
        logging.debug(f"Status request: Selected: {selected_value}, Start Address: {start_address}")
        status = read_coils_status(start_address, selected_value)
        logging.debug(f"Status for {selected_value}: {status}")
        if status:
            return jsonify({'status': status})
    logging.error(f"Invalid selected value: {selected_value}")
    return jsonify(success=False), 404

@api_bp.route('/api/control_5607', methods=['POST'])
@login_required
def control5607():
    data = request.json
    address = data.get('address')
    state = data.get('state')
    selected_value = data.get('selected')
    logging.debug(f"Control request: Address: {address}, State: {state}, Selected: {selected_value}")

    if selected_value == "5607 Building":
        start_address, end_address = values_map_5607[selected_value]
        if address == -1:
            threading.Thread(target=turn_off_lights5607, args=(start_address, end_address)).start()
        else:
            for addr in range(start_address, end_address + 1):
                if addr % 5 == address:
                    threading.Thread(target=control_lights5607, args=(addr, state)).start()
    else:
        if address == -1:
            start_address, end_address = values_map_5607[selected_value]
            threading.Thread(target=turn_off_lights5607, args=(start_address, end_address)).start()
        elif address is not None and state is not None:
            if selected_value in values_map_5607:
                start_address, end_address = values_map_5607[selected_value]
                real_address = start_address + (address % 5)
                threading.Thread(target=control_lights5607, args=(real_address, state)).start()

    logging.debug(f"Control request processed: Address: {address}, State: {state}, Selected: {selected_value}")
    return jsonify(success=True)

@api_bp.route('/api/status_5607', methods=['GET'])
@login_required
def status5607():
    selected_value = request.args.get('selected')
    logging.debug(f"Selected value: {selected_value}")

    if selected_value in values_map_5607:
        start_address = values_map_5607[selected_value][0]
        logging.debug(f"Status request: Selected: {selected_value}, Start Address: {start_address}")
        status = read_coils_status5607(start_address, selected_value)
        logging.debug(f"Status for {selected_value}: {status}")
        if status:
            return jsonify({'status': status})
    logging.error(f"Invalid selected value: {selected_value}")
    return jsonify(success=False), 404

@api_bp.route('/api/continuous_status_5605', methods=['GET'])
@login_required
def continuous_status_5605():
    status_data = {}
    for option, (start_address, end_address) in values_map.items():
        status = read_coils_status(start_address, option)
        if status:
            status_data[option] = status
        logging.debug(f"Status for {option}: {status}")

    return jsonify({'status': status_data})

@api_bp.route('/api/continuous_status_5607', methods=['GET'])
@login_required
def continuous_status_5607():
    status_data = {}
    for option, (start_address, end_address) in values_map_5607.items():
        status = read_coils_status5607(start_address, option)
        if status:
            status_data[option] = status
        logging.debug(f"Status for {option}: {status}")

    return jsonify({'status': status_data})
