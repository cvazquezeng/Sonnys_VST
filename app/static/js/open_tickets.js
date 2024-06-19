document.addEventListener("DOMContentLoaded", function() {
    const statusGrid = document.getElementById('status-grid');

    function fetchDataAndUpdate() {
        fetch('https://andon.sageclarity.com/AndonCenter/sites/71/events?filters=%7B%7D&sort=%7B%22date%22:1%7D')
            .then(response => response.json())
            .then(data => {
                const events = data.data || [];
                statusGrid.innerHTML = ''; // Clear existing squares

                events.forEach(event => {
                    const square = document.createElement('div');
                    square.classList.add('status-square');

                    const properties = event.properties.reduce((acc, prop) => {
                        acc[prop.name] = prop.value;
                        return acc;
                    }, {});

                    const elapsedTime = calculateElapsedTime(event.ts_epoch);

                    // Determine background color based on Andon Status
                    let statusColor;
                    switch (properties["Andon Status"]) {
                        case 'Acknowledged':
                            statusColor = 'green';
                            break;
                        case 'Request Made':
                            statusColor = 'yellow';
                            break;
                        case 'Work Stoppage':
                            statusColor = 'red';
                            break;
                        default:
                            statusColor = '#4CAF50'; // Default color
                    }

                    square.innerHTML = `
                        <div class="ticket-header" style="background-color: ${event.ui.colour || '#4CAF50'};">
                            <h3>${properties["Line/Machine"] || 'Unknown'}</h3>
                            <div class="status-sticker" style="background-color: ${statusColor};">
                                ${properties["Andon Status"] || 'Unknown'}
                            </div>
                        </div>
                        <div class="ticket-body">
                            <p><strong>ID:</strong> ${event.id}</p>
                            <p><strong>Issue Type:</strong> ${properties["Issue Type"] || 'Unknown'}</p>
                            <p><strong>Comment:</strong> ${properties["Comment"] || 'None'}</p>
                            <p><strong>Notification Groups:</strong> ${properties["Notification Groups"] || 'Unknown'}</p>
                        </div>
                        <div class="time-elapsed-container" style="background-color: ${event.ui.colour || '#4CAF50'};">
                            <p class="time-elapsed" data-timestamp="${event.ts_epoch}">
                                <strong>Time Elapsed:</strong> <span>${elapsedTime}</span>
                            </p>
                        </div>
                    `;
                    statusGrid.appendChild(square);
                });
            })
            .catch(error => console.error('Error fetching data:', error));
    }

    function calculateElapsedTime(timestamp) {
        const now = Date.now();
        const elapsed = now - timestamp;
        const hours = Math.floor(elapsed / (1000 * 60 * 60));
        const minutes = Math.floor((elapsed % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((elapsed % (1000 * 60)) / 1000);
        return `${hours}h ${minutes}m ${seconds}s`;
    }

    function updateElapsedTimes() {
        const timeElements = document.querySelectorAll('.time-elapsed span');
        timeElements.forEach(element => {
            const timestamp = element.closest('.time-elapsed').getAttribute('data-timestamp');
            element.textContent = calculateElapsedTime(parseInt(timestamp));
        });
    }

    // Fetch data and update every 20 seconds
    setInterval(fetchDataAndUpdate, 20000);
    // Update elapsed time every second
    setInterval(updateElapsedTimes, 1000);

    // Initial fetch and update
    fetchDataAndUpdate();
});
