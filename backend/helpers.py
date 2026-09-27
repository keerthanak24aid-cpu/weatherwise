def c_to_f(celsius: float) -> float:
    return celsius * 9.0 / 5.0 + 32.0


def heat_index(celsius: float, humidity: float) -> float:
    # Use heat index only when warm; convert to F, apply NOAA formula, convert back
    t_f = c_to_f(celsius)
    rh = humidity
    if t_f < 80 or rh < 40:
        return celsius
    # NOAA heat index formula (simplified regression)
    hi_f = (
        -42.379
        + 2.04901523 * t_f
        + 10.14333127 * rh
        - 0.22475541 * t_f * rh
        - 0.00683783 * t_f * t_f
        - 0.05481717 * rh * rh
        + 0.00122874 * t_f * t_f * rh
        + 0.00085282 * t_f * rh * rh
        - 0.00000199 * t_f * t_f * rh * rh
    )
    return (hi_f - 32.0) * 5.0 / 9.0


def wind_chill(celsius: float, wind_m_s: float) -> float:
    # Wind chill formula expects wind in km/h
    v_kmh = wind_m_s * 3.6
    t = celsius
    if t > 10 or v_kmh <= 4.8:
        return celsius
    wc = 13.12 + 0.6215 * t - 11.37 * (v_kmh ** 0.16) + 0.3965 * t * (v_kmh ** 0.16)
    return wc


def comfort_index(celsius: float, humidity: float) -> float:
    # Simple comfort score 0-100 (higher is more comfortable)
    temp_score = max(0, 100 - abs(celsius - 21) * 4)
    hum_score = max(0, 100 - abs(humidity - 50) * 1.2)
    score = (temp_score * 0.6) + (hum_score * 0.4)
    return max(0.0, min(100.0, round(score, 1)))


def advice(condition: str, temp_c: float, humidity: float, wind_m_s: float) -> list:
    cond = condition.lower()
    tips = []
    if any(k in cond for k in ("rain", "shower", "drizzle", "thunder")):
        tips.append("Carry an umbrella or wear a raincoat")
    if any(k in cond for k in ("snow", "sleet")):
        tips.append("Dress warmly and watch for slippery surfaces")
    if temp_c >= 30:
        tips.append("Stay hydrated and avoid prolonged sun exposure")
    if temp_c <= 0:
        tips.append("Protect against freezing temperatures")
    if humidity >= 80:
        tips.append("Expect muggy conditions")
    if wind_m_s >= 10:
        tips.append("Secure loose outdoor items; it will be windy")
    if not tips:
        tips.append("No special precautions — pleasant for most activities")
    return tips
