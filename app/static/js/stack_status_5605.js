document.addEventListener("DOMContentLoaded", function() {
    var statusGrid = document.getElementById("status-grid");
    var contextMenu = document.getElementById("context-menu");

    if (statusGrid && contextMenu) {
        var selectedSquare = null;

        var statusOptions = [
            "Tire FG", "Tire Subs", "Pump FG", "Pump Subs", 
            "Omni FG", "Omni Subs", "Sidewash FG", "Arches", "Top Clean", 
            "Wraps", "Subassembly", "Brushes-Weights", "RW03", "RW04", 
            "Wash Tank 1", "CTBPYTH", "Fastems (H1,H2,H3)", "Manual MS", 
            "AW001-AW002", "AW003-AW004", "AW005-AW006", "AW007-AW008", 
            "AW009-AW010", "AW011-AW012", "AW013-AW014", "AW015-AW016", "TIG"
        ];

        function createStatusSquares() {
            statusGrid.innerHTML = "";

            statusOptions.forEach(function(option) {
                var square = document.createElement("div");
                square.className = "status-square";
                square.id = option.replace(/ /g, "-");
                square.textContent = option;

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
            fetch('/api/continuous_status_5605')
                .then(response => response.json())
                .then(data => {
                    console.log(data); // Add this line to inspect the received data
                    if (data && data.status) {
                        statusOptions.forEach(function(option) {
                            if (data.status[option]) {
                                updateSquare(option, data.status[option]);
                            }
                        });
                        updateSummaryCounts(data.status); // Update summary counts
                    } else {
                        console.error("Failed to get continuous status data");
                    }
                })
                .catch(error => console.error("Error fetching continuous status:", error));
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

        statusOptions.forEach(option => {
            const coilStatus = status[option];
            if (coilStatus) {
                if (coilStatus.green) greenCount++;
                if (coilStatus.yellow) yellowCount++;
                if (coilStatus.red) redCount++;
                if (coilStatus.blue) blueCount++;
                if (coilStatus.white) whiteCount++;
            }
        });

        document.getElementById('green-count').textContent = greenCount;
        document.getElementById('yellow-count').textContent = yellowCount;
        document.getElementById('red-count').textContent = redCount;
        document.getElementById('blue-count').textContent = blueCount;
        document.getElementById('white-count').textContent = whiteCount;
    }

    function sendControlRequest(address, state, selected) {
        fetch('/api/control_5605', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ address: address, state: state, selected: selected })
        }).then(response => response.json()).then(data => {
            if (data.success) {
                fetchContinuousStatus();
            } else {
                console.error("Failed to control light");
            }
        }).catch(error => {
            console.error("Error controlling light:", error);
        });
    }
});
