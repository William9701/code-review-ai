'use client'

import { useState } from 'react'
import { Code, Upload, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { analyzeCode } from '@/lib/api'
import Link from 'next/link'

export default function AnalyzePage() {
  const [filename, setFilename] = useState('')
  const [code, setCode] = useState('')
  const [language, setLanguage] = useState('python')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setResult(null)

    try {
      const analysis = await analyzeCode(filename || 'code.py', code, language)
      setResult(analysis)
    } catch (err: any) {
      setError(err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const loadExample = () => {
    setLanguage('python')
    setFilename('auth.py')
    setCode(`import hashlib

def authenticate_user(username, password):
    # Hardcoded credentials - BAD!
    admin_password = "admin123"

    # Weak crypto - BAD!
    password_hash = hashlib.md5(password.encode()).hexdigest()

    # SQL injection vulnerability - BAD!
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)

    return True`)
  }

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
                <p className="text-sm text-gray-500">Analyze Your Code</p>
              </div>
            </div>
            <Link href="/" className="text-indigo-600 hover:text-indigo-700 font-medium">
              ← Back to Dashboard
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Code Input */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">Submit Code for Review</h2>
              <button
                onClick={loadExample}
                className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
              >
                Load Example
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Filename
                </label>
                <input
                  type="text"
                  value={filename}
                  onChange={(e) => setFilename(e.target.value)}
                  placeholder="e.g., auth.py"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Language
                </label>
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                >
                  <option value="python">Python</option>
                  <option value="typescript">TypeScript</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Code
                </label>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="Paste your code here..."
                  rows={16}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent font-mono text-sm"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={loading || !code}
                className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <>
                    <Loader className="w-5 h-5 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Upload className="w-5 h-5" />
                    <span>Analyze Code</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Results */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h2 className="text-xl font-bold text-gray-900 mb-6">Analysis Results</h2>

            {!result && !error && !loading && (
              <div className="text-center py-12">
                <Code className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">Submit code to see analysis results</p>
              </div>
            )}

            {loading && (
              <div className="text-center py-12">
                <Loader className="w-16 h-16 text-indigo-600 mx-auto mb-4 animate-spin" />
                <p className="text-gray-600 font-medium">Analyzing your code...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-medium text-red-900">Analysis Failed</h3>
                  <p className="text-sm text-red-700 mt-1">{error}</p>
                </div>
              </div>
            )}

            {result && (
              <div className="space-y-6">
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start space-x-3">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h3 className="font-medium text-green-900">Analysis Complete!</h3>
                    <p className="text-sm text-green-700 mt-1">
                      Analysis ID: #{result.analysis_id}
                    </p>
                  </div>
                </div>

                {/* Stats Grid */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <p className="text-sm text-gray-600 mb-1">Total Issues</p>
                    <p className="text-3xl font-bold text-gray-900">{result.total_issues}</p>
                  </div>
                  <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                    <p className="text-sm text-red-600 mb-1">Critical</p>
                    <p className="text-3xl font-bold text-red-700">{result.critical_issues}</p>
                  </div>
                  <div className="bg-orange-50 rounded-lg p-4 border border-orange-200">
                    <p className="text-sm text-orange-600 mb-1">High</p>
                    <p className="text-3xl font-bold text-orange-700">{result.high_issues}</p>
                  </div>
                  <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200">
                    <p className="text-sm text-yellow-600 mb-1">Medium</p>
                    <p className="text-3xl font-bold text-yellow-700">{result.medium_issues}</p>
                  </div>
                </div>

                {/* Status */}
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Status:</span>
                    <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full font-medium">
                      {result.status}
                    </span>
                  </div>
                </div>

                {/* View Details Link */}
                <Link
                  href={`/analysis/${result.analysis_id}`}
                  className="block w-full text-center bg-indigo-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-indigo-700"
                >
                  View Detailed Results →
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
