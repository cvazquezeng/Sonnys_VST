# app/routes/api.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
import threading
import logging
from ..modbus import control_lights, turn_off_lights, read_coils_status

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


@api_bp.route('/control', methods=['POST'])
@login_required
def control():
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
                real_address = start_address + (address % 5)  # Calculate the real address within the selected range
                threading.Thread(target=control_lights, args=(real_address, state)).start()

    logging.debug(f"Control request processed: Address: {address}, State: {state}, Selected: {selected_value}")
    return jsonify(success=True)

@api_bp.route('/status', methods=['GET'])
@login_required
def status():
    selected_value = request.args.get('selected')
    logging.debug(f"Selected value: {selected_value}")

    if selected_value in values_map:
        start_address = values_map[selected_value][0]
        logging.debug(f"Status request: Selected: {selected_value}, Start Address: {start_address}")
        status = read_coils_status(start_address, selected_value)
        if status:
            return jsonify({'status': status})
    logging.error(f"Invalid selected value: {selected_value}")
    return jsonify(success=False), 400

@api_bp.route('/continuous_status', methods=['GET'])
@login_required
def continuous_status():
    status_data = {}
    for option, (start_address, end_address) in values_map.items():
        status = read_coils_status(start_address, option)
        if status:
            status_data[option] = status

    return jsonify({'status': status_data})
