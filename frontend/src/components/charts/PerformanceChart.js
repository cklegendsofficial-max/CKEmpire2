import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

const PerformanceChart = ({ data }) => {
  // Generate sample performance data
  const chartData = [
    { time: '00:00', queryTime: 120, cacheHitRate: 85, slowQueries: 2 },
    { time: '04:00', queryTime: 95, cacheHitRate: 88, slowQueries: 1 },
    { time: '08:00', queryTime: 150, cacheHitRate: 82, slowQueries: 3 },
    { time: '12:00', queryTime: 180, cacheHitRate: 78, slowQueries: 5 },
    { time: '16:00', queryTime: 140, cacheHitRate: 85, slowQueries: 2 },
    { time: '20:00', queryTime: 110, cacheHitRate: 90, slowQueries: 1 },
    { time: '24:00', queryTime: data?.queryTime || 100, cacheHitRate: data?.cacheHitRate || 87, slowQueries: data?.slowQueries || 1 },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-dark-800 border border-dark-600 rounded-lg p-3 shadow-lg">
          <p className="text-dark-300 text-sm">{`Time: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-white font-semibold" style={{ color: entry.color }}>
              {`${entry.name}: ${entry.value}${entry.name === 'cacheHitRate' ? '%' : entry.name === 'queryTime' ? 'ms' : ''}`}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
          <XAxis 
            dataKey="time" 
            stroke="#94a3b8"
            fontSize={12}
            tickLine={false}
            axisLine={false}
          />
          <YAxis 
            stroke="#94a3b8"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            yAxisId="left"
          />
          <YAxis 
            stroke="#94a3b8"
            fontSize={12}
            tickLine={false}
            axisLine={false}
            yAxisId="right"
            orientation="right"
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="queryTime"
            stroke="#10b981"
            strokeWidth={2}
            dot={{ fill: '#10b981', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#10b981', strokeWidth: 2, fill: '#10b981' }}
            name="Query Time (ms)"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="cacheHitRate"
            stroke="#6366f1"
            strokeWidth={2}
            dot={{ fill: '#6366f1', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#6366f1', strokeWidth: 2, fill: '#6366f1' }}
            name="Cache Hit Rate (%)"
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="slowQueries"
            stroke="#f59e0b"
            strokeWidth={2}
            dot={{ fill: '#f59e0b', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#f59e0b', strokeWidth: 2, fill: '#f59e0b' }}
            name="Slow Queries"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PerformanceChart; 