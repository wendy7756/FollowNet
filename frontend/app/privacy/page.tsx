import Link from 'next/link'

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen bg-black">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center gap-2 text-white hover:text-blue-300 transition-colors duration-200 mb-4">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to FollowNet
          </Link>
          <h1 className="text-4xl font-bold text-white mb-2">Privacy Policy</h1>
          <p className="text-blue-200">Last updated: July 2025</p>
        </div>

        {/* Content */}
        <div className="max-w-4xl mx-auto bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8">
          <div className="prose prose-invert max-w-none">
            
            <h2 className="text-2xl font-semibold text-white mb-4">1. Introduction</h2>
            <p className="text-gray-300 mb-6">
              FollowNet ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, 
              use, disclose, and safeguard your information when you use our social media data extraction service.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">2. Information We Collect</h2>
            
            <h3 className="text-xl font-semibold text-white mb-3">2.1 Information You Provide</h3>
            <div className="text-gray-300 mb-6">
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>URLs of social media profiles or pages you want to scrape</li>
                <li>Configuration settings for scraping (e.g., maximum users, unlimited mode)</li>
                <li>Any feedback or communications you send to us</li>
              </ul>
            </div>

            <h3 className="text-xl font-semibold text-white mb-3">2.2 Information We Collect Automatically</h3>
            <div className="text-gray-300 mb-6">
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Usage data (pages visited, features used, time spent)</li>
                <li>Technical information (IP address, browser type, device information)</li>
                <li>Performance data (scraping success rates, error logs)</li>
                <li>Cookies and similar tracking technologies</li>
              </ul>
            </div>

            <h3 className="text-xl font-semibold text-white mb-3">2.3 Third-Party Data</h3>
            <p className="text-gray-300 mb-6">
              FollowNet accesses publicly available data from third-party social media platforms. This data is processed temporarily 
              and provided to you in CSV format. We do not permanently store this third-party data on our servers.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">3. How We Use Your Information</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">We use the information we collect to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Provide and maintain our scraping service</li>
                <li>Process your scraping requests and generate CSV exports</li>
                <li>Improve our service performance and user experience</li>
                <li>Communicate with you about service updates or issues</li>
                <li>Ensure compliance with platform terms of service</li>
                <li>Detect and prevent fraud or misuse of our service</li>
                <li>Comply with legal obligations</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">4. Data Retention and Storage</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">Our data retention practices:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Scraped Data:</strong> Temporarily stored during processing, automatically deleted after 24 hours</li>
                <li><strong>CSV Files:</strong> Available for download for 7 days, then automatically deleted</li>
                <li><strong>Usage Logs:</strong> Retained for 30 days for service improvement and debugging</li>
                <li><strong>Error Logs:</strong> Retained for 90 days for technical support and service optimization</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">5. Information Sharing and Disclosure</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">We do not sell, trade, or otherwise transfer your personal information to third parties, except:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Service Providers:</strong> Third-party services that help us operate our platform (hosting, analytics)</li>
                <li><strong>Legal Requirements:</strong> When required by law or to protect our rights and safety</li>
                <li><strong>Business Transfers:</strong> In connection with a merger, acquisition, or asset sale</li>
                <li><strong>Consent:</strong> When you have given us explicit consent to share your information</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">6. Third-Party Platforms</h2>
            <p className="text-gray-300 mb-6">
              FollowNet accesses data from third-party social media platforms. Each platform has its own privacy policy and terms of service. 
              We encourage you to review these policies before using our service to scrape data from these platforms. We are not responsible 
              for the privacy practices of third-party platforms.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">7. Security Measures</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">We implement appropriate security measures to protect your information:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>HTTPS encryption for all data transmission</li>
                <li>Secure server infrastructure and access controls</li>
                <li>Regular security audits and updates</li>
                <li>Automatic deletion of temporary data</li>
                <li>Limited access to personal information by authorized personnel only</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">8. Your Rights and Choices</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">You have the following rights regarding your personal information:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Access:</strong> Request information about what personal data we have about you</li>
                <li><strong>Correction:</strong> Request correction of inaccurate personal information</li>
                <li><strong>Deletion:</strong> Request deletion of your personal information</li>
                <li><strong>Portability:</strong> Request a copy of your personal information in a structured format</li>
                <li><strong>Objection:</strong> Object to the processing of your personal information</li>
                <li><strong>Restriction:</strong> Request restriction of processing your personal information</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">9. Cookies and Tracking</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">We use cookies and similar technologies to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Remember your preferences and settings</li>
                <li>Analyze usage patterns and improve our service</li>
                <li>Provide personalized content and recommendations</li>
                <li>Ensure security and prevent fraud</li>
              </ul>
              <p className="mt-4">You can control cookie settings through your browser preferences.</p>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">10. International Data Transfers</h2>
            <p className="text-gray-300 mb-6">
              Your information may be transferred to and processed in countries other than your own. We ensure that such transfers 
              comply with applicable data protection laws and implement appropriate safeguards to protect your information.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">11. Children's Privacy</h2>
            <p className="text-gray-300 mb-6">
              FollowNet is not intended for use by children under the age of 13. We do not knowingly collect personal information 
              from children under 13. If you believe we have collected information from a child under 13, please contact us immediately.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">12. Changes to This Privacy Policy</h2>
            <p className="text-gray-300 mb-6">
              We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy 
              on this page and updating the "Last updated" date. We encourage you to review this Privacy Policy periodically.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">13. Contact Information</h2>
            <p className="text-gray-300 mb-6">
              If you have any questions about this Privacy Policy or our data practices, please contact us at:
            </p>
            <div className="text-gray-300 mb-6">
              <p>Email: <a href="mailto:kimiao777@outlook.com" className="text-blue-400 hover:text-blue-300">kimiao777@outlook.com</a></p>
              <p>GitHub: <a href="https://github.com/wendy7756/FollowNet" className="text-blue-400 hover:text-blue-300" target="_blank" rel="noopener noreferrer">https://github.com/wendy7756/FollowNet</a></p>
            </div>

            <div className="mt-8 p-4 bg-green-500/20 border border-green-500/30 rounded-lg">
              <h3 className="text-lg font-semibold text-green-200 mb-2">🔒 Privacy-First Approach</h3>
              <p className="text-green-200 text-sm">
                FollowNet is designed with privacy in mind. We only access publicly available data, don't store personal information 
                permanently, and automatically delete temporary data. Your privacy and the privacy of scraped data subjects are our priority.
              </p>
            </div>

            <div className="mt-4 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-200 mb-2">📊 Open Source Transparency</h3>
              <p className="text-blue-200 text-sm">
                As an open-source project, FollowNet's code is publicly available for review. You can examine our data handling practices, 
                contribute improvements, and ensure transparency in how your data is processed.
              </p>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
} 