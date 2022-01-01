'use client'

import { useState, useEffect } from 'react'
import { Activity, AlertTriangle, CheckCircle, Code, GitPullRequest, Shield, Upload } from 'lucide-react'
import Link from 'next/link'
import StatsCard from '@/components/StatsCard'
import IssuesChart from '@/components/IssuesChart'
import RecentAnalyses from '@/components/RecentAnalyses'
import { getStats } from '@/lib/api'

export default function Dashboard() {
  const [stats, setStats] = useState({
    totalAnalyses: 0,
    criticalIssues: 0,
    prReviewed: 0,
    avgResponseTime: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await getStats()
        setStats({
          totalAnalyses: data.total_analyses,
          criticalIssues: data.critical_issues,
          prReviewed: data.prs_reviewed,
          avgResponseTime: data.avg_analysis_time
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        // Keep defaults on error
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
    const interval = setInterval(fetchStats, 30000)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-indigo-600 rounded-lg p-2">
                <Code className="w-8 h-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">CodeReview AI</h1>
                <p className="text-sm text-gray-500">Automated Code Review Dashboard</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/analyze"
                className="flex items-center space-x-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 font-medium"
              >
                <Upload className="w-5 h-5" />
                <span>Analyze Code</span>
              </Link>
              <div className="flex items-center space-x-2 bg-green-50 px-3 py-1 rounded-full">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm font-medium text-green-700">All Systems Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Analyses"
            value={stats.totalAnalyses}
            icon={<Activity className="w-6 h-6" />}
            trend="+12% from last week"
            trendUp={true}
            color="blue"
          />
          <StatsCard
            title="Critical Issues"
            value={stats.criticalIssues}
            icon={<AlertTriangle className="w-6 h-6" />}
            trend="-5% from last week"
            trendUp={false}
            color="red"
          />
          <StatsCard
            title="PRs Reviewed"
            value={stats.prReviewed}
            icon={<GitPullRequest className="w-6 h-6" />}
            trend="+8% from last week"
            trendUp={true}
            color="green"
          />
          <StatsCard
            title="Avg Response Time"
            value={`${stats.avgResponseTime}s`}
            icon={<CheckCircle className="w-6 h-6" />}
            trend="-0.3s faster"
            trendUp={true}
            color="purple"
          />
        </div>

        {/* Charts and Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2">
            <IssuesChart />
          </div>
          <div>
            <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Security Summary</h3>
                <Shield className="w-5 h-5 text-indigo-600" />
              </div>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">SQL Injection</span>
                    <span className="text-sm font-semibold text-red-600">12</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-red-600 h-2 rounded-full" style={{ width: '60%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Hardcoded Secrets</span>
                    <span className="text-sm font-semibold text-orange-600">8</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-orange-600 h-2 rounded-full" style={{ width: '40%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">XSS Vulnerabilities</span>
                    <span className="text-sm font-semibold text-yellow-600">15</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-yellow-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-sm text-gray-600">Weak Crypto</span>
                    <span className="text-sm font-semibold text-blue-600">6</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full" style={{ width: '30%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Analyses */}
        <RecentAnalyses />
      </main>
    </div>
  )
}
