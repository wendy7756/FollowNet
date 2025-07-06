"""
Performance optimization configurations for FollowNet scrapers
"""

# Browser optimization settings
BROWSER_ARGS = [
    '--disable-blink-features=AutomationControlled',
    '--disable-dev-shm-usage',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-gpu',
    '--disable-web-security',
    '--disable-features=VizDisplayCompositor',
    '--disable-background-timer-throttling',
    '--disable-backgrounding-occluded-windows',
    '--disable-renderer-backgrounding',
    '--disable-field-trial-config',
    '--disable-back-forward-cache',
    '--disable-ipc-flooding-protection'
]

# Network optimization
OPTIMIZED_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}

# Performance settings
PERFORMANCE_CONFIG = {
    # Stage 1 optimizations
    'stage1': {
        'timeout': 15000,  # Reduced from 30000ms
        'wait_between_pages': 0.3,  # Reduced from 1s
        'wait_for_load': 'domcontentloaded',  # Faster than 'networkidle'
        'disable_images': True,
        'disable_css': True,
        'max_concurrent_pages': 1  # Sequential for stability
    },
    
    # Stage 2 optimizations
    'stage2': {
        'timeout': 10000,  # Reduced from 30000ms
        'max_concurrent_users': 15,  # Increased from 5
        'batch_size': 25,  # Increased from 5
        'browser_pool_size': 3,
        'wait_between_batches': 0.5,  # Reduced from 2s
        'retry_attempts': 2,
        'disable_images': True,
        'disable_css': True
    },
    
    # Resource blocking patterns
    'block_resources': [
        '**/*.{png,jpg,jpeg,gif,svg,webp,ico}',  # Images
        '**/*.{css,scss,sass,less}',  # Stylesheets
        '**/*.{woff,woff2,ttf,eot}',  # Fonts
        '**/*.{mp4,mp3,avi,mov,wmv}',  # Media
        '**/analytics.js',  # Analytics
        '**/gtag.js',  # Google Analytics
        '**/ga.js',  # Google Analytics
        '**/ads*.js',  # Advertisements
        '**/tracking*.js'  # Tracking scripts
    ]
}

# Selectors optimization (most reliable selectors first)
OPTIMIZED_SELECTORS = {
    'followers_count': [
        'a[href$="tab=followers"] .text-bold',
        'a[href*="followers"] .Counter',
        'a[href*="followers"] span'
    ],
    'user_links': [
        'a[data-hovercard-type="user"]'
    ],
    'pagination': [
        '.pagination a[rel="next"]',
        '.pagination a:last-child',
        '.pagination a'
    ],
    'profile_elements': {
        'display_name': [
            '.js-profile-editable-area .p-name',
            '.js-profile-editable-area h1 span',
            '.js-profile-editable-area h1'
        ],
        'bio': [
            '.js-profile-editable-area .p-note'
        ],
        'avatar': [
            '.js-profile-editable-area img.avatar',
            '.js-profile-editable-area .avatar img'
        ],
        'stats_links': [
            '.js-profile-editable-area a'
        ]
    }
}

# Speed benchmarks (for comparison)
SPEED_BENCHMARKS = {
    'stage1_target_speed': 25,  # users per second
    'stage2_target_speed': 8,   # users per second
    'total_target_speed': 5     # users per second (combined)
}

# Memory optimization
MEMORY_CONFIG = {
    'max_browser_instances': 3,
    'max_contexts_per_browser': 5,
    'cleanup_interval': 50,  # Clean up every N users
    'gc_threshold': 100      # Force garbage collection every N users
} 