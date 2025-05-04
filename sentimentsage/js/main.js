document.addEventListener('DOMContentLoaded', function() {
    fetch('trend_summary.json')
        .then(response => response.json())
        .then(data => {
            const summaryDiv = document.getElementById('trend-summary') || document.getElementById('dashboard-trend-summary');
            if (summaryDiv) {
                let html = '';
                for (const [source, stats] of Object.entries(data)) {
                    html += `<h3>${source.charAt(0).toUpperCase() + source.slice(1)}</h3>`;
                    html += `<ul>`;
                    html += `<li>Average Sentiment: ${stats.average.toFixed(3)}</li>`;
                    html += `<li>Std Dev: ${stats.stddev.toFixed(3)}</li>`;
                    html += `<li>Count: ${stats.count}</li>`;
                    html += `</ul>`;
                }
                summaryDiv.innerHTML = html;
            }
        });
    fetch('report.md')
        .then(response => response.text())
        .then(data => {
            const reportDiv = document.getElementById('report-content') || document.getElementById('dashboard-report-content');
            if (reportDiv) {
                reportDiv.textContent = data;
            }
        });
});