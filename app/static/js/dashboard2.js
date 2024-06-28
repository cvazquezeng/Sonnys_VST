document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    const filterButtons = document.querySelectorAll('.filter-button');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const range = this.getAttribute('data-range');
            console.log(`Button clicked, range: ${range}`);
            fetchDetailedData(range);
        });
    });

    function fetchDetailedData(range) {
        console.log(`Fetching detailed data for range: ${range}`);
        fetch(`/api/detailed_data?range=${range}`)
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Fetched data:', data);
                if (data && data.details) {
                    renderDetailedTable(data.details);
                } else {
                    console.error('No details found in the fetched data.');
                }
                if (data && data.summary) {
                    console.log('Summary data found:', data.summary);
                    updateSummaryTable(data.summary);
                } else {
                    console.error('No summary found in the fetched data.');
                }
                if (data && data.range) {
                    document.getElementById('range-display').innerText = data.range;
                }
            })
            .catch(error => console.error('Fetch error:', error));
    }

    function renderDetailedTable(details) {
        console.log('Rendering detailed table with details:', details);
        const detailedDataElement = document.getElementById('detailed-data');
        detailedDataElement.innerHTML = details.map(detail => `
            <tr>
                <td>${detail.time}</td>
                <td>${detail.opened}</td>
                <td>${detail.closed}</td>
            </tr>
        `).join('');

        if ($.fn.DataTable.isDataTable('#detailed-table')) {
            $('#detailed-table').DataTable().destroy();
        }
        $('#detailed-table').DataTable();
    }

    function updateSummaryTable(summary) {
        console.log('Updating summary table with summary:', summary);
        document.querySelector('#summary-data').innerHTML = `
            <tr>
                <td>${summary.tickets_opened}</td>
                <td>${summary.tickets_closed}</td>
                <td>${summary.average_time_to_close}</td>
                <td>${summary.average_time_to_acknowledge}</td>
            </tr>
        `;
    }

    fetchDetailedData('today');
});
