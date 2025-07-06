/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    unoptimized: true,
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: process.env.NODE_ENV === 'production' 
          ? 'https://follownet.onrender.com/api/:path*'
          : 'http://localhost:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig; 