document.addEventListener("DOMContentLoaded", function() {
    const filterButtons = document.querySelectorAll('.filter-button');

    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const range = this.getAttribute('data-range');
            // Update URL and reload to get the summary table data
            window.location.href = `/dashboard2?range=${range}`;
        });
    });

    // Function to fetch and display detailed data
    function fetchDetailedData(range) {
        fetch(`/api/detailed_data?range=${range}`)
            .then(response => response.json())
            .then(data => {
                updateDetailedTable(data);
            })
            .catch(error => console.error('Error fetching detailed data:', error));
    }

    // Function to update detailed table
    function updateDetailedTable(data) {
        const tbody = document.getElementById('detailed-data');
        const timeLabel = document.getElementById('time-label');
        tbody.innerHTML = '';

        if (['today', 'yesterday', '24hours'].includes(data.range)) {
            timeLabel.textContent = 'Shift';
            data.details.forEach(detail => {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${detail.time}</td><td>${detail.opened}</td><td>${detail.closed}</td>`;
                tbody.appendChild(row);
            });
        } else if (data.range === '7days') {
            timeLabel.textContent = 'Day';
            data.details.forEach(detail => {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${detail.time}</td><td>${detail.opened}</td><td>${detail.closed}</td>`;
                tbody.appendChild(row);
            });
        } else if (data.range === '30days') {
            timeLabel.textContent = 'Week';
            data.details.forEach(detail => {
                const row = document.createElement('tr');
                row.innerHTML = `<td>${detail.time}</td><td>${detail.opened}</td><td>${detail.closed}</td>`;
                tbody.appendChild(row);
            });
        }
    }

    // Get the current range from the URL and fetch detailed data if needed
    const urlParams = new URLSearchParams(window.location.search);
    const range = urlParams.get('range');
    if (range) {
        fetchDetailedData(range);
    }
});
