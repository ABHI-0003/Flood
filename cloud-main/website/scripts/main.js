// API endpoints
const dataApiUrl = "http://98.70.76.114/api/raw";
const predApiUrl = "http://98.70.76.114/api/prediction";

// Risk level mapping
const RISK_LEVELS = {
    0: { text: "Low Risk (Below 50%)", class: "risk-low" },
    1: { text: "Medium Risk (75% - 90%)", class: "risk-medium" },
    2: { text: "High Risk (Above 90%)", class: "risk-high" }
};

// Fetch data with error handling
async function fetchData() {
    try {
        showLoader(true);
        const response = await fetch(dataApiUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("RAW DATA: ", data);

        // Update DOM with fetched data
        document.getElementById("soil-moisture").textContent = `${data.soil_moisture}m`;
        document.getElementById("rain").textContent = `${data.rain}mm`;
        document.getElementById("temperature").textContent = `${data.temperature}°C`;
        document.getElementById("humidity").textContent = `${data.relative_humidity}%`;
        
        hideErrorMessage();
    } catch (error) {
        console.error("Error fetching data:", error);
        showErrorMessage("Failed to fetch sensor data. Please try again later.");
    } finally {
        showLoader(false);
    }
}

async function fetchPrediction() {
    try {
        showLoader(true);
        const response = await fetch(predApiUrl);
        
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("PREDICTION: ", data);
        
        const pred24 = data.prediction_24;
        const pred48 = data.prediction_48;
        
        // Update forecast text with appropriate risk class
        updateForecast("24hr-forecast", pred24);
        updateForecast("48hr-forecast", pred48);
        
        // Update chart data if Chart.js is initialized
        if (window.forecastChart) {
            updateChartData(data);
        }
        
        hideErrorMessage();
    } catch (error) {
        console.error("Error fetching prediction:", error);
        showErrorMessage("Failed to fetch prediction data. Please try again later.");
    } finally {
        showLoader(false);
    }
}

// Update forecast with appropriate styling
function updateForecast(elementId, riskLevel) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    // Remove existing classes
    element.classList.remove("risk-low", "risk-medium", "risk-high");
    
    // Add new class and text
    if (RISK_LEVELS[riskLevel]) {
        element.textContent = RISK_LEVELS[riskLevel].text;
        element.classList.add(RISK_LEVELS[riskLevel].class);
    } else {
        element.textContent = "Unknown Risk Level";
    }
}

// Chart configuration
const chartData = {
    labels: ['Day 1', 'Day 2'],
    datasets: [{
        label: 'Flood Risk Level',
        data: [0, 0],
        backgroundColor: [
            'rgba(75, 192, 192, 0.5)',
            'rgba(153, 102, 255, 0.5)'
        ],
        borderColor: [
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
        ],
        borderWidth: 2,
        tension: 0.3
    }]
};

const chartConfig = {
    type: 'bar',
    data: chartData,
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        const value = context.raw;
                        let riskText = 'Unknown';
                        
                        if (value === 0) riskText = 'Low Risk';
                        else if (value === 1) riskText = 'Medium Risk';
                        else if (value === 2) riskText = 'High Risk';
                        
                        return `Risk Level: ${riskText} (${value})`;
                    }
                }
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 2,
                ticks: {
                    stepSize: 1,
                    callback: function(value) {
                        if (value === 0) return 'Low';
                        if (value === 1) return 'Medium';
                        if (value === 2) return 'High';
                        return '';
                    }
                }
            }
        }
    }
};

// Update chart data
function updateChartData(data) {
    if (!window.forecastChart) return;
    
    window.forecastChart.data.datasets[0].data = [data.prediction_24, data.prediction_48];
    window.forecastChart.update();
}

// Show/hide loader
function showLoader(show) {
    const loader = document.getElementById('loader');
    if (loader) {
        loader.style.display = show ? 'block' : 'none';
    }
}

// Show error message
function showErrorMessage(message) {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
}

// Hide error message
function hideErrorMessage() {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
        errorEl.style.display = 'none';
    }
}

// Toggle dark mode
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDarkMode = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDarkMode);
    
    // Update chart colors if needed
    if (window.forecastChart) {
        if (isDarkMode) {
            window.forecastChart.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';
            window.forecastChart.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';
        } else {
            window.forecastChart.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';
            window.forecastChart.options.scales.x.grid.color = 'rgba(0, 0, 0, 0.1)';
        }
        window.forecastChart.update();
    }
}

// Initialize the application
function initApp() {
    // Check for saved dark mode preference
    const savedDarkMode = localStorage.getItem('darkMode') === 'true';
    if (savedDarkMode) {
        document.body.classList.add('dark-mode');
    }
    
    // Initialize chart if the element exists
    const ctx = document.getElementById('forecast-chart');
    if (ctx) {
        window.forecastChart = new Chart(ctx, chartConfig);
    }
    
    // Add event listener for dark mode toggle
    const modeToggle = document.getElementById('mode-toggle');
    if (modeToggle) {
        modeToggle.addEventListener('click', toggleDarkMode);
    }
    
    // Fetch initial data
    fetchData();
    fetchPrediction();
    
    // Set up refresh interval (every 5 minutes)
    setInterval(() => {
        fetchData();
        fetchPrediction();
    }, 5 * 60 * 1000);
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);

async function fetchHistoricalData() {
    try {
        const response = await fetch("http://98.70.76.114/api/data/history?days=7");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        renderHistoricalChart(data.history);
    } catch (error) {
        console.error("Error fetching historical data:", error);
    }
}

function renderHistoricalChart(history) {
    const labels = history.map(entry => entry.timestamp);
    const rainData = history.map(entry => entry.rain);
    const tempData = history.map(entry => entry.temperature);

    const ctx = document.getElementById("historical-chart").getContext("2d");
    new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [
                {
                    label: "Rainfall (mm)",
                    data: rainData,
                    borderColor: "rgba(75, 192, 192, 1)",
                    backgroundColor: "rgba(75, 192, 192, 0.2)",
                    tension: 0.3,
                },
                {
                    label: "Temperature (°C)",
                    data: tempData,
                    borderColor: "rgba(255, 99, 132, 1)",
                    backgroundColor: "rgba(255, 99, 132, 0.2)",
                    tension: 0.3,
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "top",
                },
            },
            scales: {
                y: {
                    beginAtZero: true,
                },
            },
        },
    });
}

// Initialize the app when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    initApp();
    fetchHistoricalData();
});
