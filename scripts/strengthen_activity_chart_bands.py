from pathlib import Path

p = Path('frontend/index.html')
s = p.read_text()
old = "const activityBandBackground={id:'activityBandBackground',beforeDraw(chart,_,opts){if(!opts||!opts.enabled||!chart.scales.y)return;const{ctx,chartArea:{left,right},scales:{y}}=chart,zones=[{from:0,to:10,fill:'rgba(40,122,75,.11)'},{from:10,to:30,fill:'rgba(167,119,8,.11)'},{from:30,to:100,fill:'rgba(197,90,17,.08)'}];ctx.save();for(const zone of zones){const top=y.getPixelForValue(zone.to),bottom=y.getPixelForValue(zone.from);ctx.fillStyle=zone.fill;ctx.fillRect(left,top,right-left,bottom-top)}ctx.restore()}}"
new = "const activityBandBackground={id:'activityBandBackground',beforeDraw(chart,_,opts){if(!opts||!opts.enabled||!chart.scales.y)return;const{ctx,chartArea:{left,right},scales:{y}}=chart,zones=[{from:0,to:10,fill:'rgba(40,122,75,.24)',stroke:'rgba(40,122,75,.55)',label:'LOW'},{from:10,to:30,fill:'rgba(214,160,35,.22)',stroke:'rgba(167,119,8,.55)',label:'MEDIUM'},{from:30,to:100,fill:'rgba(224,113,54,.16)',stroke:'rgba(197,90,17,.45)',label:'HIGH'}];ctx.save();for(const zone of zones){const top=y.getPixelForValue(zone.to),bottom=y.getPixelForValue(zone.from);ctx.fillStyle=zone.fill;ctx.fillRect(left,top,right-left,bottom-top);ctx.strokeStyle=zone.stroke;ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(left,top);ctx.lineTo(right,top);ctx.stroke();ctx.fillStyle=zone.stroke;ctx.font='700 11px Arial,sans-serif';ctx.textAlign='right';ctx.textBaseline='top';ctx.fillText(zone.label,right-8,top+5)}ctx.restore()}}"
if old not in s:
    raise SystemExit('activity band plugin anchor not found')
s = s.replace(old, new, 1)
p.write_text(s)
