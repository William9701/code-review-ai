import { TrendingUp, TrendingDown } from 'lucide-react'

interface StatsCardProps {
  title: string
  value: number | string
  icon: React.ReactNode
  trend: string
  trendUp: boolean
  color: 'blue' | 'red' | 'green' | 'purple'
}

const colorClasses = {
  blue: 'bg-blue-50 text-blue-600 border-blue-100',
  red: 'bg-red-50 text-red-600 border-red-100',
  green: 'bg-green-50 text-green-600 border-green-100',
  purple: 'bg-purple-50 text-purple-600 border-purple-100'
}

export default function StatsCard({ title, value, icon, trend, trendUp, color }: StatsCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
      <h3 className="text-sm font-medium text-gray-600 mb-1">{title}</h3>
      <div className="flex items-baseline justify-between">
        <p className="text-3xl font-bold text-gray-900">{value}</p>
        <div className={`flex items-center space-x-1 text-sm ${trendUp ? 'text-green-600' : 'text-gray-500'}`}>
          {trendUp ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
          <span>{trend}</span>
        </div>
      </div>
    </div>
  )
}
