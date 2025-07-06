import Link from 'next/link'

export default function TermsOfService() {
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
          <h1 className="text-4xl font-bold text-white mb-2">Terms of Service</h1>
          <p className="text-blue-200">Last updated: July 2025</p>
        </div>

        {/* Content */}
        <div className="max-w-4xl mx-auto bg-white/10 backdrop-blur-sm border border-white/20 rounded-2xl p-8">
          <div className="prose prose-invert max-w-none">
            
            <h2 className="text-2xl font-semibold text-white mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-300 mb-6">
              By accessing and using FollowNet ("the Service"), you accept and agree to be bound by the terms and provision of this agreement. 
              If you do not agree to abide by the above, please do not use this service.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">2. Description of Service</h2>
            <p className="text-gray-300 mb-6">
              FollowNet is a web-based tool that allows users to extract publicly available follower data from various social media platforms 
              including but not limited to GitHub, Twitter/X, Instagram, LinkedIn, and YouTube. The service provides data export functionality 
              in CSV format for analysis purposes.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">3. Acceptable Use</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">You agree to use FollowNet only for lawful purposes and in accordance with these Terms. You agree NOT to use the service:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>To violate any applicable local, state, national, or international law or regulation</li>
                <li>To scrape private or protected data that is not publicly available</li>
                <li>To harass, abuse, or harm other users or individuals</li>
                <li>To spam or send unsolicited messages to scraped contacts</li>
                <li>To violate the terms of service of third-party platforms</li>
                <li>To engage in any activity that could damage, disable, or impair the service</li>
                <li>To attempt to gain unauthorized access to any systems or networks</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">4. Data Collection and Privacy</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">FollowNet only collects and processes publicly available data from social media platforms. We:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Do not store personal data permanently on our servers</li>
                <li>Do not collect private or protected information</li>
                <li>Provide data export functionality for user convenience</li>
                <li>Respect platform rate limits and terms of service</li>
                <li>Encourage users to use scraped data responsibly and ethically</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">5. User Responsibilities</h2>
            <div className="text-gray-300 mb-6">
              <p className="mb-4">As a user of FollowNet, you are responsible for:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Ensuring your use complies with all applicable laws and regulations</li>
                <li>Respecting the privacy and rights of individuals whose data you access</li>
                <li>Complying with the terms of service of third-party platforms</li>
                <li>Using scraped data ethically and responsibly</li>
                <li>Not exceeding reasonable usage limits to avoid service disruption</li>
                <li>Protecting any exported data according to applicable privacy laws</li>
              </ul>
            </div>

            <h2 className="text-2xl font-semibold text-white mb-4">6. Platform Compliance</h2>
            <p className="text-gray-300 mb-6">
              FollowNet operates by accessing publicly available data from various social media platforms. Users must ensure their usage 
              complies with each platform's terms of service, API usage policies, and rate limits. We are not responsible for any 
              violations of third-party platform terms that may result from your use of our service.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">7. Service Availability</h2>
            <p className="text-gray-300 mb-6">
              While we strive to maintain high availability, FollowNet is provided "as is" without warranty of any kind. We do not 
              guarantee uninterrupted service and may experience downtime for maintenance, updates, or due to factors beyond our control.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">8. Limitation of Liability</h2>
            <p className="text-gray-300 mb-6">
              In no event shall FollowNet, its operators, or contributors be liable for any indirect, incidental, special, consequential, 
              or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, 
              resulting from your use of the service.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">9. Intellectual Property</h2>
            <p className="text-gray-300 mb-6">
              FollowNet is open-source software licensed under the Apache License 2.0. The service itself, including its design, 
              functionality, and documentation, is protected by copyright and other intellectual property laws. Users may contribute 
              to the project under the terms of the Apache License 2.0.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">10. Termination</h2>
            <p className="text-gray-300 mb-6">
              We may terminate or suspend your access to FollowNet immediately, without prior notice or liability, if you breach 
              these Terms of Service. Upon termination, your right to use the service will cease immediately.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">11. Changes to Terms</h2>
            <p className="text-gray-300 mb-6">
              We reserve the right to modify or replace these Terms at any time. If a revision is material, we will try to provide 
              at least 30 days notice prior to any new terms taking effect. What constitutes a material change will be determined 
              at our sole discretion.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">12. Governing Law</h2>
            <p className="text-gray-300 mb-6">
              These Terms shall be interpreted and governed by the laws of the jurisdiction in which the service is operated, 
              without regard to its conflict of law provisions.
            </p>

            <h2 className="text-2xl font-semibold text-white mb-4">13. Contact Information</h2>
            <p className="text-gray-300 mb-6">
              If you have any questions about these Terms of Service, please contact us at:
            </p>
            <div className="text-gray-300 mb-6">
              <p>Email: <a href="mailto:kimiao777@outlook.com" className="text-blue-400 hover:text-blue-300">kimiao777@outlook.com</a></p>
              <p>GitHub: <a href="https://github.com/wendy7756/FollowNet" className="text-blue-400 hover:text-blue-300" target="_blank" rel="noopener noreferrer">https://github.com/wendy7756/FollowNet</a></p>
            </div>

            <div className="mt-8 p-4 bg-blue-500/20 border border-blue-500/30 rounded-lg">
              <h3 className="text-lg font-semibold text-blue-200 mb-2">🛡️ Ethical Usage Reminder</h3>
              <p className="text-blue-200 text-sm">
                FollowNet is designed to help developers and researchers access publicly available social media data ethically. 
                Please use this tool responsibly, respect user privacy, and comply with all applicable laws and platform terms of service.
              </p>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
} 