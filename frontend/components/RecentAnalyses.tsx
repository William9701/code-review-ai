'use client'

import { Clock, GitPullRequest, AlertCircle } from 'lucide-react'

const recentAnalyses = [
  {
    id: 1,
    repo: 'frontend/auth-service',
    pr: '#234',
    issues: 12,
    critical: 3,
    time: '5 min ago',
    status: 'completed'
  },
  {
    id: 2,
    repo: 'backend/api-gateway',
    pr: '#235',
    issues: 8,
    critical: 1,
    time: '12 min ago',
    status: 'completed'
  },
  {
    id: 3,
    repo: 'frontend/dashboard',
    pr: '#236',
    issues: 15,
    critical: 5,
    time: '25 min ago',
    status: 'completed'
  },
  {
    id: 4,
    repo: 'backend/payment-service',
    pr: '#237',
    issues: 6,
    critical: 0,
    time: '1 hour ago',
    status: 'completed'
  },
]

export default function RecentAnalyses() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">Recent Analyses</h3>
      </div>
      <div className="divide-y divide-gray-200">
        {recentAnalyses.map((analysis) => (
          <div key={analysis.id} className="p-6 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-2">
                  <GitPullRequest className="w-5 h-5 text-indigo-600" />
                  <h4 className="font-medium text-gray-900">{analysis.repo}</h4>
                  <span className="text-sm text-gray-500">{analysis.pr}</span>
                </div>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1">
                    <AlertCircle className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-600">{analysis.issues} issues</span>
                  </div>
                  {analysis.critical > 0 && (
                    <span className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                      {analysis.critical} critical
                    </span>
                  )}
                  <div className="flex items-center space-x-1 text-gray-500">
                    <Clock className="w-4 h-4" />
                    <span>{analysis.time}</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                  Completed
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
