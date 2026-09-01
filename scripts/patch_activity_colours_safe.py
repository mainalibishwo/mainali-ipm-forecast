from pathlib import Path

path = Path('frontend/index.html')
text = path.read_text()

# 1) Card/pill styles only. Do not touch selectors, location loading, or forecast controls.
css_marker = ".orchard-seasonal{margin:22px 0;padding:16px;background:#f8fbf9;border:1px solid #d7e5de;border-left:5px solid #4b87a8;border-radius:9px}.orchard-seasonal h2{margin-bottom:4px}.projection-key{display:flex;flex-wrap:wrap;gap:14px;margin:8px 0;color:var(--muted);font-size:12px}.projection-key span:before{content:'';display:inline-block;width:22px;border-top:3px solid #164d3f;margin-right:6px;vertical-align:middle}.projection-key .projected:before{border-top-style:dashed;border-color:#4b87a8}\n"
css_extra = ".metric.activity-low-card{background:#edf7f0;border-color:#a8cfb3;border-top:5px solid #287a4b}.metric.activity-medium-card{background:#fff8e9;border-color:#e3c98a;border-top:5px solid #a77708}.metric.activity-high-card{background:#fff1ec;border-color:#e3b19c;border-top:5px solid #c55a11}.activity-pill{display:inline-block;padding:2px 8px;border-radius:999px;font-weight:800;line-height:1.4;margin-left:4px}.activity-pill.low{background:#e2f2e7;color:#1f6840}.activity-pill.medium{background:#fff0c9;color:#845b00}.activity-pill.high{background:#fde3d8;color:#a64416}\n"
if ".metric.activity-low-card" not in text:
    if css_marker not in text:
        raise SystemExit('CSS marker not found')
    text = text.replace(css_marker, css_marker + css_extra, 1)

# 2) Add chart background band plugin and enable only on 0-100 activity charts.
old_chart_options = "function chartOptions(title){return{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},scales:{x:{ticks:{maxTicksLimit:12}},y:{beginAtZero:true,max:100,title:{display:true,text:title}}},plugins:{legend:{position:'bottom'}}}}"
new_chart_options = "function chartOptions(title){const useActivityBands=title.includes('Population activity')||title.includes('Common model scale')||title.includes('Within-region seasonal index');return{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},scales:{x:{ticks:{maxTicksLimit:12}},y:{beginAtZero:true,max:100,title:{display:true,text:title}}},plugins:{legend:{position:'bottom'},activityBandBackground:{enabled:useActivityBands}}}}"
if old_chart_options in text:
    text = text.replace(old_chart_options, new_chart_options, 1)
elif "activityBandBackground:{enabled:useActivityBands}" not in text:
    raise SystemExit('chartOptions marker not found')

old_plugin = "const forecastPeriodPlugin={id:'forecastPeriod',beforeDraw(chart,_,opts){if(!opts||opts.todayIndex<0)return;"
new_plugin = "const activityBandBackground={id:'activityBandBackground',beforeDraw(chart,_,opts){if(!opts||!opts.enabled||!chart.scales.y)return;const{ctx,chartArea:{left,right},scales:{y}}=chart,zones=[{from:0,to:10,fill:'rgba(40,122,75,.11)'},{from:10,to:30,fill:'rgba(167,119,8,.11)'},{from:30,to:100,fill:'rgba(197,90,17,.08)'}];ctx.save();for(const zone of zones){const top=y.getPixelForValue(zone.to),bottom=y.getPixelForValue(zone.from);ctx.fillStyle=zone.fill;ctx.fillRect(left,top,right-left,bottom-top)}ctx.restore()}},forecastPeriodPlugin={id:'forecastPeriod',beforeDraw(chart,_,opts){if(!opts||opts.todayIndex<0)return;"
if "const activityBandBackground=" not in text:
    if old_plugin not in text:
        raise SystemExit('forecast plugin marker not found')
    text = text.replace(old_plugin, new_plugin, 1)

text = text.replace("Chart.register(forecastPeriodPlugin,projectionBoundaryPlugin);", "Chart.register(activityBandBackground,forecastPeriodPlugin,projectionBoundaryPlugin);", 1)

# 3) Colour only the activity card and 7/14-day status pills.
pressure_old = "el('pressure').textContent=activity;el('pressureValue').textContent=`Index ${current.toFixed(1)}/100 · model range ${low[currentIndex].toFixed(1)}–${high[currentIndex].toFixed(1)}`;"
pressure_new = "el('pressure').textContent=activity;el('pressureValue').textContent=`Index ${current.toFixed(1)}/100 · model range ${low[currentIndex].toFixed(1)}–${high[currentIndex].toFixed(1)}`;const pressureCard=el('pressure').closest('.metric'),growerClass=activity.toLowerCase();pressureCard.classList.remove('activity-low-card','activity-medium-card','activity-high-card');pressureCard.classList.add(`activity-${growerClass}-card`);"
if pressure_old in text:
    text = text.replace(pressure_old, pressure_new, 1)
elif "pressureCard.classList.add" not in text:
    raise SystemExit('pressure card marker not found')

outlook_old = "el('outlook').innerHTML=`<span class=\"outlook-line\">In ${day7-currentIndex} days: <strong>${growerActivityLabel(median[day7]).toUpperCase()}</strong> · ${median[day7].toFixed(1)}/100</span><span class=\"outlook-line\">In ${day14-currentIndex} days: <strong>${growerActivityLabel(median[day14]).toUpperCase()}</strong> · ${median[day14].toFixed(1)}/100</span>`;"
outlook_new = "el('outlook').innerHTML=`<span class=\"outlook-line\">In ${day7-currentIndex} days: <span class=\"activity-pill ${growerActivityLabel(median[day7]).toLowerCase()}\">${growerActivityLabel(median[day7]).toUpperCase()}</span> · ${median[day7].toFixed(1)}/100</span><span class=\"outlook-line\">In ${day14-currentIndex} days: <span class=\"activity-pill ${growerActivityLabel(median[day14]).toLowerCase()}\">${growerActivityLabel(median[day14]).toUpperCase()}</span> · ${median[day14].toFixed(1)}/100</span>`;"
if outlook_old in text:
    text = text.replace(outlook_old, outlook_new, 1)
elif "activity-pill ${growerActivityLabel" not in text:
    raise SystemExit('outlook marker not found')

# 4) Add concise legend note for the main and regional-comparison activity plots.
main_old = "The dark line is the middle result across nine biological scenarios, and the green band shows their full range. Pale blue indicates future weather; the dashed line marks today."
main_new = "The dark line is the middle result across nine biological scenarios, and the green band shows their full range. Background zones show the grower activity guide: green = Low (0–&lt;10), amber = Medium (10–&lt;30), orange = High (30–100). Pale blue indicates future weather; the dashed line marks today."
text = text.replace(main_old, main_new, 1)

compare_old = "All locations use the same starting population and model scale. Compare relative timing and life-stage patterns; these are not bugs/ha or treatment thresholds."
compare_new = "All locations use the same starting population and model scale. Background zones use the same grower activity guide: green = Low, amber = Medium, orange = High. Compare relative timing and life-stage patterns; these are not bugs/ha or treatment thresholds."
text = text.replace(compare_old, compare_new, 1)

path.write_text(text)
print('Applied safe activity colours without modifying region/location controls.')
