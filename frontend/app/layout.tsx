import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'CodeReview AI - Dashboard',
  description: 'AI-powered code review analytics and insights',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">{children}</body>
    </html>
  )
}
