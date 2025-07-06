# Contributing to FollowNet

Thank you for your interest in contributing to FollowNet! We welcome contributions from developers around the world to help expand platform support and improve the tool.

## 🎯 How You Can Contribute

### 1. Adding New Platform Support
The most valuable contribution is adding support for new social media platforms. We currently support:
- ✅ **GitHub** (Fully implemented)
- 🔄 **Twitter/X** (Coming soon)
- 🔄 **Instagram** (Coming soon)
- 🔄 **LinkedIn** (Coming soon)
- 🔄 **YouTube** (Coming soon)
- 🔄 **TikTok** (Coming soon)
- 🔄 **Reddit** (Coming soon)
- 🔄 **Medium** (Coming soon)

### 2. Other Ways to Contribute
- 🐛 **Bug Reports**: Report issues and bugs
- 💡 **Feature Requests**: Suggest new features
- 📚 **Documentation**: Improve documentation and guides
- 🔧 **Code Improvements**: Optimize existing code
- 🌐 **Translations**: Add support for more languages

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git
- Basic knowledge of web scraping
- Familiarity with FastAPI and Next.js

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/FollowNet.git
   cd FollowNet
   ```

2. **Set up the backend**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install
   ```

3. **Set up the frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Start development servers**
   ```bash
   # Terminal 1: Backend
   cd backend && source venv/bin/activate && python main.py
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   ```

## 📝 Adding a New Platform

### Step 1: Create the Scraper Module

Create a new directory for your platform in `backend/scrapers/`:

```
backend/scrapers/
├── base.py
├── github/
├── your_platform/
│   ├── __init__.py
│   ├── get_followers_list.py
│   └── scrape_profiles.py
```

### Step 2: Implement the Base Classes

Your scraper should inherit from the base classes and implement required methods:

```python
# backend/scrapers/your_platform/get_followers_list.py
from ..base import BaseFollowersListScraper

class YourPlatformFollowersListScraper(BaseFollowersListScraper):
    def __init__(self):
        super().__init__()
        self.platform_name = "your_platform"
    
    async def scrape_followers_list(self, url: str, max_pages: int = 5) -> dict:
        """
        Scrape followers list from the platform
        
        Returns:
            dict: {
                'csv_file': str,
                'total_followers': int,
                'total_pages': int,
                'scraped_followers': int
            }
        """
        # Implement your scraping logic here
        pass
```

```python
# backend/scrapers/your_platform/scrape_profiles.py
from ..base import BaseProfileScraper

class YourPlatformProfileScraper(BaseProfileScraper):
    def __init__(self):
        super().__init__()
        self.platform_name = "your_platform"
    
    async def scrape_profiles(self, csv_file: str, max_users: int = None) -> str:
        """
        Scrape detailed profiles from the followers list
        
        Returns:
            str: Path to the detailed CSV file
        """
        # Implement your profile scraping logic here
        pass
```

### Step 3: Create the Two-Stage Scraper

```python
# backend/scrapers/your_platform_two_stage.py
from .your_platform.get_followers_list import YourPlatformFollowersListScraper
from .your_platform.scrape_profiles import YourPlatformProfileScraper

class YourPlatformTwoStageScraper:
    def __init__(self):
        self.stage1_scraper = YourPlatformFollowersListScraper()
        self.stage2_scraper = YourPlatformProfileScraper()
    
    async def scrape_with_progress(self, url: str, max_users: int = None, unlimited: bool = False):
        """
        Two-stage scraping with progress reporting
        """
        # Implement the two-stage process
        pass
```

### Step 4: Update the Main API

Add your platform to the main API in `backend/main.py`:

```python
# Import your scraper
from scrapers.your_platform_two_stage import YourPlatformTwoStageScraper

# Add platform detection
def detect_platform(url: str) -> str:
    # Add your platform detection logic
    if "your-platform.com" in url:
        return "your_platform"
    # ... existing logic

# Add to scraping logic
async def handle_scraping(url: str, max_users: int = None, unlimited: bool = False):
    platform = detect_platform(url)
    
    if platform == "your_platform":
        scraper = YourPlatformTwoStageScraper()
        async for progress in scraper.scrape_with_progress(url, max_users, unlimited):
            yield progress
```

### Step 5: Update Frontend Detection

Add platform detection to the frontend in `frontend/app/page.tsx`:

```typescript
const detectPlatform = (inputUrl: string) => {
  // Add your platform detection
  if (inputUrl.includes('your-platform.com')) {
    return 'Your Platform'
  }
  // ... existing logic
}
```

## 🔧 Development Guidelines

### Code Style
- **Python**: Follow PEP 8 style guidelines
- **TypeScript**: Use consistent naming conventions
- **Comments**: Add clear comments for complex logic
- **Error Handling**: Implement comprehensive error handling

### Scraping Best Practices
- **Rate Limiting**: Implement delays between requests
- **Respectful Scraping**: Don't overload servers
- **Error Recovery**: Handle network failures gracefully
- **Data Validation**: Validate scraped data before saving
- **Privacy**: Only scrape publicly available data

### Testing
- Test with multiple user profiles
- Test edge cases (empty profiles, private accounts)
- Test error scenarios (network failures, rate limits)
- Verify CSV output format and data integrity

### Performance Considerations
- Use efficient selectors for web elements
- Implement concurrent processing where possible
- Optimize memory usage for large datasets
- Add progress reporting for long-running operations

## 📋 Platform-Specific Guidelines

### Twitter/X
- Handle rate limiting (15-minute windows)
- Respect API limits and ToS
- Handle protected accounts gracefully
- Consider using Twitter API v2 if available

### Instagram
- Be aware of strict anti-scraping measures
- Implement proper session management
- Handle dynamic content loading
- Consider Instagram Basic Display API

### LinkedIn
- Respect professional network privacy
- Handle LinkedIn's anti-scraping measures
- Consider LinkedIn API for authorized access
- Focus on public profile data only

### YouTube
- Use YouTube Data API v3 when possible
- Handle channel vs user URLs
- Respect API quotas and limits
- Consider subscriber privacy settings

## 🐛 Bug Reports

When reporting bugs, please include:
- **Platform**: Which platform you were scraping
- **URL**: The specific URL that caused the issue
- **Error Message**: Full error message and stack trace
- **Environment**: OS, Python version, browser version
- **Steps to Reproduce**: Clear steps to reproduce the issue

## 💡 Feature Requests

For feature requests, please provide:
- **Use Case**: Why this feature would be useful
- **Platform**: Which platform(s) it applies to
- **Implementation Ideas**: Any thoughts on how to implement
- **Priority**: How important this feature is to you

## 📚 Documentation

Help improve our documentation by:
- Adding examples for new platforms
- Improving API documentation
- Creating tutorial videos
- Translating documentation to other languages

## 🔒 Security and Privacy

- **Never scrape private data**: Only access publicly available information
- **Respect ToS**: Always comply with platform terms of service
- **Rate limiting**: Implement appropriate delays between requests
- **Data handling**: Securely handle any temporary data storage
- **User consent**: Ensure users understand what data is being collected

## 📞 Getting Help

If you need help with your contribution:
- **GitHub Issues**: Ask questions in our issues
- **Discussions**: Use GitHub Discussions for general questions
- **Email**: Contact us at dev@follownet.com
- **Documentation**: Check our [Wiki](https://github.com/wendy7756/FollowNet/wiki)

## 🎉 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes
- Contributors page
- Social media shoutouts

## 📄 License

By contributing to FollowNet, you agree that your contributions will be licensed under the Apache License 2.0.

---

**Thank you for helping make FollowNet better! Your contributions help developers worldwide access social media data more easily and ethically.** 