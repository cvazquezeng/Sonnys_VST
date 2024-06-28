// app/static/js/home_status.js
document.addEventListener("DOMContentLoaded", function() {
    var statusGrid = document.getElementById("status-grid");
    var contextMenu = document.getElementById("context-menu");

    if (statusGrid && contextMenu) {
        var selectedSquare = null;

        // Combine status options for 5605 and 5607
        var statusOptions5605 = [
            "Tire FG", "Tire Subs", "Pump FG", "Pump Subs", 
            "Omni FG", "Omni Subs", "Sidewash FG", "Arches", "Top Clean", 
            "Wraps", "Subassembly", "Brushes-Weights", "RW03", "RW04", 
            "Wash Tank 1", "CTBPYTH", "Fastems (H1,H2,H3)", "Manual MS", 
            "AW001-AW002", "AW003-AW004", "AW005-AW006", "AW007-AW008", 
            "AW009-AW010", "AW011-AW012", "AW013-AW014", "AW015-AW016", "TIG"
        ];
        
        var statusOptions5607 = [
            "RW01", "RW02", "RW08", "RW05", "RW06E", 
            "RW06W", "BLOWER", "Cloth", "ConvAssy", "Final", 
            "Rollers", "Stargate", "SP-A", "SP-B", "SP-C", 
            "Paint-Oven", "Wash Tank 2", "Exit Weld Booth", 
            "Entrance Weld Booth", "SW001-SW002", "SW003-SW004", 
            "SW005-SW006", "SW007"
        ];

        var statusOptions = statusOptions5605.concat(statusOptions5607);

        function createStatusSquares() {


            // Remove existing squares
            var squares = document.querySelectorAll(".status-square");
            squares.forEach(square => square.remove());

            // Create new squares
            statusOptions.forEach(function(option) {
                var square = document.createElement("div");
                square.className = "status-square";
                square.id = option.replace(/ /g, "-");
                square.textContent = option;

                // Set data-type attribute to differentiate between 5605 and 5607
                if (statusOptions5605.includes(option)) {
                    square.setAttribute('data-type', '5605');
                } else {
                    square.setAttribute('data-type', '5607');
                }

                var showContextMenu = function(event) {
                    event.preventDefault();
                    selectedSquare = event.target.textContent;
                    contextMenu.style.top = `${event.pageY}px`;
                    contextMenu.style.left = `${event.pageX}px`;
                    setTimeout(() => {
                        contextMenu.style.display = "block";
                    }, 100);
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

                if (color === "off") {
                    sendControlRequest(Array.from({ length: 5 }, (_, i) => address + i), false, selectedSquare);
                } else {
                    switch (color) {
                        case "red":
                            sendControlRequest([address + 4], state, selectedSquare);
                            break;
                        case "yellow":
                            sendControlRequest([address + 3], state, selectedSquare);
                            break;
                        case "blue":
                            sendControlRequest([address + 2], state, selectedSquare);
                            break;
                        case "white":
                            sendControlRequest([address + 1], state, selectedSquare);
                            break;
                        case "green":
                            sendControlRequest([address + 0], state, selectedSquare);
                            break;
                    }
                }

                contextMenu.style.display = "none";
            });
        });

        function updateSquare(option, status) {
            var square = document.getElementById(option.replace(/ /g, "-"));
            if (square) {
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
            } else {
                console.error(`Square element not found for option: ${option}`);
            }
        }

        function fetchContinuousStatus() {
            Promise.all([
                fetch('/api/continuous_status_5605').then(response => response.json()),
                fetch('/api/continuous_status_5607').then(response => response.json())
            ]).then(([data5605, data5607]) => {
                if (data5605 && data5605.status) {
                    statusOptions5605.forEach(option => {
                        if (data5605.status[option]) {
                            updateSquare(option, data5605.status[option]);
                        }
                    });
                } else {
                    console.error("Failed to get continuous status data for 5605");
                }
        
                if (data5607 && data5607.status) {
                    statusOptions5607.forEach(option => {
                        if (data5607.status[option]) {
                            updateSquare(option, data5607.status[option]);
                        }
                    });
                } else {
                    console.error("Failed to get continuous status data for 5607");
                }
        
                // Combine statuses and update summary counts
                const combinedStatus = { ...data5605.status, ...data5607.status };
                updateSummaryCounts(combinedStatus);
            }).catch(error => console.error("Error fetching continuous status:", error));
        }
        
        setInterval(fetchContinuousStatus, 30000);
        fetchContinuousStatus();
        
    }

    function updateSummaryCounts(status) {
        let greenCount = 0;
        let yellowCount = 0;
        let redCount = 0;
        let blueCount = 0;
        let whiteCount = 0;
    
        // Iterate over the status options, excluding legend squares
        statusOptions.forEach(option => {
            const coilStatus = status[option];
            if (coilStatus) {
                if (coilStatus.green) {
                    greenCount++;
                }
                if (coilStatus.yellow) {
                    yellowCount++;
                }
                if (coilStatus.red) {
                    redCount++;
                }
                if (coilStatus.blue) {
                    blueCount++;
                }
                if (coilStatus.white) {
                    whiteCount++;
                }
            }
        });
    
        document.getElementById('green-count').textContent = greenCount;
        document.getElementById('yellow-count').textContent = yellowCount;
        document.getElementById('red-count').textContent = redCount;
        document.getElementById('blue-count').textContent = blueCount;
        document.getElementById('white-count').textContent = whiteCount;
    }
    
    
    function sendControlRequest(addresses, state, selected) {
        var requests = addresses.map(address => {
            // Determine the correct endpoint based on the selected square's data-type attribute
            var selectedSquare = document.getElementById(selected.replace(/ /g, "-"));
            var endpoint = selectedSquare.getAttribute('data-type') === '5605' ? '/api/control_5605' : '/api/control_5607';
            
            return fetch(endpoint, {
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
                fetchContinuousStatus();
            }
        }).catch(error => {
            console.error("Error controlling light:", error);
        });
    }
});
