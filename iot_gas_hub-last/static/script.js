// 加载趋势图数据
function loadTrendGraph() {
    fetch('/api/trend')
        .then(response => response.json())
        .then(data => {
            const ctx = document.getElementById('trendChart').getContext('2d');
            new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.times, // 时间数据，按时间顺序显示
                    datasets: [{
                        label: 'Gas Levels',
                        data: data.gas_levels, // 气体浓度数据
                        borderColor: 'rgba(75, 192, 192, 1)',
                        fill: false,
                    }]
                },
                options: {
                    scales: {
                        x: { title: { display: true, text: 'Time' }},
                        y: { title: { display: true, text: 'Gas Levels' }}
                    }
                }
            });
        })
        .catch(error => console.error('Error fetching trend data:', error));
}


// 加载警报数据
function loadAlerts() {
    fetch('/api/alerts')
        .then(response => response.json())
        .then(data => {
            const alertsTableBody = document.getElementById('alertsTableBody');
            alertsTableBody.innerHTML = '';
            data.forEach(alert => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${alert.sensor_id}</td>
                    <td>${alert.time}</td>
                    <td>${alert.address}</td>
                    <td>${alert.gas_level}</td>
                `;
                alertsTableBody.appendChild(row);
            });
        });
}

// 加载仪表盘数据
function loadGauge() {
    fetch('/api/gas-level')
        .then(response => response.json())
        .then(data => {
            const gasValueElement = document.getElementById('gasValue');
            const statusTextElement = document.getElementById('statusText');
            
            gasValueElement.textContent = `Gas Level: ${data.gas_level}`;
            statusTextElement.textContent = `Status: ${data.status}`;

            const gaugeOptions = {
                angle: 0, 
                lineWidth: 0.2, 
                radiusScale: 1, 
                pointer: { length: 0.6, strokeWidth: 0.035, color: '#000000' },
                limitMax: false, 
                limitMin: false, 
                colorStart: '#6FADCF', 
                colorStop: '#8FC0DA', 
                strokeColor: '#E0E0E0', 
                generateGradient: true,
            };

            const gauge = new Gauge(document.getElementById('gaugeChart')).setOptions(gaugeOptions);
            gauge.maxValue = 100; 
            gauge.setMinValue(0);
            gauge.animationSpeed = 32;
            gauge.set(data.gas_level);
        });
}

// 加载Peak Gas Levels数据
function loadPeakGasLevels() {
    fetch('/api/peak-gas-levels')
        .then(response => response.json())
        .then(data => {
            document.getElementById('today').textContent = `Today's Peak: ${data.today}`;
            document.getElementById('month').textContent = `This Month's Peak: ${data.month}`;
            document.getElementById('history').textContent = `All-Time Peak: ${data.history}`;
        });
}

// 页面加载时调用所有函数
window.onload = function() {
    loadTrendGraph();
    loadAlerts();
    loadGauge();
    loadPeakGasLevels();
};
// 获取按钮并为每个按钮绑定点击事件
document.getElementById('dashboardBtn').addEventListener('click', function() {
    window.location.href = 'index.html'; // 跳转到dashboard页面
});

document.getElementById('notificationsBtn').addEventListener('click', function() {
    window.location.href = '/alerts'; // 跳转到 Flask 渲染的 alerts 页面
});


document.getElementById('dataBtn').addEventListener('click', function() {
    window.location.href = 'data.html'; // 跳转到data页面
});

document.getElementById('loginBtn').addEventListener('click', function() {
    window.location.href = 'login.html'; // 跳转到login页面
});
