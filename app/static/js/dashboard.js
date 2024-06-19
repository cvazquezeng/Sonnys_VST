function initializeChart(labels, data) {
    var ctx = document.getElementById('responseTimeChart').getContext('2d');
    var chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Average Response Time',
                data: data,
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Response Time (seconds)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Category'
                    }
                }
            }
        }
    });
}
