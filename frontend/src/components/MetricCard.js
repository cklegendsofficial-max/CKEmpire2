import React from 'react';

const MetricCard = ({ title, value, change, changeType, icon, color = 'empire' }) => {
  const colorClasses = {
    empire: {
      bg: 'bg-empire-900/20',
      border: 'border-empire-700/30',
      icon: 'text-empire-400',
      change: 'text-empire-400',
    },
    royal: {
      bg: 'bg-royal-900/20',
      border: 'border-royal-700/30',
      icon: 'text-royal-400',
      change: 'text-royal-400',
    },
    gold: {
      bg: 'bg-gold-900/20',
      border: 'border-gold-700/30',
      icon: 'text-gold-400',
      change: 'text-gold-400',
    },
    green: {
      bg: 'bg-green-900/20',
      border: 'border-green-700/30',
      icon: 'text-green-400',
      change: 'text-green-400',
    },
  };

  const colors = colorClasses[color] || colorClasses.empire;

  return (
    <div className={`metric-card ${colors.bg} ${colors.border}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center">
          <div className={`p-2 rounded-lg bg-dark-800/50 ${colors.icon}`}>
            {icon}
          </div>
          <div className="ml-4">
            <p className="text-sm font-medium text-dark-300">{title}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
          </div>
        </div>
        <div className="text-right">
          <div className={`flex items-center text-sm font-medium ${colors.change}`}>
            {changeType === 'positive' ? (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
              </svg>
            ) : (
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
              </svg>
            )}
            {change}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricCard; 