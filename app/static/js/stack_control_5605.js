document.addEventListener("DOMContentLoaded", function() {
    var dropdownMenu = document.getElementById("dropdown-menu");

    if (dropdownMenu) {
        var options = [
            "5605 Building", "Tire FG", "Tire Subs", "Pump FG", "Pump Subs", 
            "Omni FG", "Omni Subs", "Sidewash FG", "Arches", "Top Clean", 
            "Wraps", "Subassembly", "Brushes-Weights", "RW03", "RW04", 
            "Wash Tank 1", "CTBPYTH", "Fastems (H1,H2,H3)", "Manual MS", 
            "AW001-AW002", "AW003-AW004", "AW005-AW006", "AW007-AW008", 
            "AW009-AW010", "AW011-AW012", "AW013-AW014", "AW015-AW016", "TIG"
        ];

        // Populate dropdown menu
        options.forEach(function(option) {
            var el = document.createElement("option");
            el.textContent = option;
            el.value = option;
            dropdownMenu.appendChild(el);
        });

        var buttons = {
            "red-button": 4,
            "yellow-button": 3,
            "blue-button": 2,
            "white-button": 1,
            "green-button": 0,
            "off-button": -1
        };

        Object.keys(buttons).forEach(function(buttonId) {
            var button = document.getElementById(buttonId);
            if (button) {
                button.addEventListener("click", function() {
                    var selected = dropdownMenu.value;
                    var state = buttonId !== "off-button";

                    if (selected === "5605 Building") {
                        if (buttonId === "off-button") {
                            sendControlRequest(Array.from({ length: 171 }, (_, i) => i), false, selected);
                        } else {
                            var addressRange = Array.from({ length: 171 }, (_, i) => i);
                            var addresses = addressRange.filter(address => address % 5 === buttons[buttonId]);
                            sendControlRequest(addresses, state, selected);
                        }
                    } else {
                        var offset = options.indexOf(selected) * 5;
                        if (buttonId === "off-button") {
                            sendControlRequest(Array.from({ length: 5 }, (_, i) => offset + i), false, selected);
                        } else {
                            var address = offset + buttons[buttonId];
                            sendControlRequest([address], state, selected);
                        }
                    }
                });
            }
        });

        function sendControlRequest(addresses, state, selected) {
            var requests = addresses.map(address => {
                return fetch('/api/control_5605', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ address: address, state: state, selected: selected })
                }).then(response => {
                    if (response.status === 403) {
                        return response.json().then(data => {
                            return { success: false, message: data.message };
                        });
                    }
                    return response.json();
                });
            });

            Promise.all(requests).then(results => {
                var unauthorized = results.find(result => result.success === false && result.message);
                if (unauthorized) {
                    $('#unauthorizedModal').modal('show');
                } else {
                    fetchStatus(selected);
                }
            }).catch(error => {
                console.error("Error controlling light:", error);
            });
        }

        function fetchStatus(selected) {
            fetch(`/api/status_5605?selected=${selected}`)
                .then(response => response.json())
                .then(data => {
                    if (data && data.status) {
                        updateOverlay(data.status);
                    } else {
                        console.error("Failed to get status data");
                    }
                })
                .catch(error => console.error("Error fetching status:", error));
        }

        function updateOverlay(status) {
            document.getElementById('green-overlay').style.backgroundColor = status.green ? 'rgba(76, 175, 80, 0.7)' : 'transparent';
            document.getElementById('white-overlay').style.backgroundColor = status.white ? 'rgba(169, 169, 169, 0.7)' : 'transparent';
            document.getElementById('blue-overlay').style.backgroundColor = status.blue ? 'rgba(47, 0, 255, 0.7)' : 'transparent';
            document.getElementById('yellow-overlay').style.backgroundColor = status.yellow ? 'rgba(255, 238, 0, 0.7)' : 'transparent';
            document.getElementById('red-overlay').style.backgroundColor = status.red ? 'rgba(255, 0, 0, 0.7)' : 'transparent';
        }

        dropdownMenu.addEventListener("change", function() {
            var selected = dropdownMenu.value;
            fetchStatus(selected);
        });

        dropdownMenu.dispatchEvent(new Event('change'));
    }
});
