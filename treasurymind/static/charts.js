// TreasuryMind Charts (Chart.js)
Chart.defaults.color = '#8b949e';
Chart.defaults.borderColor = 'rgba(255,255,255,0.04)';
Chart.defaults.font.family = 'Inter';

// Reconciliation Trends
const trendCtx = document.getElementById('trendChart');
if (trendCtx) {
    new Chart(trendCtx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Matched',
                data: [180, 195, 210, 185, 220, 160, 190],
                borderColor: '#06d6a0',
                backgroundColor: 'rgba(6,214,160,0.08)',
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 0,
            }, {
                label: 'Unmatched',
                data: [30, 25, 45, 35, 50, 20, 28],
                borderColor: '#f85149',
                backgroundColor: 'rgba(248,81,73,0.05)',
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: true, position: 'top', labels: { boxWidth: 12, padding: 20 } } },
            scales: { y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' } },
                      x: { grid: { display: false } } }
        }
    });
}

// Currency Distribution
const currCtx = document.getElementById('currencyChart');
if (currCtx) {
    new Chart(currCtx, {
        type: 'doughnut',
        data: {
            labels: ['USD', 'EUR', 'MYR', 'GBP', 'SGD', 'Other'],
            datasets: [{
                data: [42, 24, 14, 9, 6, 5],
                backgroundColor: ['#06d6a0', '#58a6ff', '#a855f7', '#f85149', '#d29922', '#8b949e'],
                borderWidth: 0,
            }]
        },
        options: {
            responsive: true,
            cutout: '65%',
            plugins: { legend: { position: 'bottom', labels: { boxWidth: 10, padding: 15 } } }
        }
    });
}

// FX Exposure
const fxCtx = document.getElementById('fxChart');
if (fxCtx) {
    new Chart(fxCtx, {
        type: 'bar',
        data: {
            labels: ['USD', 'EUR', 'MYR', 'GBP', 'SGD', 'JPY'],
            datasets: [{
                data: [6000, 4500, 3000, 1500, 1200, 800],
                backgroundColor: ['#06d6a0', '#06d6a0', '#06d6a0', '#58a6ff', '#58a6ff', '#58a6ff'],
                borderRadius: 4,
                barThickness: 40,
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.04)' },
                     ticks: { callback: v => v/1000 + 'k' } },
                x: { grid: { display: false } }
            }
        }
    });
}
