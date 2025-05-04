// Simple chart rendering using Chart.js (assumes Chart.js is loaded via CDN or bundled)
document.addEventListener('DOMContentLoaded', function() {
    fetch('trend_summary.json')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('sentimentChart') || document.getElementById('dashboardSentimentChart');
            if (ctx) {
                const labels = Object.keys(data);
                const averages = labels.map(source => data[source].average);
                const stddevs = labels.map(source => data[source].stddev);
                new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels: labels,
                        datasets: [
                            {
                                label: 'Average Sentiment',
                                data: averages,
                                backgroundColor: 'rgba(54, 162, 235, 0.6)'
                            },
                            {
                                label: 'Std Dev',
                                data: stddevs,
                                backgroundColor: 'rgba(255, 206, 86, 0.4)'
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        plugins: {
                            legend: { position: 'top' },
                            title: { display: true, text: 'Sentiment Trends by Source' }
                        }
                    }
                });
            }
        });
});