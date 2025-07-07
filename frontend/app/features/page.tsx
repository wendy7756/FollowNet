import Link from 'next/link'
import { Github, ArrowLeft, Star, Zap, Shield, Users, Target, BarChart3, Mail } from 'lucide-react'

export default function Features() {
  return (
    <div className="min-h-screen w-full bg-black text-white overflow-x-hidden">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 w-full border-b border-white/10 backdrop-blur-sm bg-black/80 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <img 
                src="/favicon/favicon-96x96.png" 
                alt="FollowNet Logo" 
                className="w-10 h-10 rounded-full shadow-lg"
              />
              <span className="text-xl font-bold text-white">FollowNet</span>
            </Link>
            
            <Link 
              href="/"
              className="flex items-center gap-2 px-4 py-2 border border-white/30 rounded-lg bg-transparent text-white hover:bg-white/10 transition-all duration-200"
            >
              <ArrowLeft className="w-4 h-4" />
              <span className="text-sm font-medium">Back to Home</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="w-full bg-black">
        <div className="container mx-auto px-4 py-8 pt-28">
          <div className="max-w-4xl mx-auto">
            {/* Title */}
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-bold text-cyan-400 mb-4">
                Features & Services
              </h1>
              <p className="text-xl text-gray-300">
                Everything you need to know about FollowNet
              </p>
            </div>

            <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8">
              <div className="prose prose-invert max-w-none">
                
                {/* What We Offer */}
                <h2 className="text-3xl font-semibold text-white mb-6 flex items-center gap-3">
                  <Star className="w-8 h-8 text-cyan-400" />
                  What We Offer
                </h2>
                
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                  <div className="bg-white/5 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Users className="w-6 h-6 text-blue-400" />
                      <h3 className="text-xl font-semibold text-white">Audience Discovery</h3>
                    </div>
                    <p className="text-gray-300">
                      Extract follower lists from GitHub, Twitter, and other platforms to discover your competitors' audiences.
                    </p>
                  </div>
                  
                  <div className="bg-white/5 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Target className="w-6 h-6 text-green-400" />
                      <h3 className="text-xl font-semibold text-white">Real-time Scraping</h3>
                    </div>
                    <p className="text-gray-300">
                      Get live data with our streaming technology, processing thousands of profiles efficiently.
                    </p>
                  </div>
                  
                  <div className="bg-white/5 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <BarChart3 className="w-6 h-6 text-purple-400" />
                      <h3 className="text-xl font-semibold text-white">Data Export</h3>
                    </div>
                    <p className="text-gray-300">
                      Export all collected data to CSV format for further analysis and marketing campaigns.
                    </p>
                  </div>
                  
                  <div className="bg-white/5 rounded-xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Zap className="w-6 h-6 text-yellow-400" />
                      <h3 className="text-xl font-semibold text-white">High Performance</h3>
                    </div>
                    <p className="text-gray-300">
                      Unlimited mode with 20x parallel processing and optimized memory usage for large datasets.
                    </p>
                  </div>
                </div>

                {/* Supported Platforms */}
                <h2 className="text-3xl font-semibold text-white mb-6 flex items-center gap-3">
                  <Shield className="w-8 h-8 text-cyan-400" />
                  Supported Platforms
                </h2>
                
                <div className="mb-8">
                  <div className="bg-green-500/20 border border-green-500/30 rounded-lg p-4 mb-4">
                    <h4 className="text-green-400 font-medium mb-2">✅ Currently Available</h4>
                    <ul className="text-gray-300 space-y-1">
                      <li>• <strong>GitHub</strong> - Extract followers, stargazers, and repository contributors</li>
                    </ul>
                  </div>
                  
                  <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
                    <h4 className="text-blue-400 font-medium mb-2">🚀 Coming Soon</h4>
                    <ul className="text-gray-300 space-y-1">
                      <li>• <strong>Twitter/X</strong> - Discover followers and engagement patterns</li>
                      <li>• <strong>LinkedIn</strong> - Professional network analysis</li>
                      <li>• <strong>Instagram</strong> - Social media audience insights</li>
                      <li>• <strong>YouTube</strong> - Subscriber and viewer analysis</li>
                      <li>• <strong>Reddit</strong> - Community member discovery</li>
                    </ul>
                  </div>
                </div>

                {/* Current Limitations */}
                <h2 className="text-3xl font-semibold text-white mb-6">Current Limitations</h2>
                
                <div className="bg-yellow-500/20 border border-yellow-500/30 rounded-lg p-6 mb-8">
                  <ul className="text-gray-300 space-y-3">
                    <li>• <strong>Platform Coverage:</strong> Currently limited to GitHub, with other platforms in development</li>
                    <li>• <strong>Rate Limits:</strong> Subject to platform API rate limits and anti-bot measures</li>
                    <li>• <strong>Data Accuracy:</strong> Depends on public profile information availability</li>
                    <li>• <strong>Real-time Updates:</strong> Data is scraped at the time of request, not continuously updated</li>
                    <li>• <strong>Large Datasets:</strong> Very large follower lists (100k+) may require multiple sessions</li>
                  </ul>
                </div>

                {/* Custom Services */}
                <h2 className="text-3xl font-semibold text-white mb-6 flex items-center gap-3">
                  <Mail className="w-8 h-8 text-cyan-400" />
                  Custom Services
                </h2>
                
                <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-lg p-6 mb-8">
                  <h3 className="text-xl font-semibold text-white mb-4">Need More Than Self-Service?</h3>
                  <p className="text-gray-300 mb-4">
                    If you need comprehensive competitor analysis, we offer custom services including:
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <h4 className="font-medium text-white mb-2">🎯 Audience Analysis</h4>
                      <ul className="text-gray-300 text-sm space-y-1">
                        <li>• Complete competitor follower extraction</li>
                        <li>• User persona development</li>
                        <li>• Demographic analysis</li>
                        <li>• Engagement pattern insights</li>
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-white mb-2">📊 Research & Strategy</h4>
                      <ul className="text-gray-300 text-sm space-y-1">
                        <li>• Market research reports</li>
                        <li>• Audience segmentation</li>
                        <li>• Content strategy recommendations</li>
                        <li>• Competitive intelligence</li>
                      </ul>
                    </div>
                  </div>
                  
                  <div className="bg-white/10 rounded-lg p-4">
                    <p className="text-white font-medium mb-2">Interested in custom services?</p>
                    <p className="text-gray-300 text-sm mb-3">
                      Contact us for personalized competitor analysis, user research, and audience development services.
                    </p>
                    <a 
                      href="mailto:kimiao777@outlook.com?subject=Custom%20Audience%20Analysis%20Services"
                      className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white rounded-lg hover:from-cyan-600 hover:to-blue-600 transition-all duration-200 text-sm font-medium"
                    >
                      <Mail className="w-4 h-4" />
                      Get Custom Analysis
                    </a>
                  </div>
                </div>

                {/* Open Source */}
                <h2 className="text-3xl font-semibold text-white mb-6 flex items-center gap-3">
                  <Github className="w-8 h-8 text-cyan-400" />
                  Open Source
                </h2>
                
                <div className="bg-white/5 rounded-lg p-6">
                  <p className="text-gray-300 mb-4">
                    FollowNet is an open-source project. You can contribute, report issues, or fork the repository on GitHub.
                  </p>
                  <div className="flex flex-wrap gap-4">
                    <a 
                      href="https://github.com/wendy7756/FollowNet"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 border border-white/30 rounded-lg bg-transparent text-white hover:bg-white/10 transition-all duration-200 text-sm"
                    >
                      <Github className="w-4 h-4" />
                      View on GitHub
                    </a>
                    <a 
                      href="https://github.com/wendy7756/FollowNet/issues"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-2 px-4 py-2 border border-white/30 rounded-lg bg-transparent text-white hover:bg-white/10 transition-all duration-200 text-sm"
                    >
                      <Star className="w-4 h-4" />
                      Report Issues
                    </a>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
} 