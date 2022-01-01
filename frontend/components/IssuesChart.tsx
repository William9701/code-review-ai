'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const data = [
  { name: 'Mon', critical: 4, high: 8, medium: 12, low: 6 },
  { name: 'Tue', critical: 3, high: 10, medium: 15, low: 8 },
  { name: 'Wed', critical: 5, high: 12, medium: 10, low: 9 },
  { name: 'Thu', critical: 2, high: 9, medium: 14, low: 7 },
  { name: 'Fri', critical: 6, high: 11, medium: 13, low: 10 },
  { name: 'Sat', critical: 1, high: 4, medium: 6, low: 3 },
  { name: 'Sun', critical: 2, high: 5, medium: 8, low: 4 },
]

export default function IssuesChart() {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Issues Found This Week</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="name" stroke="#6b7280" />
          <YAxis stroke="#6b7280" />
          <Tooltip
            contentStyle={{
              backgroundColor: '#fff',
              border: '1px solid #e5e7eb',
              borderRadius: '6px'
            }}
          />
          <Legend />
          <Bar dataKey="critical" fill="#ef4444" name="Critical" />
          <Bar dataKey="high" fill="#f59e0b" name="High" />
          <Bar dataKey="medium" fill="#eab308" name="Medium" />
          <Bar dataKey="low" fill="#3b82f6" name="Low" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
