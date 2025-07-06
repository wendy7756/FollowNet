# FollowNet

A powerful social media follower data export tool that supports scraping and exporting data from GitHub, Twitter, Product Hunt, and other platforms.

## 🎯 Features

- **Multi-platform Support**: Supports GitHub, Twitter/X, Product Hunt, and more
- **Smart Detection**: Automatically detects the platform from input URLs
- **Data Export**: Export scraped data to CSV format
- **Modern Interface**: Modern UI built with Next.js and Tailwind CSS
- **High Performance**: Efficient data scraping using Playwright
- **Unlimited Scraping**: Advanced mode for scraping large datasets (500-5000 users)
- **Real-time Progress**: Live progress tracking and streaming updates

## 🚀 Supported Platforms and Data

### GitHub ✅ Available
- Repository stargazers information
- User followers information
- Extract username, display name, avatar, bio, follower count, repositories, etc.

### Twitter/X 🔄 Coming Soon
- User followers list
- User following list
- Extract username, display name, bio, statistics, etc.

### Product Hunt 🔄 Coming Soon
- Product voters information
- User activity data
- Extract username, bio, voting time, etc.

### Other Platforms 🔄 Coming Soon
- **Instagram**: Followers and following data
- **LinkedIn**: Professional connections
- **YouTube**: Subscriber information
- **Reddit**: Community engagement data
- **TikTok**: Follower analytics
- **Medium**: Reader engagement

## 📁 Project Structure

```
FollowNet/
├── frontend/              # Next.js frontend application
│   ├── app/
│   │   ├── page.tsx      # Main page
│   │   ├── layout.tsx    # Layout component
│   │   └── globals.css   # Global styles
│   ├── package.json
│   └── next.config.js
├── backend/               # FastAPI backend application
│   ├── scrapers/          # Scraper modules
│   │   ├── base.py       # Base scraper class
│   │   ├── github/       # GitHub scrapers
│   │   └── ...           # Other platform scrapers
│   ├── main.py           # FastAPI main application
│   └── requirements.txt   # Python dependencies
└── README.md
```

## 🛠️ Installation and Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers:
```bash
playwright install
```

5. Start the backend server:
```bash
python main.py
```

The backend server will run on `http://localhost:8000`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend application will run on `http://localhost:3000`.

## 📖 Usage

1. Open `http://localhost:3000` in your browser
2. Paste the URL you want to scrape in the input field, for example:
   - GitHub Repository: `https://github.com/owner/repo`
   - GitHub User: `https://github.com/username`
   - Twitter User: `https://twitter.com/username` (coming soon)
   - Product Hunt Product: `https://www.producthunt.com/posts/product-name` (coming soon)
3. The system will automatically detect the platform type
4. Configure advanced settings if needed (unlimited mode, max users)
5. Click the "Start" button to begin scraping
6. Wait for the scraping to complete, then click "Export CSV" to download the data

## 🔧 API Endpoints

### POST /api/scrape-stream
Stream scraping data from the specified URL

**Request Body:**
```json
{
  "url": "https://github.com/username/repo",
  "max_users": 500,
  "unlimited": false
}
```

**Response:** Server-Sent Events (SSE) stream with real-time updates

### GET /api/download/{file_id}
Download the generated CSV file

## 🚀 Performance Features

- **Unlimited Mode**: Scrape 500-5000 users with optimized performance
- **Concurrent Processing**: Up to 20 users processed in parallel
- **Smart Pagination**: Intelligent page navigation and data extraction
- **Resource Optimization**: Reduced memory usage and faster loading
- **Retry Logic**: Automatic retry for failed requests

## ⚠️ Important Notes

1. **Compliance**: Ensure your scraping activities comply with the target website's terms of service
2. **Rate Limiting**: Avoid overly frequent requests to prevent being blocked by platforms
3. **Data Privacy**: Only scrape publicly available data
4. **Terms of Service**: Please read the terms of service of each platform before use
5. **Ethical Usage**: Use this tool responsibly and respect platform policies

## 🤝 Contributing

We welcome contributions to add support for more platforms! Here's how you can help:

### Adding New Platforms

1. **Fork** this repository
2. **Create** a new branch for your platform: `git checkout -b feature/add-platform-name`
3. **Implement** the scraper in `backend/scrapers/platform_name/`
4. **Add** frontend detection logic in `frontend/app/page.tsx`
5. **Test** your implementation thoroughly
6. **Submit** a Pull Request with a clear description

### Priority Platforms We Need Help With

- **Twitter/X**: Followers and following scraping
- **Instagram**: Follower data extraction
- **LinkedIn**: Professional network data
- **YouTube**: Subscriber information
- **TikTok**: Follower analytics
- **Reddit**: Community engagement data
- **Medium**: Reader and clap data
- **Discord**: Server member data
- **Twitch**: Follower and subscriber data

### Development Guidelines

- Follow the existing code structure and patterns
- Add comprehensive error handling
- Include rate limiting and respectful scraping practices
- Write clear documentation for new features
- Test with multiple accounts and edge cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

## 📄 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React full-stack framework
- [Playwright](https://playwright.dev/) - Modern web automation library
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework

## 📞 Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/wendy7756/FollowNet/issues)
- **Email**: contact@follownet.com
- **Documentation**: Check our [Wiki](https://github.com/wendy7756/FollowNet/wiki) for detailed guides

---

**⭐ Star this repository if you find it useful! Your support helps us continue developing new platform integrations.**
