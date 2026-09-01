from pathlib import Path

path = Path("frontend/index.html")
text = path.read_text()

replacements = [
    (
        "Low is 0–&lt;10, moderate 10–&lt;30, high 30–&lt;70 and very high 70–100. These are activity bands—not economic, damage or treatment thresholds. See the <a href=\"/manual\">grower manual</a> for model details.",
        "Low is 0–&lt;10, moderate 10–&lt;30, high 30–&lt;70 and very high 70–100. These are activity bands—not economic, damage or treatment thresholds. For the simplified grower display, these are grouped as <strong>Low</strong> (0–&lt;10), <strong>Medium</strong> (10–&lt;30) and <strong>High</strong> (30–100). See the <a href=\"/manual\">grower manual</a> for model details."
    ),
    (
        "<div class=\"metrics\"><div class=\"metric\"><span>Regional activity today</span><strong id=\"pressure\">—</strong><small id=\"pressureValue\"></small></div><div class=\"metric\"><span>Recent direction</span><strong id=\"direction\">—</strong><small id=\"directionValue\"></small></div><div class=\"metric\"><span>7- and 14-day regional forecast</span><strong id=\"outlook\">—</strong><small id=\"outlookValue\"></small></div><div class=\"metric\"><span>Most common stage today</span><strong id=\"stage\">—</strong><small id=\"stageDate\"></small></div></div><div class=\"forecast-meta\">Live weather available through",
        "<div class=\"metrics\"><div class=\"metric\"><span id=\"activityCardLabel\">Regional activity today</span><strong id=\"pressure\">—</strong><small id=\"pressureValue\"></small></div><div class=\"metric\"><span>Recent direction</span><strong id=\"direction\">—</strong><small id=\"directionValue\"></small></div><div class=\"metric\"><span id=\"forecastCardLabel\">7- and 14-day regional forecast</span><strong id=\"outlook\">—</strong><small id=\"outlookValue\"></small></div><div class=\"metric\"><span>Most common stage today</span><strong id=\"stage\">—</strong><small id=\"stageDate\"></small></div></div><div class=\"forecast-meta\"><strong>Activity level:</strong> Low, Medium and High describe relative modelled population activity. They are not treatment thresholds. <span id=\"activityModeNote\"></span></div><div class=\"forecast-meta\">Live weather available through"
    ),
    (
        "el('outlookHeading').textContent=orchard?'Your orchard-adjusted monitoring outlook':'Your regional monitoring outlook';el('orchardTrajectory').classList.toggle('active',orchard);",
        "el('outlookHeading').textContent=orchard?'Your orchard activity outlook':'Your regional monitoring outlook';el('activityCardLabel').textContent=orchard?'Local activity today':'Regional activity today';el('forecastCardLabel').textContent=orchard?'7- and 14-day local forecast':'7- and 14-day regional forecast';el('activityModeNote').textContent=orchard?'In orchard mode, the activity level uses local weather at the orchard coordinates; the separate sampling outlook is anchored by the field observation.':'In regional mode, the activity level uses the selected representative regional weather point.';el('orchardTrajectory').classList.toggle('active',orchard);"
    ),
    (
        "function mobile(r){return r.n1+r.n2+r.n3+r.n4+r.n5+r.adult_females+r.adult_males}function pressureLabel(v){return v<10?'Low':v<30?'Moderate':v<70?'High':'Very high'}function displayDate(value)",
        "function mobile(r){return r.n1+r.n2+r.n3+r.n4+r.n5+r.adult_females+r.adult_males}function pressureLabel(v){return v<10?'Low':v<30?'Moderate':v<70?'High':'Very high'}function growerActivityLabel(v){return v<10?'Low':v<30?'Medium':'High'}function displayDate(value)"
    ),
    (
        "function directionLabel(delta){return delta>2?'Increasing':delta< -2?'Decreasing':'Stable'}",
        "function directionLabel(delta){return delta>2?'Increasing':delta< -2?'Declining':'Stable'}"
    ),
    (
        "const activity=pressureLabel(current),activityClass=activity.toLowerCase().replace(' ','-'),alert=el('activityAlert');alert.className=`activity-alert activity-${activityClass}`;alert.innerHTML=`${activity.toUpperCase()} REGIONAL ACTIVITY — ${directionLabel(delta14).toUpperCase()}<small>${current.toFixed(1)}/100 today; ${median[day14].toFixed(1)}/100 in ${day14-currentIndex} days. Regional context—not an orchard count or treatment recommendation.</small>`;el('pressure').textContent=activity;",
        "const activity=growerActivityLabel(current),activityClass=activity==='Low'?'low':activity==='Medium'?'moderate':'high',alert=el('activityAlert'),activityContext=forecastMode==='orchard'?'LOCAL':'REGIONAL',activityBoundary=forecastMode==='orchard'?'Local-weather population activity; field observations are shown separately below. Not a treatment recommendation.':'Regional population activity; not an orchard count or treatment recommendation.';alert.className=`activity-alert activity-${activityClass}`;alert.innerHTML=`${activity.toUpperCase()} ${activityContext} ACTIVITY — ${directionLabel(delta14).toUpperCase()}<small>${current.toFixed(1)}/100 today; ${median[day14].toFixed(1)}/100 in ${day14-currentIndex} days. ${activityBoundary}</small>`;el('pressure').textContent=activity;"
    ),
    (
        "el('outlook').innerHTML=`<span class=\"outlook-line\">In ${day7-currentIndex} days: ${median[day7].toFixed(1)}/100</span><span class=\"outlook-line\">In ${day14-currentIndex} days: ${median[day14].toFixed(1)}/100</span>`;",
        "el('outlook').innerHTML=`<span class=\"outlook-line\">In ${day7-currentIndex} days: <strong>${growerActivityLabel(median[day7]).toUpperCase()}</strong> · ${median[day7].toFixed(1)}/100</span><span class=\"outlook-line\">In ${day14-currentIndex} days: <strong>${growerActivityLabel(median[day14]).toUpperCase()}</strong> · ${median[day14].toFixed(1)}/100</span>`;"
    ),
    (
        "The modelled nymph-and-adult activity index is <strong>${current.toFixed(1)}/100 (${pressureLabel(current).toLowerCase()})</strong>",
        "The modelled nymph-and-adult activity index is <strong>${current.toFixed(1)}/100 (${growerActivityLabel(current).toLowerCase()})</strong>"
    ),
]

for old, new in replacements:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"Expected exactly one match, found {count}: {old[:120]!r}")
    text = text.replace(old, new)

path.write_text(text)
print("Applied grower-facing Low/Medium/High activity display without changing model thresholds or biology.")
