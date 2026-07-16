import { Link } from 'react-router-dom';

export type ChartDatum = { label: string; value: number; color: string; detail?: string; to?: string };
export type ActivityDatum = { label: string; value: number; detail?: string };

export function DonutChart({ data, centerValue, centerLabel, ariaLabel }: { data: ChartDatum[]; centerValue: string; centerLabel: string; ariaLabel: string }) {
  const total = Math.max(1, data.reduce((sum, item) => sum + item.value, 0));
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  let offset = 0;

  return <div className="dashboard-donut-layout">
    <div className="dashboard-donut" role="img" aria-label={ariaLabel}>
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <circle className="dashboard-donut-track" cx="50" cy="50" r={radius} />
        {data.filter((item) => item.value > 0).map((item) => {
          const length = item.value / total * circumference;
          const currentOffset = offset;
          offset += length;
          return <circle key={item.label} className="dashboard-donut-segment" cx="50" cy="50" r={radius} style={{ stroke: item.color }} strokeDasharray={`${Math.max(0, length - 2)} ${circumference}`} strokeDashoffset={-currentOffset} />;
        })}
      </svg>
      <span><strong>{centerValue}</strong><small>{centerLabel}</small></span>
    </div>
    <div className="dashboard-chart-legend">{data.map((item) => item.to ? <Link key={item.label} to={item.to}><i style={{ background: item.color }} /><span><strong>{item.label}</strong>{item.detail && <small>{item.detail}</small>}</span><b>{item.value}</b></Link> : <div key={item.label}><i style={{ background: item.color }} /><span><strong>{item.label}</strong>{item.detail && <small>{item.detail}</small>}</span><b>{item.value}</b></div>)}</div>
  </div>;
}

export function BarChart({ data, ariaLabel }: { data: ChartDatum[]; ariaLabel: string }) {
  const max = Math.max(1, ...data.map((item) => item.value));
  const column = (item: ChartDatum) => <><div><span style={{ height: `${Math.max(item.value ? 12 : 2, item.value / max * 100)}%`, background: item.color }}><b>{item.value}</b></span></div><small>{item.label}</small></>;
  return <div className="dashboard-bar-chart" role="group" aria-label={ariaLabel}>
    <div className="dashboard-bar-plot">{data.map((item) => item.to ? <Link key={item.label} to={item.to} className="dashboard-bar-column" aria-label={`${item.label}: ${item.value}`}>{column(item)}</Link> : <div key={item.label} className="dashboard-bar-column">{column(item)}</div>)}</div>
    <div className="dashboard-bar-axis"><span>0</span><span>{Math.ceil(max / 2)}</span><span>{max}</span></div>
  </div>;
}

export function ActivityChart({ data, ariaLabel }: { data: ActivityDatum[]; ariaLabel: string }) {
  const max = Math.max(1, ...data.map((item) => item.value));
  const width = 720;
  const height = 190;
  const paddingX = 22;
  const paddingY = 24;
  const step = data.length > 1 ? (width - paddingX * 2) / (data.length - 1) : 0;
  const points = data.map((item, index) => ({ ...item, x: paddingX + index * step, y: height - paddingY - item.value / max * (height - paddingY * 2) }));
  const polyline = points.map((point) => `${point.x},${point.y}`).join(' ');
  const area = `${paddingX},${height - paddingY} ${polyline} ${width - paddingX},${height - paddingY}`;

  return <div className="dashboard-activity-chart" role="img" aria-label={ariaLabel}>
    <svg viewBox={`0 0 ${width} ${height}`} aria-hidden="true" preserveAspectRatio="none">
      <defs><linearGradient id="activity-area" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="var(--teal)" stopOpacity=".28" /><stop offset="100%" stopColor="var(--teal)" stopOpacity=".02" /></linearGradient></defs>
      <line x1={paddingX} y1={paddingY} x2={width - paddingX} y2={paddingY} />
      <line x1={paddingX} y1={height / 2} x2={width - paddingX} y2={height / 2} />
      <line x1={paddingX} y1={height - paddingY} x2={width - paddingX} y2={height - paddingY} />
      <polygon className="dashboard-activity-area" points={area} />
      <polyline className="dashboard-activity-line" points={polyline} />
      {points.map((point) => <circle key={`${point.label}-${point.x}`} cx={point.x} cy={point.y} r="5"><title>{point.label}: {point.value}{point.detail ? ` · ${point.detail}` : ''}</title></circle>)}
    </svg>
    <div className="dashboard-activity-labels" style={{ gridTemplateColumns: `repeat(${data.length}, minmax(0, 1fr))` }}>{data.map((item) => <span key={item.label}><strong>{item.value}</strong><small>{item.label}</small></span>)}</div>
  </div>;
}
