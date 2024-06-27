document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM fully loaded and parsed");

    // Handle filter button clicks
    const filterButtons = document.querySelectorAll('.filter-button');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            const range = this.getAttribute('data-range');
            fetchDetailedData(range);
        });
    });

    // Function to fetch detailed data
    function fetchDetailedData(range) {
        fetch(`/api/detailed_data?range=${range}`)
            .then(response => response.json())
            .then(data => {
                renderDetailedTable(data.details);
            })
            .catch(error => console.error('Fetch error:', error));
    }

    // Function to render detailed table
    function renderDetailedTable(details) {
        const detailedDataElement = document.getElementById('detailed-data');
        detailedDataElement.innerHTML = details.map(detail => `
            <tr>
                <td>${detail.time}</td>
                <td>${detail.opened}</td>
                <td>${detail.closed}</td>
            </tr>
        `).join('');
        $('#detailed-table').DataTable(); // Initialize DataTables on detailed table
    }

    // Initialize detailed table DataTable
    $('#detailed-table').DataTable();
    
    // Fetch detailed data for "today" range by default
    fetchDetailedData('today');



});
