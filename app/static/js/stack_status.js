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

        setInterval(fetchContinuousStatus, 15000);
        fetchContinuousStatus(); // Initial fetch to populate data immediately
    }

    function sendControlRequest(address, state, selected) {
        fetch('/control', {
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
