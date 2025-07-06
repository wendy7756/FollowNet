import asyncio
import csv
import os
import random
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
import gc

class UnlimitedGitHubFollowersScraper:
    """
    Unlimited GitHub Followers Scraper
    Can scrape more than 250 followers with intelligent performance optimization
    """
    
    def __init__(self, max_concurrent: int = 20, batch_size: int = 50):
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Performance settings
        self.browser_pool: List[Browser] = []
        self.context_pool: List[BrowserContext] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
        # Anti-bot measures
        self.user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
        ]
        
    async def scrape_unlimited_followers(self, username: str, max_users: int = 1000, auto_scale: bool = True):
        """
        Scrape unlimited followers with intelligent scaling
        
        Args:
            username: GitHub username
            max_users: Maximum number of users to scrape (0 = unlimited)
            auto_scale: Automatically adjust based on total followers
        """
        print(f"🚀 Starting unlimited followers scraping for {username}")
        print(f"📊 Target: {max_users} users (auto_scale: {auto_scale})")
        
        start_time = time.time()
        
        # Step 1: Get total followers count
        total_followers = await self._get_total_followers(username)
        print(f"📈 Total followers found: {total_followers}")
        
        # Step 2: Calculate intelligent scraping strategy
        scraping_strategy = self._calculate_scraping_strategy(total_followers, max_users, auto_scale)
        print(f"🎯 Scraping strategy: {scraping_strategy}")
        
        # Step 3: Initialize browser pool
        await self._init_browser_pool(pool_size=min(3, self.max_concurrent // 10 + 1))
        
        try:
            # Step 4: Scrape followers list (Stage 1)
            followers_data = await self._scrape_followers_unlimited(
                username, 
                scraping_strategy['target_pages'],
                scraping_strategy['target_users']
            )
            
            if not followers_data:
                print("❌ No followers data obtained")
                return {
                    'csv_file': '',
                    'total_followers': total_followers,
                    'scraped_followers': 0,
                    'total_pages': 0,
                    'performance_stats': {}
                }
            
            # Step 5: Save Stage 1 results
            stage1_csv = await self._save_followers_csv(followers_data, f"{username}_unlimited_followers_raw.csv")
            
            # Step 6: Scrape detailed profiles (Stage 2)
            if scraping_strategy['enable_stage2']:
                detailed_data = await self._scrape_profiles_unlimited(followers_data)
                stage2_csv = await self._save_profiles_csv(detailed_data, f"{username}_unlimited_followers_enriched.csv")
            else:
                detailed_data = []
                stage2_csv = ""
            
            # Step 7: Performance statistics
            total_time = time.time() - start_time
            performance_stats = {
                'total_time': total_time,
                'stage1_users': len(followers_data),
                'stage2_users': len(detailed_data),
                'users_per_second': len(followers_data) / total_time if total_time > 0 else 0,
                'strategy_used': scraping_strategy['name'],
                'optimization_enabled': True
            }
            
            print(f"🎉 Scraping complete! {len(followers_data)} followers in {total_time:.1f}s")
            print(f"⚡ Speed: {performance_stats['users_per_second']:.1f} users/second")
            
            return {
                'csv_file': stage1_csv,
                'enriched_csv': stage2_csv,
                'total_followers': total_followers,
                'scraped_followers': len(followers_data),
                'total_pages': scraping_strategy['target_pages'],
                'performance_stats': performance_stats,
                'detailed_data': detailed_data
            }
            
        finally:
            await self._cleanup_browser_pool()
    
    async def _get_total_followers(self, username: str) -> int:
        """Get total followers count from profile page"""
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            profile_url = f"https://github.com/{username}"
            await page.goto(profile_url, wait_until="domcontentloaded", timeout=15000)
            
            # Try multiple selectors for followers count
            selectors = [
                'a[href$="tab=followers"] .text-bold',
                'a[href*="followers"] .Counter',
                'a[href*="followers"] span'
            ]
            
            for selector in selectors:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        text = await element.text_content()
                        if text and text.strip():
                            return self._parse_followers_count(text.strip())
                except:
                    continue
            
            return 0
            
        except Exception as e:
            print(f"Error getting total followers: {e}")
            return 0
        finally:
            await browser.close()
            await playwright.stop()
    
    def _parse_followers_count(self, count_str: str) -> int:
        """Parse followers count string (e.g., '1.2k' -> 1200)"""
        count_str = count_str.replace(',', '').strip()
        if 'k' in count_str.lower():
            return int(float(count_str.lower().replace('k', '')) * 1000)
        elif 'm' in count_str.lower():
            return int(float(count_str.lower().replace('m', '')) * 1000000)
        else:
            try:
                return int(count_str)
            except:
                return 0
    
    def _calculate_scraping_strategy(self, total_followers: int, max_users: int, auto_scale: bool) -> Dict:
        """Calculate intelligent scraping strategy based on followers count"""
        
        if auto_scale:
            if total_followers <= 500:
                # Small users: scrape all
                target_users = min(total_followers, max_users) if max_users > 0 else total_followers
                strategy_name = "Small Scale (All followers)"
            elif total_followers <= 2000:
                # Medium users: scrape up to 1000
                target_users = min(1000, max_users) if max_users > 0 else 1000
                strategy_name = "Medium Scale (1000 followers)"
            elif total_followers <= 10000:
                # Large users: scrape up to 2000
                target_users = min(2000, max_users) if max_users > 0 else 2000
                strategy_name = "Large Scale (2000 followers)"
            else:
                # Huge users: scrape up to 2500
                target_users = min(2500, max_users) if max_users > 0 else 2500
                strategy_name = "Huge Scale (2500 followers)"
        else:
            # Manual mode: use specified max_users
            target_users = max_users if max_users > 0 else min(1000, total_followers)
            strategy_name = f"Manual ({target_users} followers)"
        
        target_pages = (target_users + 49) // 50  # 50 users per page
        
        return {
            'name': strategy_name,
            'target_users': target_users,
            'target_pages': target_pages,
            'enable_stage2': target_users <= 1000,  # Only enable detailed scraping for <= 1000 users
            'batch_size': min(20, target_pages),  # Process in batches
            'delay_range': (0.5, 2.0) if total_followers > 5000 else (0.3, 1.0)
        }
    
    async def _init_browser_pool(self, pool_size: int = 3):
        """Initialize browser pool for concurrent processing"""
        playwright = await async_playwright().start()
        
        for i in range(pool_size):
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            
            context = await browser.new_context(
                user_agent=random.choice(self.user_agents),
                viewport={'width': 1280, 'height': 720}
            )
            
            self.browser_pool.append(browser)
            self.context_pool.append(context)
    
    async def _cleanup_browser_pool(self):
        """Clean up browser pool"""
        for context in self.context_pool:
            await context.close()
        for browser in self.browser_pool:
            await browser.close()
        self.browser_pool.clear()
        self.context_pool.clear()
        
        # Force garbage collection
        gc.collect()
    
    async def _scrape_followers_unlimited(self, username: str, target_pages: int, target_users: int) -> List[Dict]:
        """Scrape followers list with unlimited pages"""
        print(f"📄 Starting Stage 1: Scraping {target_pages} pages ({target_users} users)")
        
        all_followers = []
        seen_usernames = set()
        
        # Process in batches to manage memory
        batch_size = min(20, target_pages)
        
        for batch_start in range(0, target_pages, batch_size):
            batch_end = min(batch_start + batch_size, target_pages)
            batch_pages = list(range(batch_start + 1, batch_end + 1))
            
            print(f"📦 Processing batch: pages {batch_start + 1}-{batch_end}")
            
            # Process batch of pages
            batch_followers = await self._scrape_pages_batch(username, batch_pages, seen_usernames)
            all_followers.extend(batch_followers)
            
            # Update seen usernames
            for follower in batch_followers:
                seen_usernames.add(follower['username'])
            
            # Check if we've reached target users
            if len(all_followers) >= target_users:
                all_followers = all_followers[:target_users]
                break
            
            # Smart delay between batches
            await asyncio.sleep(random.uniform(1.0, 3.0))
            
            # Memory management
            if len(all_followers) % 500 == 0:
                gc.collect()
        
        print(f"✅ Stage 1 complete: {len(all_followers)} followers scraped")
        return all_followers
    
    async def _scrape_pages_batch(self, username: str, pages: List[int], seen_usernames: set) -> List[Dict]:
        """Scrape a batch of pages concurrently"""
        semaphore = asyncio.Semaphore(5)  # Limit concurrent pages
        
        async def scrape_single_page(page_num: int) -> List[Dict]:
            async with semaphore:
                return await self._scrape_single_page(username, page_num, seen_usernames)
        
        # Create tasks for all pages in batch
        tasks = [scrape_single_page(page_num) for page_num in pages]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        batch_followers = []
        for result in results:
            if isinstance(result, list):
                batch_followers.extend(result)
            elif isinstance(result, Exception):
                print(f"Page scraping error: {result}")
        
        return batch_followers
    
    async def _scrape_single_page(self, username: str, page_num: int, seen_usernames: set) -> List[Dict]:
        """Scrape a single page of followers"""
        if not self.context_pool:
            return []
        
        context = self.context_pool[page_num % len(self.context_pool)]
        page = await context.new_page()
        
        try:
            # Block resources for faster loading
            await page.route('**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}', lambda route: route.abort())
            
            url = f"https://github.com/{username}?page={page_num}&tab=followers"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            
            # Wait for user links
            try:
                await page.wait_for_selector('a[data-hovercard-type="user"]', timeout=5000)
            except:
                return []
            
            # Extract user links
            user_links = await page.query_selector_all('a[data-hovercard-type="user"]')
            
            page_followers = []
            for link in user_links:
                try:
                    href = await link.get_attribute('href')
                    if href and href.startswith('/'):
                        follower_username = href.strip('/')
                        if follower_username and follower_username not in seen_usernames:
                            page_followers.append({
                                'username': follower_username,
                                'profile_url': f'https://github.com/{follower_username}',
                                'type': 'follower',
                                'source_user': username,
                                'page_number': page_num,
                                'scraped_at': datetime.now().isoformat()
                            })
                except Exception as e:
                    continue
            
            # Random delay to avoid rate limiting
            await asyncio.sleep(random.uniform(0.3, 1.0))
            
            return page_followers
            
        except Exception as e:
            print(f"Error scraping page {page_num}: {e}")
            return []
        finally:
            await page.close()
    
    async def _scrape_profiles_unlimited(self, followers_data: List[Dict]) -> List[Dict]:
        """Scrape detailed profiles with high concurrency"""
        print(f"👥 Starting Stage 2: Scraping {len(followers_data)} profiles")
        
        if len(followers_data) > 1000:
            print("⚠️ Large dataset detected, using sampling strategy")
            # For very large datasets, sample intelligently
            followers_data = self._sample_followers(followers_data, 1000)
        
        # Process in large batches
        batch_size = 50
        all_profiles = []
        
        for i in range(0, len(followers_data), batch_size):
            batch = followers_data[i:i + batch_size]
            print(f"📦 Processing profile batch {i//batch_size + 1}: {len(batch)} users")
            
            # Process batch concurrently
            batch_profiles = await self._scrape_profiles_batch(batch)
            all_profiles.extend(batch_profiles)
            
            # Progress update
            progress = (i + len(batch)) / len(followers_data) * 100
            print(f"📊 Progress: {progress:.1f}% ({len(all_profiles)} profiles completed)")
            
            # Small delay between batches
            await asyncio.sleep(0.5)
        
        print(f"✅ Stage 2 complete: {len(all_profiles)} profiles scraped")
        return all_profiles
    
    def _sample_followers(self, followers_data: List[Dict], target_count: int) -> List[Dict]:
        """Intelligently sample followers for large datasets"""
        if len(followers_data) <= target_count:
            return followers_data
        
        # Take first 50% from early pages (more active users)
        early_count = target_count // 2
        early_followers = followers_data[:early_count]
        
        # Sample remaining from the rest
        remaining_count = target_count - early_count
        remaining_followers = random.sample(followers_data[early_count:], remaining_count)
        
        return early_followers + remaining_followers
    
    async def _scrape_profiles_batch(self, batch: List[Dict]) -> List[Dict]:
        """Scrape a batch of profiles concurrently"""
        
        async def scrape_single_profile(follower_data: Dict) -> Optional[Dict]:
            async with self.semaphore:
                return await self._scrape_single_profile(follower_data)
        
        # Create tasks for all profiles in batch
        tasks = [scrape_single_profile(follower) for follower in batch]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect successful results
        profiles = []
        for result in results:
            if isinstance(result, dict) and result:
                profiles.append(result)
        
        return profiles
    
    async def _scrape_single_profile(self, follower_data: Dict) -> Optional[Dict]:
        """Scrape a single user profile"""
        if not self.context_pool:
            return None
        
        context = random.choice(self.context_pool)
        page = await context.new_page()
        
        try:
            username = follower_data['username']
            profile_url = f"https://github.com/{username}"
            
            # Block resources
            await page.route('**/*.{png,jpg,jpeg,gif,svg,css}', lambda route: route.abort())
            
            await page.goto(profile_url, wait_until="domcontentloaded", timeout=10000)
            
            # Quick profile check
            try:
                await page.wait_for_selector('.js-profile-editable-area', timeout=3000)
            except:
                return None
            
            # Extract profile data
            profile_data = {
                'username': username,
                'profile_url': profile_url,
                'platform': 'github',
                'type': follower_data.get('type', 'follower'),
                'scraped_at': datetime.now().isoformat(),
                'display_name': await self._extract_display_name(page),
                'bio': await self._extract_bio(page),
                'avatar_url': await self._extract_avatar(page, username),
                'follower_count': 0,
                'following_count': 0,
                'public_repos': 0,
                'company': '',
                'location': '',
                'website': '',
                'twitter': ''
            }
            
            # Extract additional data (quick version)
            await self._extract_quick_stats(page, profile_data)
            
            return profile_data
            
        except Exception as e:
            return None
        finally:
            await page.close()
    
    async def _extract_display_name(self, page: Page) -> str:
        """Extract display name"""
        try:
            selectors = ['.js-profile-editable-area .p-name', '.js-profile-editable-area h1']
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    name = await element.text_content()
                    if name and name.strip():
                        return name.strip()
        except:
            pass
        return ''
    
    async def _extract_bio(self, page: Page) -> str:
        """Extract bio"""
        try:
            element = await page.query_selector('.js-profile-editable-area .p-note')
            if element:
                bio = await element.text_content()
                return bio.strip() if bio else ''
        except:
            pass
        return ''
    
    async def _extract_avatar(self, page: Page, username: str) -> str:
        """Extract avatar URL"""
        try:
            element = await page.query_selector('.js-profile-editable-area img.avatar')
            if element:
                avatar_url = await element.get_attribute('src')
                return avatar_url or f'https://github.com/{username}.png'
        except:
            pass
        return f'https://github.com/{username}.png'
    
    async def _extract_quick_stats(self, page: Page, profile_data: Dict):
        """Extract quick stats (followers, following, repos)"""
        try:
            links = await page.query_selector_all('.js-profile-editable-area a')
            for link in links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                if href and text:
                    import re
                    numbers = re.findall(r'\d+', text.replace(',', ''))
                    if numbers:
                        count = int(numbers[0])
                        if 'followers' in href:
                            profile_data['follower_count'] = count
                        elif 'following' in href:
                            profile_data['following_count'] = count
                        elif 'repositories' in href:
                            profile_data['public_repos'] = count
        except:
            pass
    
    async def _save_followers_csv(self, followers_data: List[Dict], filename: str) -> str:
        """Save followers data to CSV"""
        if not followers_data:
            return ""
        
        csv_file_path = os.path.join(self.data_dir, filename)
        
        try:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = followers_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(followers_data)
            return csv_file_path
        except Exception as e:
            print(f"Error saving followers CSV: {e}")
            return ""
    
    async def _save_profiles_csv(self, profiles_data: List[Dict], filename: str) -> str:
        """Save profiles data to CSV"""
        if not profiles_data:
            return ""
        
        csv_file_path = os.path.join(self.data_dir, filename)
        
        try:
            fieldnames = [
                'username', 'display_name', 'bio', 'avatar_url', 'profile_url',
                'platform', 'type', 'follower_count', 'following_count', 'public_repos',
                'company', 'location', 'website', 'twitter', 'scraped_at'
            ]
            
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(profiles_data)
            return csv_file_path
        except Exception as e:
            print(f"Error saving profiles CSV: {e}")
            return ""

# Test function
async def test_unlimited_scraper():
    """Test the unlimited scraper"""
    scraper = UnlimitedGitHubFollowersScraper(max_concurrent=20)
    
    # Test with octocat (has many followers)
    result = await scraper.scrape_unlimited_followers(
        username="octocat",
        max_users=500,  # Scrape 500 users
        auto_scale=True
    )
    
    print(f"\n📊 Test Results:")
    print(f"Total followers: {result['total_followers']}")
    print(f"Scraped followers: {result['scraped_followers']}")
    print(f"CSV file: {result['csv_file']}")
    print(f"Performance: {result['performance_stats']}")

if __name__ == "__main__":
    asyncio.run(test_unlimited_scraper()) 