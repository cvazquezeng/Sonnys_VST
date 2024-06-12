document.addEventListener("DOMContentLoaded", function() {
    var dropdownMenu = document.getElementById("dropdown-menu");
    var statusGrid = document.getElementById("status-grid");
    var contextMenu = document.getElementById("context-menu");
    var selectedSquare = null;

    var options = [
        "5605 Building", "Tire FG", "Tire Subs", "Pump FG", "Pump Subs", 
        "Omni FG", "Omni Subs", "Sidewash FG", "Arches", "Top Clean", 
        "Wraps", "Subassembly", "Brushes-Weights", "RW03", "RW04", 
        "Wash Tank 1", "CTBPYTH", "Fastems (H1,H2,H3)", "Manual MS", 
        "AW001-AW002", "AW003-AW004", "AW005-AW006", "AW007-AW008", 
        "AW009-AW010", "AW011-AW012", "AW013-AW014", "AW015-AW016", "TIG"
        
    ];

    var statusOptions = options.filter(option => option !== "5605 Building");

    // Populate dropdown menu
    options.forEach(function(option) {
        var el = document.createElement("option");
        el.textContent = option;
        el.value = option;
        dropdownMenu.appendChild(el);
    });

    // Function to create status squares
    function createStatusSquares() {
        // Clear the status grid first to avoid duplicates
        statusGrid.innerHTML = "";

        statusOptions.forEach(function(option) {
            var square = document.createElement("div");
            square.className = "status-square";
            square.id = option.replace(/ /g, "-");
            square.textContent = option;

            var showContextMenu = function(event) {
                event.preventDefault();
                selectedSquare = event.target.textContent; // Assuming the option is stored in the text content
                contextMenu.style.top = `${event.pageY}px`;
                contextMenu.style.left = `${event.pageX}px`;
                setTimeout(() => {
                    contextMenu.style.display = "block";
                }, 100); // 100 milliseconds delay
            };
            
            square.addEventListener("contextmenu", showContextMenu);
            
            square.addEventListener("click", function(event) {
                event.preventDefault();
                showContextMenu(event);
            });

            statusGrid.appendChild(square);
        });
    }

    createStatusSquares();

    document.addEventListener("click", function(event) {
        if (!contextMenu.contains(event.target)) {
            contextMenu.style.display = "none";
        }
    });

    contextMenu.querySelectorAll("ul li").forEach(function(item) {
        item.addEventListener("click", function() {
            var color = this.getAttribute("data-color");
            var state = color !== "off";
            var address = statusOptions.indexOf(selectedSquare) * 5;

            switch (color) {
                case "red":
                    sendControlRequest(address + 4, state, selectedSquare);
                    break;
                case "yellow":
                    sendControlRequest(address + 3, state, selectedSquare);
                    break;
                case "blue":
                    sendControlRequest(address + 2, state, selectedSquare);
                    break;
                case "white":
                    sendControlRequest(address + 1, state, selectedSquare);
                    break;
                case "green":
                    sendControlRequest(address + 0, state, selectedSquare);
                    break;
                case "off":
                    for (var i = 0; i < 5; i++) {
                        sendControlRequest(address + i, false, selectedSquare);
                    }
                    break;
            }

            contextMenu.style.display = "none"; // Hide the context menu after selection
        });
    });

    function updateOverlay(status) {
        document.getElementById('green-overlay').style.backgroundColor = status.green ? 'rgba(76, 175, 80, 0.7)' : 'transparent';
        document.getElementById('white-overlay').style.backgroundColor = status.white ? 'rgba(169, 169, 169, 0.7)' : 'transparent';
        document.getElementById('blue-overlay').style.backgroundColor = status.blue ? 'rgba(47, 0, 255, 0.7)' : 'transparent';
        document.getElementById('yellow-overlay').style.backgroundColor = status.yellow ? 'rgba(255, 238, 0, 0.7)' : 'transparent';
        document.getElementById('red-overlay').style.backgroundColor = status.red ? 'rgba(255, 0, 0, 0.7)' : 'transparent';
    }

    function fetchStatus(selected) {
        fetch(`/status?selected=${selected}`)
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

    function updateSquare(option, status) {
        var square = document.getElementById(option.replace(/ /g, "-"));
        var colors = [];
        if (status.green) colors.push('rgba(76, 175, 80, 0.7)');
        if (status.white) colors.push('rgba(169, 169, 169, 0.7)');
        if (status.blue) colors.push('rgba(47, 0, 255, 0.7)');
        if (status.yellow) colors.push('rgba(255, 238, 0, 0.7)');
        if (status.red) colors.push('rgba(255, 0, 0, 0.7)');

        if (colors.length > 1) {
            square.style.background = `linear-gradient(${colors.join(', ')})`;
            square.style.color = 'white';
        } else if (colors.length === 1) {
            square.style.backgroundColor = colors[0];
            square.style.color = (colors[0] === 'rgba(169, 169, 169, 0.7)') ? 'black' : 'white';
        } else {
            square.style.backgroundColor = 'gray';
            square.style.color = 'white';
        }
    }

    function fetchContinuousStatus() {
        fetch('/continuous_status')
            .then(response => response.json())
            .then(data => {
                if (data && data.status) {
                    statusOptions.forEach(function(option) {
                        if (data.status[option]) {
                            updateSquare(option, data.status[option]);
                        }
                    });
                } else {
                    console.error("Failed to get continuous status data");
                }
            })
            .catch(error => console.error("Error fetching continuous status:", error));
    }

    var intervalId, timeoutId;

    function resetTimers() {
        clearInterval(intervalId);
        clearTimeout(timeoutId);

        intervalId = setInterval(function() {
            var selected = dropdownMenu.value;
            fetchStatus(selected);
        }, 10000);

        timeoutId = setTimeout(function() {
            clearInterval(intervalId);
        }, 20000);
    }

    dropdownMenu.addEventListener("change", function() {
        var selected = dropdownMenu.value;
        fetchStatus(selected);
        resetTimers();
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
        document.getElementById(buttonId).addEventListener("click", function() {
            clearInterval(intervalId);
            var selected = dropdownMenu.value;
            var state = buttonId !== "off-button";

            if (selected === "5605 Building") {
                if (buttonId === "off-button") {
                    sendControlRequest(-1, false, selected);
                } else {
                    var addressRange = Array.from({ length: 171 }, (_, i) => i);
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
    });

    function sendControlRequest(address, state, selected) {
        fetch('/control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address: address, state: state, selected: selected })
        }).then(response => response.json()).then(data => {
            if (data.success) {
                setTimeout(function() {
                    fetchStatus(selected);
                    resetTimers();
                }, 500);
            } else {
                console.error("Failed to control light");
                resetTimers();
            }
        }).catch(error => {
            console.error("Error controlling light:", error);
            resetTimers();
        });
    }

    dropdownMenu.dispatchEvent(new Event('change'));
    fetchContinuousStatus();
    setInterval(fetchContinuousStatus, 15000);
});
