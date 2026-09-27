const apiBase = '';

function hideAllSections() {
    document.querySelector('.weather-card').style.display = 'none';
    document.querySelector('.ai-card').style.display = 'none';
    document.getElementById('planButton').style.display = 'none';
    document.getElementById('advice').style.display = 'none';
    document.getElementById('forecastContent').style.display = 'none';
}

function showHome() {
    hideAllSections();
    document.querySelector('.weather-card').style.display = 'block';
    document.getElementById('planButton').style.display = 'block';
    document.getElementById('advice').style.display = 'block';
}

async function loadWeatherData(city) {
    const response = await fetch(`${apiBase}/weather/extended?city=${encodeURIComponent(city)}`);
    const data = await response.json();

    if (!response.ok || data.error) {
        throw new Error(data.error || 'Unable to load weather data');
    }

    document.getElementById('city').textContent = data.city || city;
    document.getElementById('temperature').textContent = data.temperature_c ?? '--';
    document.getElementById('humidity').textContent = `${data.humidity ?? '--'}%`;
    document.getElementById('wind').textContent = `${data.wind_speed_m_s ?? '--'} m/s`;
    document.getElementById('pressure').textContent = data.pressure ?? '--';
    document.getElementById('condition').textContent = data.condition || 'Weather data available';

    let prediction = '☀️ Pleasant Weather';
    let rainChance = 20;
    const temp = Number(data.temperature_c);
    const humidity = Number(data.humidity);

    if (temp >= 35 && humidity >= 70) {
        prediction = '🔥 Very Hot & Humid';
        rainChance = 30;
    } else if (temp >= 32) {
        prediction = '☀️ Hot and Humid';
        rainChance = 25;
    } else if (temp <= 25) {
        prediction = '🌥️ Cool Weather';
        rainChance = 40;
    }

    document.getElementById('prediction').textContent = prediction;
    document.getElementById('rainChance').textContent = `${rainChance}%`;

    let advice = '🌤️ Weather looks comfortable. It is a good time for normal outdoor activities.';
    if (temp >= 35) {
        advice = '🌡️ Very hot weather. Avoid outdoor activities during the afternoon and stay hydrated.';
    } else if (humidity >= 75) {
        advice = '💧 Humidity is high. Drink plenty of water and take breaks outdoors.';
    } else if ((data.condition || '').toLowerCase().includes('rain')) {
        advice = '🌧️ Rain may occur. Carry an umbrella and prefer indoor activities.';
    }

    document.querySelector('#advice p').textContent = advice;
    return data;
}

async function checkWeather() {
    const city = document.getElementById('cityInput').value.trim();

    if (!city) {
        alert('Please enter a city.');
        return;
    }

    try {
        await loadWeatherData(city);
    } catch (error) {
        alert(error.message || 'Cannot connect to the server.');
        console.error(error);
    }
}

async function planDay() {
    const city = document.getElementById('cityInput').value.trim();
    if (!city) {
        alert('Please enter a city first.');
        return;
    }

    try {
        const data = await loadWeatherData(city);
        let plan = '';

        if (data.temperature_c >= 35) {
            plan = `
                <p>☀️ Very hot weather. Avoid outdoor activities during the afternoon.</p>
                <p>💧 Drink plenty of water.</p>
                <p>🌅 Prefer outdoor activities in the morning or evening.</p>
            `;
        } else if (data.humidity >= 75) {
            plan = `
                <p>💧 High humidity. Stay hydrated.</p>
                <p>🌳 Prefer shaded outdoor activities.</p>
                <p>🕒 Take breaks if you stay outside for long.</p>
            `;
        } else if ((data.condition || '').toLowerCase().includes('rain')) {
            plan = `
                <p>🌧️ Rain is expected. Carry an umbrella.</p>
                <p>🏠 Prefer indoor activities.</p>
                <p>🚗 Be careful while travelling.</p>
            `;
        } else {
            plan = `
                <p>🌤️ Weather is comfortable for outdoor activities.</p>
                <p>🚶 Good time for walking or a light outing.</p>
                <p>💧 Keep yourself hydrated.</p>
            `;
        }

        document.getElementById('advice').innerHTML = `
            <h2>⭐ ${data.city} Day Plan</h2>
            ${plan}
        `;
    } catch (error) {
        alert(error.message || 'Cannot connect to the Flask server.');
        console.error(error);
    }
}

async function showForecast() {
    hideAllSections();
    const forecastBox = document.getElementById('forecastContent');
    forecastBox.style.display = 'block';

    const city = document.getElementById('cityInput').value.trim();
    if (!city) {
        forecastBox.innerHTML = '<p>Please enter a city first.</p>';
        return;
    }

    forecastBox.innerHTML = '<p>Loading forecast...</p>';

    try {
        const response = await fetch(`${apiBase}/api/forecast?city=${encodeURIComponent(city)}`);
        const data = await response.json();

        if (!response.ok || data.error) {
            forecastBox.innerHTML = `<p>Error: ${data.error || 'Unable to get forecast'}</p>`;
            return;
        }

        let html = `
            <h2>🌤️ 5-Day Forecast</h2>
            <p>📍 ${data.city}, ${data.country}</p>
        `;

        data.forecast.forEach((day, index) => {
            const forecastDate = new Date(day.date);
            let dayName = 'Day';

            if (index === 0) dayName = 'Today';
            else if (index === 1) dayName = 'Tomorrow';
            else dayName = forecastDate.toLocaleDateString('en-US', { weekday: 'long' });

            html += `
                <div class="forecast-day">
                    <h3>${dayName}</h3>
                    <p>🌤️ ${day.condition}</p>
                    <p>🌡️ Temperature: ${day.temperature_c}°C</p>
                    <p>💧 Humidity: ${day.humidity}%</p>
                    <p>💨 Wind: ${day.wind_speed_m_s} m/s</p>
                    <p>🌧️ Rain Chance: ${day.rain_chance}%</p>
                </div>
            `;
        });

        forecastBox.innerHTML = html;
    } catch (error) {
        console.error(error);
        forecastBox.innerHTML = '<p>Cannot connect to Flask server.</p>';
    }
}

async function showAI() {
    hideAllSections();
    document.querySelector('.ai-card').style.display = 'block';

    const city = document.getElementById('cityInput').value.trim();
    if (!city) {
        return;
    }

    try {
        await loadWeatherData(city);
    } catch (error) {
        console.log('AI connection error:', error);
    }
}

async function showPlan() {
    hideAllSections();
    document.getElementById('planButton').style.display = 'block';
    document.getElementById('advice').style.display = 'block';

    const city = document.getElementById('cityInput').value.trim();
    if (!city) {
        document.getElementById('advice').innerHTML = '<h2>💡 Smart Advice</h2><p>Please enter a city first.</p>';
        return;
    }

    try {
        await planDay();
    } catch (error) {
        console.error(error);
    }
}

document.getElementById('searchBtn').addEventListener('click', checkWeather);
document.getElementById('planButton').addEventListener('click', planDay);
document.getElementById('cityInput').addEventListener('keydown', (event) => {
    if (event.key === 'Enter') checkWeather();
});

document.querySelectorAll('.nav-item').forEach((item) => {
    item.addEventListener('click', () => {
        const target = item.dataset.target;
        if (target === 'home') showHome();
        if (target === 'forecast') showForecast();
        if (target === 'ai') showAI();
        if (target === 'plan') showPlan();
    });
});

showHome();