import { PieChart, Pie, Cell, Legend, ResponsiveContainer, Tooltip } from 'recharts'
import { riskColors } from '../../utils/riskUtils'

export default function RiskDistributionChart({ distribution }) {
  const data = [
    { name: 'CRITICAL', value: distribution.CRITICAL || 0, color: riskColors.CRITICAL },
    { name: 'HIGH', value: distribution.HIGH || 0, color: riskColors.HIGH },
    { name: 'MEDIUM', value: distribution.MEDIUM || 0, color: riskColors.MEDIUM },
    { name: 'LOW', value: distribution.LOW || 0, color: riskColors.LOW },
  ].filter(item => item.value > 0)

  return (
    <div className="card p-6">
      <h3 className="font-semibold text-text mb-4">Risk Distribution</h3>
      {data.length > 0 ? (
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={100}
              paddingAngle={2}
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#111118',
                border: '1px solid #1E1E2E',
                borderRadius: '8px',
                color: '#F1F0FF'
              }}
            />
          </PieChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-center text-muted py-8">No risk data available</p>
      )}
    </div>
  )
}
