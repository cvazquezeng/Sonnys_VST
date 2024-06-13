document.addEventListener("DOMContentLoaded", function() {
    var dropdownMenu = document.getElementById("dropdown-menu");

    if (dropdownMenu) {
        var options = [
            "5607 Building", "RW01", "RW02", "RW08", "RW05", 
            "RW06E", "RW06W", "BLOWER", "Cloth", 
            "ConvAssy", "Final", "Rollers", "Stargate", 
            "SP-A", "SP-B", "SP-C", "Paint-Oven", 
            "Wash Tank 2", "Exit Weld Booth", "Entrance Weld Booth", 
            "SW001-SW002", "SW003-SW004", 
            "SW005-SW006", "SW007"
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

                    if (selected === "5607 Building") {
                        if (buttonId === "off-button") {
                            sendControlRequest(-1, false, selected);
                        } else {
                            var addressRange = Array.from({ length: 115 }, (_, i) => i);
                            addressRange.forEach(address => {
                                if (address % 5 === buttons[buttonId]) {
                                    sendControlRequest(address, state, selected);
                                }
                            });
                        }
                    } else {
                        var offset = options.indexOf(selected) * 5;
                        if (buttonId === "off-button") {
                            for (var i = 0; i < 5; i++) {
                                sendControlRequest(offset + i, false, selected);
                            }
                        } else {
                            var address = offset + buttons[buttonId];
                            sendControlRequest(address, state, selected);
                        }
                    }
                });
            }
        });

        function sendControlRequest(address, state, selected) {
            fetch('/api/control_5607', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ address: address, state: state, selected: selected })
            }).then(response => response.json()).then(data => {
                if (data.success) {
                    setTimeout(function() {
                        fetchStatus(selected);
                    }, 500);
                } else {
                    console.error("Failed to control light");
                }
            }).catch(error => {
                console.error("Error controlling light:", error);
            });
        }

        function fetchStatus(selected) {
            fetch(`/api/status_5607?selected=${selected}`)
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
