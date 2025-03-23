// API endpointser API endpoint
const dataApiUrl = "https://flood-prediction-api.onrender.com/api/raw";
const predApiUrl = "https://flood-prediction-api.onrender.com/api/prediction";

// Risk level mappingate dashboard
const RISK_LEVELS = {ata() {
    0: { text: "Low Risk (Below 50%)", class: "risk-low" },
    1: { text: "Medium Risk (75% - 90%)", class: "risk-medium" },
    2: { text: "High Risk (Above 90%)", class: "risk-high" }
};      console.log("RAW DATA: ", data)

// Fetch data with error handlingd data
async function fetchData() {yId("soil-moisture").textContent = `Soil Moisture: ${data.soil_moisture}m`;
    try {ocument.getElementById("rain").textContent = `Rain: ${data.rain}mm`;
        showLoader(true);ntById("temperature").textContent = `Temp: ${data.temperature}°C`;
        const response = await fetch(dataApiUrl);ontent = `Humidity: ${data.relative_humidity}%`;
        tch (error) {
        if (!response.ok) {r fetching data:", error);
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log("RAW DATA: ", data);
        const response = await fetch(predApiUrl);
        // Update DOM with fetched datan();
        document.getElementById("soil-moisture").textContent = `${data.soil_moisture}m`;
        document.getElementById("rain").textContent = `${data.rain}mm`;
        document.getElementById("temperature").textContent = `${data.temperature}°C`;
        document.getElementById("humidity").textContent = `${data.relative_humidity}%`;
        ])
        hideErrorMessage();TION: ", data);
    } catch (error) {a.prediction_24;
        console.error("Error fetching data:", error);
        showErrorMessage("Failed to fetch sensor data. Please try again later.");
    } finally {t.getElementById("24hr-forecast").textContent = `Forecast: ${prediction_level_map.get(pred_24)}`;
        showLoader(false);tById("48hr-forecast").textContent = `Forecast: ${prediction_level_map.get(pred_48)}`;
    }   chartData.datasets.data = [data.level_24, data.level_48];
}   } catch (error) {
        console.error("Error fetching data:", error)
async function fetchPrediction() {
    try {
        showLoader(true);
        const response = await fetch(predApiUrl);
        artData = {
        if (!response.ok) {, 'day3', 'day4', 'day5', 'day6', 'day7', 'day8', 'day9', 'day10'],
            throw new Error(`HTTP error! Status: ${response.status}`);
        }abel: 'Flood Forecast',
        data: [50, 19, 23, 34, 10, 34, 12, 56, 23, 40],
        const data = await response.json();2, 0.2)', 'rgba(153, 102, 255, 0.2)'],
        console.log("PREDICTION: ", data);1)', 'rgba(153, 102, 255, 1)'],
        borderWidth: 1,
        const pred24 = data.prediction_24;
        const pred48 = data.prediction_48;
        
        // Update forecast text with appropriate risk class
        updateForecast("24hr-forecast", pred24);
        updateForecast("48hr-forecast", pred48);
        ons: {
        // Update chart data if Chart.js is initialized
        if (window.forecastChart) {
            updateChartData(data);
        }   }
        }
        hideErrorMessage();
    } catch (error) {
        console.error("Error fetching prediction:", error);
        showErrorMessage("Failed to fetch prediction data. Please try again later.");
    } finally {
        showLoader(false);
    }Data();
}etchPrediction();
new Chart(ctx, chartConfig);
// Update forecast with appropriate stylingfunction updateForecast(elementId, riskLevel) {    const element = document.getElementById(elementId);    if (!element) return;        // Remove existing classes    element.classList.remove("risk-low", "risk-medium", "risk-high");        // Add new class and text    if (RISK_LEVELS[riskLevel]) {        element.textContent = RISK_LEVELS[riskLevel].text;        element.classList.add(RISK_LEVELS[riskLevel].class);    } else {        element.textContent = "Unknown Risk Level";    }}// Chart configurationconst chartData = {    labels: ['Day 1', 'Day 2'],    datasets: [{        label: 'Flood Risk Level',        data: [0, 0],        backgroundColor: [            'rgba(75, 192, 192, 0.5)',            'rgba(153, 102, 255, 0.5)'        ],        borderColor: [            'rgba(75, 192, 192, 1)',            'rgba(153, 102, 255, 1)'        ],        borderWidth: 2,        tension: 0.3    }]};const chartConfig = {    type: 'bar',    data: chartData,    options: {        responsive: true,        plugins: {            legend: {                position: 'top',            },            tooltip: {                callbacks: {                    label: function(context) {                        const value = context.raw;                        let riskText = 'Unknown';                                                if (value === 0) riskText = 'Low Risk';                        else if (value === 1) riskText = 'Medium Risk';                        else if (value === 2) riskText = 'High Risk';                                                return `Risk Level: ${riskText} (${value})`;                    }                }            }        },        scales: {            y: {                beginAtZero: true,                max: 2,                ticks: {                    stepSize: 1,                    callback: function(value) {                        if (value === 0) return 'Low';                        if (value === 1) return 'Medium';                        if (value === 2) return 'High';                        return '';                    }                }            }        }    }};// Update chart datafunction updateChartData(data) {    if (!window.forecastChart) return;        window.forecastChart.data.datasets[0].data = [data.prediction_24, data.prediction_48];    window.forecastChart.update();}// Show/hide loaderfunction showLoader(show) {    const loader = document.getElementById('loader');    if (loader) {        loader.style.display = show ? 'block' : 'none';    }}// Show error messagefunction showErrorMessage(message) {    const errorEl = document.getElementById('error-message');    if (errorEl) {        errorEl.textContent = message;        errorEl.style.display = 'block';    }}// Hide error messagefunction hideErrorMessage() {    const errorEl = document.getElementById('error-message');    if (errorEl) {        errorEl.style.display = 'none';    }}// Toggle dark modefunction toggleDarkMode() {    document.body.classList.toggle('dark-mode');    const isDarkMode = document.body.classList.contains('dark-mode');    localStorage.setItem('darkMode', isDarkMode);        // Update chart colors if needed    if (window.forecastChart) {        if (isDarkMode) {            window.forecastChart.options.scales.y.grid.color = 'rgba(255, 255, 255, 0.1)';            window.forecastChart.options.scales.x.grid.color = 'rgba(255, 255, 255, 0.1)';        } else {            window.forecastChart.options.scales.y.grid.color = 'rgba(0, 0, 0, 0.1)';            window.forecastChart.options.scales.x.grid.color = 'rgba(0, 0, 0, 0.1)';        }        window.forecastChart.update();    }}// Initialize the applicationfunction initApp() {    // Check for saved dark mode preference    const savedDarkMode = localStorage.getItem('darkMode') === 'true';    if (savedDarkMode) {        document.body.classList.add('dark-mode');    }        // Initialize chart if the element exists    const ctx = document.getElementById('forecast-chart');    if (ctx) {        window.forecastChart = new Chart(ctx, chartConfig);    }        // Add event listener for dark mode toggle    const modeToggle = document.getElementById('mode-toggle');    if (modeToggle) {        modeToggle.addEventListener('click', toggleDarkMode);    }        // Fetch initial data    fetchData();    fetchPrediction();        // Set up refresh interval (every 5 minutes)    setInterval(() => {        fetchData();        fetchPrediction();    }, 5 * 60 * 1000);}// Initialize the app when DOM is loadeddocument.addEventListener('DOMContentLoaded', initApp);