
function canvasDraw(data) {
  if (!data) return;
  
  const dpr = window.devicePixelRatio || 1;

  console.log(data)
  const sunLongitudeDeg = data.surya_longitude_deg;
  const moonLongitudeDeg = data.chandra_longitude_deg;

  const ctx = calendarCanvas.getContext('2d');
  const rect = calendarCanvas.getBoundingClientRect();

  calendarCanvas.width = Math.round(rect.width * dpr);
  calendarCanvas.height = Math.round(rect.height * dpr);

  const cx = calendarCanvas.width / 2;
  const cy = calendarCanvas.height / 2;

  // Visual scale (purely illustrative)
  const sunRadius = 90;
  const moonRadius = 65;

  // Convert degrees to calendarCanvas angle
  // calendarCanvas: 0 rad = right, positive clockwise
  // Astronomy: 0° = Aries direction, counter-clockwise
  function toCanvasAngle(deg) {
    return (deg - 90) * Math.PI / 180;
  }

  function polarToXY(radius, angle) {
    return {
      x: cx + radius * Math.cos(angle),
      y: cy + radius * Math.sin(angle)
    };
  }

  // Clear
  ctx.clearRect(0, 0, calendarCanvas.width, calendarCanvas.height);

  // Draw reference circle (ecliptic)
  ctx.beginPath();
  ctx.arc(cx, cy, sunRadius, 0, Math.PI * 2);
  ctx.strokeStyle = '#e5e7eb';
  ctx.stroke();

    // Degree markers around the ecliptic
  const labelRadius = sunRadius + 18;
  const tickInner = sunRadius - 4;
  const tickOuter = sunRadius + 4;

  ctx.font = `${10 * dpr}px system-ui, sans-serif`;
  ctx.fillStyle = '#475569';
  ctx.strokeStyle = '#94a3b8';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';

  for (let deg = 0; deg < 360; deg += 10) {
    const angle = toCanvasAngle(deg);

    const inner = polarToXY(tickInner, angle);
    const outer = polarToXY(tickOuter, angle);

    // Tick mark
    ctx.beginPath();
    ctx.moveTo(inner.x, inner.y);
    ctx.lineTo(outer.x, outer.y);
    ctx.stroke();

    // Label every 30°
    if (deg % 30 === 0) {
      const labelPos = polarToXY(labelRadius, angle);
      ctx.fillText(`${deg}°`, labelPos.x, labelPos.y);
    }
  }

  // Earth
  ctx.beginPath();
  ctx.arc(cx, cy, 8, 0, Math.PI * 2);
  ctx.fillStyle = '#22c55e';
  ctx.fill();

  // Sun
  const sunAngle = toCanvasAngle(sunLongitudeDeg);
  const sunPos = polarToXY(sunRadius, sunAngle);

  ctx.beginPath();
  ctx.arc(sunPos.x, sunPos.y, 10, 0, Math.PI * 2);
  ctx.fillStyle = '#facc15';
  ctx.fill();

  // Moon
  const moonAngle = toCanvasAngle(moonLongitudeDeg);
  const moonPos = polarToXY(moonRadius, moonAngle);

  ctx.beginPath();
  ctx.arc(moonPos.x, moonPos.y, 6, 0, Math.PI * 2);
  ctx.fillStyle = '#9ca3af';
  ctx.fill();

  // Lines from Earth
  ctx.strokeStyle = '#111827';
  ctx.lineWidth = 1;

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(sunPos.x, sunPos.y);
  ctx.stroke();

  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(moonPos.x, moonPos.y);
  ctx.stroke();

  // Aries direction marker (0°)
  ctx.beginPath();
  ctx.moveTo(cx, cy);
  ctx.lineTo(cx + sunRadius, cy);
  ctx.setLineDash([4, 4]);
  ctx.strokeStyle = '#94a3b8';
  ctx.stroke();
  ctx.setLineDash([]);
}
