'use client'

import { useState, useMemo } from 'react'
import Link from 'next/link'
import { Github, Twitter, Download, Users, Building, MapPin, Globe, ExternalLink, Mail, ArrowUpDown, ArrowUp, ArrowDown, Search, Star, Settings, X, ChevronDown, User } from 'lucide-react'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

interface UserData {
  username: string
  display_name: string
  bio: string
  avatar_url: string
  profile_url: string
  platform: string
  type: string
  follower_count: number
  following_count: number
  company: string
  location: string
  website: string
  twitter: string
  email: string
  public_repos?: number
  scraped_at: string
}

interface ScrapeResult {
  success: boolean
  message: string
  platform: string
  total_extracted: number
  data: UserData[]
  download_url: string
  current_page: number
  has_next_page: boolean
  cache_id: string
  total_followers?: number
  total_pages?: number
}

type SortField = 'follower_count' | 'following_count' | 'public_repos' | 'scraped_at' | 'username'
type SortOrder = 'asc' | 'desc'

export default function Home() {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')
  const [maxUsers, setMaxUsers] = useState<number>(250)
  const [unlimitedMode, setUnlimitedMode] = useState<boolean>(false)
  const [showAdvancedSettings, setShowAdvancedSettings] = useState<boolean>(false)

  const [streamingData, setStreamingData] = useState<UserData[]>([])
  const [sortField, setSortField] = useState<SortField>('follower_count')
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc')
  const [totalFollowers, setTotalFollowers] = useState<number>(-1)
  const [totalPages, setTotalPages] = useState<number>(1)
  const [currentPage, setCurrentPage] = useState<number>(1)
  const [hasNextPage, setHasNextPage] = useState<boolean>(false)
  const [streamingStatus, setStreamingStatus] = useState<{
    isStreaming: boolean
    progress: number
    message: string
    stage?: number
    currentUser?: string
    processedCount?: number
    totalCount?: number
  }>({
    isStreaming: false,
    progress: 0,
    message: ''
  })
  
  const [abortController, setAbortController] = useState<AbortController | null>(null)

  const detectPlatform = (inputUrl: string) => {
    const url = inputUrl.toLowerCase()
    if (url.includes('github.com')) return 'GitHub'
    if (url.includes('twitter.com') || url.includes('x.com')) return 'Twitter/X'
    if (url.includes('producthunt.com')) return 'Product Hunt'
    if (url.includes('weibo.com')) return 'Weibo'
    if (url.includes('news.ycombinator.com')) return 'Hacker News'
    if (url.includes('youtube.com') || url.includes('youtu.be')) return 'YouTube'
    if (url.includes('reddit.com')) return 'Reddit'
    if (url.includes('medium.com')) return 'Medium'
    if (url.includes('bilibili.com')) return 'Bilibili'
    return null
  }

    const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!url.trim() || streamingStatus.isStreaming) return

    await handleStreamingScrape()
  }

  const handleStopScraping = () => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
      setStreamingStatus({
        isStreaming: false,
        progress: 0,
        message: 'Scraping stopped by user'
      })
    }
  }

  const handleStreamingScrape = async () => {
    if (!url.trim()) return

    setStreamingData([])
    setError('')
    setStreamingStatus({
      isStreaming: true,
      progress: 0,
      message: 'Connecting...'
    })

    const controller = new AbortController()
    setAbortController(controller)

    try {
      const response = await fetch('/api/scrape-stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          url: url.trim(),
          page: 1,
          max_users: unlimitedMode ? maxUsers : 0,
          unlimited: unlimitedMode
        }),
        signal: controller.signal
      })

      if (!response.ok) {
        throw new Error('Network request failed')
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('Unable to read response stream')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')

        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))

              switch (data.type) {
                case 'start':
                case 'platform':
                case 'progress':
                  setStreamingStatus(prev => ({
                    ...prev,
                    message: data.message,
                    progress: data.progress || prev.progress,
                    stage: data.stage,
                    currentUser: data.current_user,
                    processedCount: data.processed_count,
                    totalCount: data.total_count
                  }))
                  // Update pagination info if available
                  if (data.total_followers !== undefined) {
                    setTotalFollowers(data.total_followers)
                  }
                  if (data.total_pages !== undefined) {
                    setTotalPages(data.total_pages)
                  }
                  if (data.current_page !== undefined) {
                    setCurrentPage(data.current_page)
                  }
                  break

                case 'user_completed':
                  if (data.user_data) {
                    setStreamingData(prev => [...prev, data.user_data])
                  }
                  setStreamingStatus(prev => ({
                    ...prev,
                    message: data.message,
                    progress: data.progress || prev.progress,
                    currentUser: data.current_user,
                    processedCount: data.processed_count,
                    totalCount: data.total_count
                  }))
                  break

                case 'complete':
                  setStreamingData(data.data || [])
                  // Update pagination info from complete response
                  if (data.total_followers !== undefined) {
                    setTotalFollowers(data.total_followers)
                  }
                  if (data.total_pages !== undefined) {
                    setTotalPages(data.total_pages)
                  }
                  if (data.current_page !== undefined) {
                    setCurrentPage(data.current_page)
                  }
                  if (data.has_next_page !== undefined) {
                    setHasNextPage(data.has_next_page)
                  }
                  setStreamingStatus({
                    isStreaming: false,
                    progress: 100,
                    message: data.message
                  })
                  setAbortController(null)
                  break

                case 'error':
                  setError(data.message)
                  setStreamingStatus({
                    isStreaming: false,
                    progress: 0,
                    message: ''
                  })
                  setAbortController(null)
                  break
              }
            } catch (e) {
              console.error('Error parsing data:', e)
            }
          }
        }
      }
    } catch (err) {
      console.error('Streaming scrape error:', err)
      if (err instanceof Error && err.name === 'AbortError') {
        // Request was aborted, don't show error message
        return
      }
      setError('Network error, please try again later')
      setStreamingStatus({
        isStreaming: false,
        progress: 0,
        message: ''
      })
      setAbortController(null)
    }
  }



  const handleUserClick = (profileUrl: string) => {
    window.open(profileUrl, '_blank', 'noopener,noreferrer')
  }

  // CSV生成和下载函数
  const generateCSV = (data: UserData[]) => {
    const headers = [
      'username', 'display_name', 'bio', 'avatar_url', 'profile_url',
      'platform', 'type', 'follower_count', 'following_count',
      'company', 'location', 'website', 'twitter', 'email',
      'public_repos', 'scraped_at'
    ]

    const csvContent = [
      headers.join(','),
      ...data.map(user => headers.map(header => {
        const value = user[header as keyof UserData]
        // 处理包含逗号或引号的值
        if (typeof value === 'string' && (value.includes(',') || value.includes('"') || value.includes('\n'))) {
          return `"${value.replace(/"/g, '""')}"`
        }
        return value || ''
      }).join(','))
    ].join('\n')

    return csvContent
  }

  const downloadCSV = (csvContent: string, filename: string) => {
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    if (link.download !== undefined) {
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', filename)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      URL.revokeObjectURL(url)
    }
  }

  const detectedPlatform = detectPlatform(url)

  // 排序后的数据
  const sortedStreamingData = useMemo(() => {
    if (streamingData.length === 0) return []

    return [...streamingData].sort((a, b) => {
      let aValue: any = a[sortField]
      let bValue: any = b[sortField]

      // 处理数值类型
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortOrder === 'desc' ? bValue - aValue : aValue - bValue
      }

      // 处理字符串类型
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
        return sortOrder === 'desc'
          ? bValue.localeCompare(aValue)
          : aValue.localeCompare(bValue)
      }

      // 处理日期类型
      if (sortField === 'scraped_at') {
        const aDate = new Date(aValue).getTime()
        const bDate = new Date(bValue).getTime()
        return sortOrder === 'desc' ? bDate - aDate : aDate - bDate
      }

      return 0
    })
  }, [streamingData, sortField, sortOrder])

  // 处理排序
  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')
    } else {
      setSortField(field)
      setSortOrder('desc')
    }
  }

    // 获取排序图标
  const getSortIcon = (field: SortField) => {
    if (sortField !== field) {
      return <ArrowUpDown className="w-4 h-4 text-gray-400" />
    }
    return sortOrder === 'desc'
      ? <ArrowDown className="w-4 h-4 text-blue-400" />
      : <ArrowUp className="w-4 h-4 text-blue-400" />
  }

  // 排序表头组件
  const SortableTableHead = ({ field, children, className }: {
    field: SortField,
    children: React.ReactNode,
    className?: string
  }) => (
    <TableHead
      className={`cursor-pointer hover:bg-white/5 transition-colors ${className}`}
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-2">
        {children}
        {getSortIcon(field)}
      </div>
    </TableHead>
  )

  return (
    <div className="min-h-screen bg-black relative">
        {/* Header */}
      <header className="fixed top-0 left-0 right-0 w-full border-b border-white/10 backdrop-blur-sm bg-black/80 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            {/* Logo and Brand */}
            <div className="flex items-center gap-3">
              <img 
                src="/favicon/favicon-96x96.png" 
                alt="FollowNet Logo" 
                className="w-10 h-10 rounded-full shadow-lg"
              />
              <span className="text-xl font-bold text-white">FollowNet</span>
          </div>
            
            {/* Action Buttons */}
            <div className="flex items-center gap-2 sm:gap-4">
              <button
                onClick={() => window.open('https://github.com/wendy7756/FollowNet', '_blank')}
                className="flex items-center gap-2 px-3 sm:px-4 py-2 border border-white/30 rounded-lg bg-transparent text-white hover:bg-white/10 transition-all duration-200"
              >
                <Github className="w-4 h-4" />
                <span className="text-xs sm:text-sm font-medium hidden sm:inline">Star on Github</span>
                <span className="text-xs font-medium sm:hidden">Star</span>
              </button>
              <button
                onClick={() => window.location.href = 'mailto:kimiao777@outlook.com'}
                className="flex items-center gap-2 px-3 sm:px-4 py-2 border border-white/30 rounded-lg bg-transparent text-white hover:bg-white/10 transition-all duration-200"
              >
                <Mail className="w-4 h-4" />
                <span className="text-xs sm:text-sm font-medium hidden sm:inline">Contact</span>
                <span className="text-xs font-medium sm:hidden">Email</span>
              </button>
            </div>
          </div>
        </div>
      </header>
      
      <div className="container mx-auto px-4 py-8 relative z-10">
        {/* Main Title */}
        <div className="text-center mb-12 mt-24">
          <div className="mb-8">
            <h1 className="font-bold text-cyan-400 leading-relaxed">
              <div className="text-4xl md:text-5xl lg:text-6xl mb-3">Discover Who Follows Your Competitors</div>
              <div className="text-3xl md:text-4xl lg:text-5xl">Turn Them Into Your Customers</div>
            </h1>
          </div>
        </div>

        {/* Search form */}
        <div className="max-w-6xl mx-auto mb-12">
          <form onSubmit={handleSubmit} className="relative">
            <div className="relative">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Enter URL to scrape, e.g.: https://github.com/username"
                className={`w-full px-6 py-4 text-lg bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-transparent ${
                  detectedPlatform ? 'pr-48' : 'pr-32'
                }`}
                disabled={streamingStatus.isStreaming}
              />
              {detectedPlatform && (
                <div className="absolute right-32 top-1/2 transform -translate-y-1/2 px-3 py-1 bg-blue-500/20 text-blue-200 text-sm rounded-lg flex items-center gap-2">
                  {detectedPlatform === 'GitHub' && <Github className="w-4 h-4" />}
                  {detectedPlatform === 'Twitter/X' && <Twitter className="w-4 h-4" />}
                  {detectedPlatform === 'Product Hunt' && <Star className="w-4 h-4" />}
                  {detectedPlatform === 'Hacker News' && <Search className="w-4 h-4" />}
                  {(detectedPlatform === 'Weibo' || detectedPlatform === 'YouTube' || detectedPlatform === 'Reddit' || detectedPlatform === 'Medium' || detectedPlatform === 'Bilibili') && <Globe className="w-4 h-4" />}
                  <span>{detectedPlatform}</span>
                </div>
              )}
              <button
                type="submit"
                disabled={streamingStatus.isStreaming || !url.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 px-4 py-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm font-medium"
              >
                {streamingStatus.isStreaming ? 'Scraping...' : 'Start'}
              </button>
            </div>
          </form>

          {/* Advanced Settings Toggle */}
          <div className="mt-3 flex justify-center">
            <button
              onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
              className="flex items-center gap-2 text-gray-300 hover:text-blue-300 text-sm transition-colors duration-200"
              disabled={streamingStatus.isStreaming}
            >
              <Settings className="w-4 h-4" />
              <span>Advanced Settings</span>
              <ChevronDown 
                className={`w-4 h-4 transition-transform duration-200 ${showAdvancedSettings ? 'rotate-180' : ''}`} 
              />
            </button>
          </div>

          {/* Advanced Settings Panel */}
          {showAdvancedSettings && (
            <div className="mt-4 bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Unlimited Mode Toggle */}
                <div className="space-y-3">
                  <label className="flex items-center gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={unlimitedMode}
                      onChange={(e) => setUnlimitedMode(e.target.checked)}
                      className="w-5 h-5 rounded border-white/20 bg-white/10 text-blue-500 focus:ring-blue-500 focus:ring-offset-0"
                      disabled={streamingStatus.isStreaming}
                    />
                    <div>
                      <span className="text-white font-medium">Unlimited Mode</span>
                      <p className="text-blue-200 text-sm">Scrape more than 250 followers with high performance</p>
                    </div>
                  </label>
                </div>

                {/* Max Users Input */}
                {unlimitedMode && (
                  <div className="space-y-2">
                    <label className="block text-white font-medium">
                      Maximum Users to Scrape
                    </label>
                    <input
                      type="number"
                      value={maxUsers}
                      onChange={(e) => setMaxUsers(Math.max(1, parseInt(e.target.value) || 250))}
                      min="1"
                      max="5000"
                      step="50"
                      className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-blue-200 focus:outline-none focus:ring-2 focus:ring-blue-400"
                      disabled={streamingStatus.isStreaming}
                    />
                    <p className="text-blue-200 text-sm">
                      Recommended: 500-1000 for optimal performance
                    </p>
                  </div>
                )}
              </div>

              {/* Performance Info */}
              {unlimitedMode && (
                <div className="mt-4 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
                  <h4 className="text-blue-200 font-medium mb-2">🚀 Performance Mode Active</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-blue-300">Expected Speed:</span>
                      <span className="text-white ml-2">5-8x faster</span>
                    </div>
                    <div>
                      <span className="text-blue-300">Concurrency:</span>
                      <span className="text-white ml-2">20 users parallel</span>
                    </div>
                    <div>
                      <span className="text-blue-300">Memory Usage:</span>
                      <span className="text-white ml-2">30% optimized</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Export button */}
              {streamingData.length > 0 && (
            <div className="mt-4 flex justify-center">
                <button
                  onClick={() => {
                    const csvContent = generateCSV(sortedStreamingData)
                    downloadCSV(csvContent, `follownet_${detectedPlatform || 'data'}_sorted_by_${sortField}_${sortOrder}_${new Date().toISOString().split('T')[0]}.csv`)
                  }}
                  disabled={streamingStatus.isStreaming}
                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl hover:from-green-600 hover:to-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm"
                >
                  <Download className="w-4 h-4" />
                Export CSV ({streamingData.length} users)
                </button>
            </div>
          )}

          {error && (
            <div className="mt-4 p-4 bg-yellow-500/20 border border-yellow-500/30 rounded-xl text-yellow-200">
              {error}
            </div>
          )}
        </div>

                {/* Real-time scraping display area */}
        {(streamingStatus.isStreaming || streamingData.length > 0 || totalFollowers >= 0) && (
          <div className="max-w-6xl mx-auto mb-8">
            {/* Progress bar display */}
            {streamingStatus.isStreaming && (
              <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-4">
                    <div className="animate-spin w-6 h-6 border-2 border-blue-400 border-t-transparent rounded-full"></div>
                    <h2 className="text-xl font-semibold text-white">Real-time Scraping</h2>
                  </div>
                  <button
                    onClick={handleStopScraping}
                    className="flex items-center gap-2 px-4 py-2 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300 hover:bg-red-500/30 hover:text-red-200 transition-all duration-200"
                    title="Stop scraping"
                  >
                    <X className="w-4 h-4" />
                    <span className="text-sm font-medium">Stop</span>
                  </button>
                </div>

                <div className="mb-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-blue-200 text-sm">
                      {streamingStatus.stage && `Stage ${streamingStatus.stage}: `}
                      {streamingStatus.message}
                      {streamingStatus.currentUser && ` - Current user: ${streamingStatus.currentUser}`}
                    </span>
                    <span className="text-blue-400 font-medium text-sm">{Math.round(streamingStatus.progress)}%</span>
                  </div>
                  <div className="w-full bg-white/20 rounded-full h-3">
                    <div
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-3 rounded-full transition-all duration-300"
                      style={{ width: `${streamingStatus.progress}%` }}
                    ></div>
                  </div>
                </div>

                {streamingStatus.processedCount !== undefined && streamingStatus.totalCount !== undefined && (
                  <div className="text-sm text-blue-200">
                    Processed: <span className="text-blue-400 font-medium">{streamingStatus.processedCount}/{streamingStatus.totalCount}</span> users
                    {streamingData.length > 0 && (
                      <span className="ml-4">Detailed info obtained: <span className="text-green-400 font-medium">{streamingData.length}</span> users</span>
                    )}
                  </div>
                )}
                
                {/* Pagination info */}
                {totalFollowers >= 0 && !streamingStatus.isStreaming && (
                  <div className="text-sm text-blue-200 mt-2">
                    <span className="text-blue-400 font-medium">Progress:</span> Page {currentPage} of {totalPages}
                    <span className="ml-4 text-blue-300">Total followers: <span className="text-blue-400 font-medium">{totalFollowers.toLocaleString()}</span></span>
                  </div>
                )}
              </div>
            )}

            {/* Real-time user data display */}
            {(!streamingStatus.isStreaming && totalFollowers >= 0) && (
              <>
                <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 mb-6">
                  <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                    <div>
                      <h2 className="text-xl font-semibold text-white mb-2">
                        Scraping Results (<span className="text-blue-400">{streamingData.length}</span> users)
                        {streamingStatus.isStreaming && <span className="text-green-400 ml-2 animate-pulse">Updating...</span>}
                        {!streamingStatus.isStreaming && <span className="text-green-400 ml-2">✓ Complete</span>}
                      </h2>
                      {!streamingStatus.isStreaming && (
                        <p className="text-blue-300 text-sm">
                          Current sort: {sortField === 'follower_count' && 'Followers'}
                          {sortField === 'following_count' && 'Following'}
                          {sortField === 'public_repos' && 'Repositories'}
                          {sortField === 'scraped_at' && 'Scraped time'}
                          {sortField === 'username' && 'Username'}
                          <span className="ml-1">
                            ({sortOrder === 'desc' ? 'High to Low' : 'Low to High'})
                          </span>
                        </p>
                      )}
                    </div>


                  </div>
                </div>

                                                {/* User data table */}
                <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl overflow-hidden">
                  <div className="overflow-x-auto">
                    <Table className="min-w-[800px]">
                      <TableHeader>
                        <TableRow className="border-white/20 hover:bg-white/5">
                          <TableHead className="text-blue-200 font-medium">Avatar</TableHead>
                          <SortableTableHead field="username" className="text-blue-200 font-medium">
                            User Info
                          </SortableTableHead>
                          <TableHead className="text-blue-200 font-medium">Bio</TableHead>
                          <SortableTableHead field="follower_count" className="text-blue-200 font-medium">
                            Followers
                          </SortableTableHead>
                          <SortableTableHead field="following_count" className="text-blue-200 font-medium">
                            Following
                          </SortableTableHead>
                          <SortableTableHead field="public_repos" className="text-blue-200 font-medium">
                            Repos
                          </SortableTableHead>
                          <TableHead className="text-blue-200 font-medium">Actions</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {streamingData.length > 0 ? sortedStreamingData.map((user, index) => (
                          <TableRow
                            key={`${user.username}-${index}`}
                            className="border-white/20 hover:bg-white/5 cursor-pointer animate-fade-in"
                            onClick={() => handleUserClick(user.profile_url)}
                            style={{
                              animationDelay: `${(index % 5) * 100}ms`
                            }}
                          >
                            {/* 头像 */}
                            <TableCell>
                              <img
                                src={user.avatar_url}
                                alt={user.username}
                                className="w-12 h-12 rounded-full border-2 border-white/20"
                                onError={(e) => {
                                  e.currentTarget.src = `https://ui-avatars.com/api/?name=${user.username}&background=random`
                                }}
                              />
                            </TableCell>

                            {/* 用户信息 */}
                            <TableCell>
                              <div className="space-y-1">
                                <div className="flex items-center gap-2">
                                  <span className="font-semibold text-white truncate max-w-[150px]">
                                    {user.display_name || user.username}
                                  </span>
                                  {index < 3 && streamingStatus.isStreaming && (
                                    <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full animate-pulse">
                                      New
                                    </span>
                                  )}
                                </div>
                                <div className={`text-sm ${
                                  sortField === 'username' ? 'text-blue-300 font-medium' : 'text-blue-200'
                                }`}>
                                  @{user.username}
                                </div>
                              </div>
                            </TableCell>

                            {/* Bio */}
                            <TableCell>
                              <div className="text-blue-100 text-sm max-w-[200px] truncate">
                                {user.bio || '-'}
                              </div>
                            </TableCell>

                            {/* Followers count */}
                            <TableCell>
                              <div className={`flex items-center gap-1 ${
                                sortField === 'follower_count' ? 'text-blue-300 font-medium' : 'text-blue-200'
                              }`}>
                                <Users className="w-4 h-4 text-blue-400" />
                                <span>{user.follower_count.toLocaleString()}</span>
                              </div>
                            </TableCell>

                            {/* Following count */}
                            <TableCell>
                              <div className={`flex items-center gap-1 ${
                                sortField === 'following_count' ? 'text-blue-300 font-medium' : 'text-blue-200'
                              }`}>
                                <Users className="w-4 h-4 text-green-400" />
                                <span>{user.following_count.toLocaleString()}</span>
                              </div>
                            </TableCell>

                            {/* Repository count */}
                            <TableCell>
                              <div className={`flex items-center gap-1 ${
                                sortField === 'public_repos' ? 'text-blue-300 font-medium' : 'text-blue-200'
                              }`}>
                                <Github className="w-4 h-4 text-gray-400" />
                                <span>{user.public_repos || 0}</span>
                              </div>
                            </TableCell>

                            {/* Actions */}
                            <TableCell>
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleUserClick(user.profile_url)
                                  }}
                                  className="p-1 rounded hover:bg-white/10 transition-colors"
                                  title="Visit user profile"
                                >
                                  <Github className="w-4 h-4 text-blue-400" />
                                </button>
                                {user.email && (
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      window.location.href = `mailto:${user.email}`
                                    }}
                                    className="p-1 rounded hover:bg-white/10 transition-colors"
                                    title="Send email"
                                  >
                                    <Mail className="w-4 h-4 text-red-400" />
                                  </button>
                                )}
                                {user.website && (
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      window.open(user.website, '_blank')
                                    }}
                                    className="p-1 rounded hover:bg-white/10 transition-colors"
                                    title="Visit website"
                                  >
                                    <Globe className="w-4 h-4 text-teal-400" />
                                  </button>
                                )}
                              </div>
                            </TableCell>
                          </TableRow>
                        )) : (
                          <TableRow>
                            <TableCell colSpan={7} className="text-center py-12">
                              <div className="text-blue-200">
                                <Users className="w-12 h-12 mx-auto mb-4 text-blue-400" />
                                <p className="text-lg font-medium">No followers found</p>
                                <p className="text-sm text-blue-300 mt-2">
                                  This user has {totalFollowers} followers
                                </p>
                              </div>
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </div>
                  
                  {/* Pagination Controls */}
                  {!streamingStatus.isStreaming && totalPages >= 1 && (
                    <div className="mt-4 mb-8 mx-6 flex items-center justify-between">
                      <div className="text-sm text-blue-200">
                        Showing page {currentPage} of {totalPages} ({totalFollowers.toLocaleString()} total followers)
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => {
                            if (currentPage > 1) {
                              // TODO: Implement previous page functionality
                              console.log('Previous page clicked')
                            }
                          }}
                          disabled={currentPage <= 1 || streamingStatus.isStreaming}
                          className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                        >
                          Previous
                        </button>
                        <span className="px-3 py-2 text-blue-200 text-sm">
                          Page {currentPage}
                        </span>
                        <button
                          onClick={() => {
                            if (currentPage < totalPages) {
                              // TODO: Implement next page functionality
                              console.log('Next page clicked')
                            }
                          }}
                          disabled={currentPage >= totalPages || streamingStatus.isStreaming}
                          className="px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm hover:bg-white/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>
        )}



        {/* Platform display - only show when no results and not scraping */}
        {!streamingStatus.isStreaming && totalFollowers < 0 && (
          <div className="max-w-6xl mx-auto mt-16">
            <h3 className="text-3xl font-bold text-white text-center mb-12">Supported Platforms</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {/* 第一排 */}
                             {/* GitHub */}
               <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src="/logos/github.png" 
                    alt="GitHub" 
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'block';
                    }}
                  />
                  <Github className="w-8 h-8 text-white hidden" />
                </div>
                <h4 className="text-xl font-bold text-white mb-3">GitHub</h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Find developers who starred repositories or follow specific users.
                </p>
              </div>

                             {/* Twitter/X */}
               <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center relative">
                <div className="absolute top-2 right-2 bg-blue-500/70 text-white text-xs px-2 py-1 rounded-full">
                  Coming soon
                </div>
                <div className="w-16 h-16 mx-auto mb-4 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src="/logos/twitter.png" 
                    alt="Twitter/X" 
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'block';
                    }}
                  />
                  <Twitter className="w-8 h-8 text-white hidden" />
                </div>
                <h4 className="text-xl font-bold text-white mb-3">Twitter/X</h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Discover people who follow your industry rivals or key topics.
                </p>
              </div>

              {/* YouTube */}
              <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center relative">
                <div className="absolute top-2 right-2 bg-blue-500/70 text-white text-xs px-2 py-1 rounded-full">
                  Coming soon
                </div>
                <div className="w-16 h-16 mx-auto mb-4 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src="/logos/youtube.png" 
                    alt="YouTube" 
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'block';
                    }}
                  />
                  <Globe className="w-8 h-8 text-white hidden" />
              </div>
                <h4 className="text-xl font-bold text-white mb-3">YouTube</h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Engage with subscribers of your competitors' channels.
                </p>
            </div>

              {/* 第二排 */}
              {/* Instagram */}
              <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center relative">
                <div className="absolute top-2 right-2 bg-blue-500/70 text-white text-xs px-2 py-1 rounded-full">
                  Coming soon
                </div>
                <div className="w-16 h-16 mx-auto mb-4 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src="/logos/instagram.png" 
                    alt="Instagram" 
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'block';
                    }}
                  />
                  <Users className="w-8 h-8 text-white hidden" />
                </div>
                <h4 className="text-xl font-bold text-white mb-3">Instagram</h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Reach audiences following brands, creators, or competitors on Ins.
                </p>
              </div>

              {/* Reddit */}
              <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center relative">
                <div className="absolute top-2 right-2 bg-blue-500/70 text-white text-xs px-2 py-1 rounded-full">
                  Coming soon
                </div>
                <div className="w-16 h-16 mx-auto mb-4 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src="/logos/reddit.png" 
                    alt="Reddit" 
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'block';
                    }}
                  />
                  <Search className="w-8 h-8 text-white hidden" />
                </div>
                <h4 className="text-xl font-bold text-white mb-3">Reddit</h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Identify users engaging in competitor subreddits or related communities.
                </p>
              </div>

              {/* LinkedIn */}
              <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-6 text-center relative">
                <div className="absolute top-2 right-2 bg-blue-500/70 text-white text-xs px-2 py-1 rounded-full">
                  Coming soon
                </div>
                <div className="w-16 h-16 mx-auto mb-4 rounded-full overflow-hidden flex items-center justify-center">
                  <img 
                    src="/logos/linkedin.png" 
                    alt="LinkedIn" 
                    className="w-12 h-12 object-contain"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                      const fallback = e.currentTarget.nextElementSibling as HTMLElement;
                      if (fallback) fallback.style.display = 'block';
                    }}
                  />
                  <Building className="w-8 h-8 text-white hidden" />
                </div>
                <h4 className="text-xl font-bold text-white mb-3">LinkedIn</h4>
                <p className="text-gray-300 text-sm leading-relaxed">
                  Connect with professionals who follow your competitors or their company pages.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <footer className="w-full border-t border-white/10 bg-black/50 backdrop-blur-sm mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            {/* Copyright */}
            <div className="text-center md:text-left">
              <p className="text-white/70 text-sm">
                © 2025 FollowNet. All rights reserved.
              </p>
            </div>
            
            {/* Links */}
            <div className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6 text-sm">
              <Link 
                href="/terms" 
                className="text-white/70 hover:text-white transition-colors duration-200"
              >
                Terms of Service
              </Link>
              <Link 
                href="/privacy" 
                className="text-white/70 hover:text-white transition-colors duration-200"
              >
                Privacy Policy
              </Link>
              <a 
                href="mailto:kimiao777@outlook.com" 
                className="text-white/70 hover:text-white transition-colors duration-200"
              >
                Contact
              </a>
              <a 
                href="https://github.com/wendy7756/FollowNet" 
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-white/70 hover:text-white transition-colors duration-200"
              >
                <Github className="w-4 h-4" />
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}