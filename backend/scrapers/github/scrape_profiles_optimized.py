import asyncio
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Browser, BrowserContext
import aiofiles
import time

class OptimizedGitHubProfileScraper:
    """Optimized GitHub Profile Scraper with concurrent processing"""
    
    def __init__(self, max_concurrent: int = 10, timeout: int = 15000):
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.browser_pool: List[Browser] = []
        self.context_pool: List[BrowserContext] = []
        
    async def init_browser_pool(self, pool_size: int = 3):
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
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1280, 'height': 720}
            )
            
            self.browser_pool.append(browser)
            self.context_pool.append(context)
            
    async def close_browser_pool(self):
        """Clean up browser pool"""
        for context in self.context_pool:
            await context.close()
        for browser in self.browser_pool:
            await browser.close()
            
    async def get_context(self) -> BrowserContext:
        """Get available browser context from pool"""
        if not self.context_pool:
            await self.init_browser_pool()
        return self.context_pool[len(self.context_pool) % len(self.context_pool)]
    
    async def scrape_user_profile_concurrent(self, username: str, original_data: Dict) -> Optional[Dict]:
        """Scrape single user profile with concurrency control"""
        async with self.semaphore:
            context = await self.get_context()
            page = await context.new_page()
            
            try:
                profile_url = f"https://github.com/{username}"
                
                # Faster page load with reduced timeout
                await page.goto(profile_url, wait_until="domcontentloaded", timeout=self.timeout)
                
                # Quick check if profile exists
                try:
                    await page.wait_for_selector('.js-profile-editable-area', timeout=3000)
                except:
                    print(f"❌ Profile not found or private: {username}")
                    return None
                
                # Extract data with optimized selectors
                user_data = {
                    'username': username,
                    'profile_url': profile_url,
                    'platform': 'github',
                    'type': original_data.get('type', 'follower'),
                    'scraped_at': datetime.now().isoformat()
                }
                
                # Parallel data extraction using Promise.all equivalent
                tasks = [
                    self._extract_display_name(page),
                    self._extract_bio(page),
                    self._extract_avatar(page, username),
                    self._extract_stats(page),
                    self._extract_contact_info(page)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Merge results
                for result in results:
                    if isinstance(result, dict):
                        user_data.update(result)
                
                return user_data
                
            except Exception as e:
                print(f"❌ Error scraping {username}: {e}")
                return None
            finally:
                await page.close()
    
    async def _extract_display_name(self, page) -> Dict:
        """Extract display name"""
        try:
            selectors = [
                '.js-profile-editable-area .p-name',
                '.js-profile-editable-area h1 span',
                '.js-profile-editable-area h1'
            ]
            
            for selector in selectors:
                element = await page.query_selector(selector)
                if element:
                    display_name = await element.text_content()
                    if display_name and display_name.strip():
                        return {'display_name': display_name.strip()}
            
            return {'display_name': ''}
        except:
            return {'display_name': ''}
    
    async def _extract_bio(self, page) -> Dict:
        """Extract bio"""
        try:
            bio_element = await page.query_selector('.js-profile-editable-area .p-note')
            if bio_element:
                bio = await bio_element.text_content()
                return {'bio': bio.strip() if bio else ''}
            return {'bio': ''}
        except:
            return {'bio': ''}
    
    async def _extract_avatar(self, page, username: str) -> Dict:
        """Extract avatar URL"""
        try:
            avatar_element = await page.query_selector('.js-profile-editable-area img.avatar')
            if avatar_element:
                avatar_url = await avatar_element.get_attribute('src')
                return {'avatar_url': avatar_url or f'https://github.com/{username}.png'}
            return {'avatar_url': f'https://github.com/{username}.png'}
        except:
            return {'avatar_url': f'https://github.com/{username}.png'}
    
    async def _extract_stats(self, page) -> Dict:
        """Extract follower/following counts"""
        try:
            stats = {'follower_count': 0, 'following_count': 0, 'public_repos': 0}
            
            # Get all stat links
            stat_links = await page.query_selector_all('.js-profile-editable-area a')
            
            for link in stat_links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                
                if href and text:
                    text = text.strip().replace(',', '')
                    
                    if 'followers' in href:
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            stats['follower_count'] = int(numbers[0])
                    elif 'following' in href:
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            stats['following_count'] = int(numbers[0])
                    elif 'repositories' in href or 'tab=repositories' in href:
                        import re
                        numbers = re.findall(r'\d+', text)
                        if numbers:
                            stats['public_repos'] = int(numbers[0])
            
            return stats
        except:
            return {'follower_count': 0, 'following_count': 0, 'public_repos': 0}
    
    async def _extract_contact_info(self, page) -> Dict:
        """Extract contact information"""
        try:
            contact_info = {'company': '', 'location': '', 'website': '', 'twitter': '', 'email': ''}
            
            # Company
            company_element = await page.query_selector('.js-profile-editable-area [data-test-selector="profile-company"]')
            if company_element:
                company = await company_element.text_content()
                contact_info['company'] = company.strip() if company else ''
            
            # Location
            location_element = await page.query_selector('.js-profile-editable-area [data-test-selector="profile-location"]')
            if location_element:
                location = await location_element.text_content()
                contact_info['location'] = location.strip() if location else ''
            
            # Website
            website_element = await page.query_selector('.js-profile-editable-area [data-test-selector="profile-website"] a')
            if website_element:
                website = await website_element.get_attribute('href')
                contact_info['website'] = website or ''
            
            # Twitter
            twitter_element = await page.query_selector('.js-profile-editable-area [data-test-selector="profile-twitter"] a')
            if twitter_element:
                twitter = await twitter_element.get_attribute('href')
                contact_info['twitter'] = twitter or ''
            
            return contact_info
        except:
            return {'company': '', 'location': '', 'website': '', 'twitter': '', 'email': ''}
    
    async def scrape_profiles_batch_optimized(self, usernames: List[Dict], batch_size: int = 20):
        """Scrape profiles in optimized batches"""
        start_time = time.time()
        total_users = len(usernames)
        processed_count = 0
        enriched_users = []
        
        print(f"🚀 Starting optimized batch processing for {total_users} users")
        print(f"⚙️ Concurrency: {self.max_concurrent}, Batch size: {batch_size}")
        
        # Initialize browser pool
        await self.init_browser_pool(pool_size=min(3, self.max_concurrent // 3 + 1))
        
        try:
            # Process in batches
            for i in range(0, len(usernames), batch_size):
                batch = usernames[i:i + batch_size]
                batch_start = time.time()
                
                print(f"📦 Processing batch {i//batch_size + 1}: {len(batch)} users")
                
                # Create concurrent tasks for batch
                tasks = [
                    self.scrape_user_profile_concurrent(user_data['username'], user_data)
                    for user_data in batch
                ]
                
                # Execute batch concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for result in results:
                    if isinstance(result, dict) and result:
                        enriched_users.append(result)
                    processed_count += 1
                
                batch_time = time.time() - batch_start
                avg_time_per_user = batch_time / len(batch)
                
                print(f"✅ Batch completed in {batch_time:.2f}s (avg: {avg_time_per_user:.2f}s/user)")
                print(f"📊 Progress: {processed_count}/{total_users} ({processed_count/total_users*100:.1f}%)")
                
                # Small delay between batches to be respectful
                if i + batch_size < len(usernames):
                    await asyncio.sleep(0.5)
        
        finally:
            await self.close_browser_pool()
        
        total_time = time.time() - start_time
        print(f"🎉 Completed! {len(enriched_users)}/{total_users} profiles scraped in {total_time:.2f}s")
        print(f"⚡ Average speed: {total_time/total_users:.2f}s per user")
        
        return enriched_users

    async def read_usernames_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """Read usernames from CSV file"""
        usernames = []
        try:
            async with aiofiles.open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                content = await csvfile.read()
                lines = content.strip().split('\n')
                
                if len(lines) <= 1:
                    return []
                
                # Parse header
                header = lines[0].split(',')
                username_index = header.index('username') if 'username' in header else 0
                
                # Parse data rows
                for line in lines[1:]:
                    if line.strip():
                        fields = line.split(',')
                        if len(fields) > username_index:
                            usernames.append({
                                'username': fields[username_index].strip('"'),
                                'type': fields[header.index('type')] if 'type' in header else 'follower'
                            })
        except Exception as e:
            print(f"Error reading CSV file: {e}")
        
        return usernames

    async def save_enriched_csv(self, users: List[Dict[str, Any]], original_csv_path: str) -> str:
        """Save enriched data to CSV file"""
        if not users:
            return ""
        
        # Generate output filename
        base_name = os.path.splitext(original_csv_path)[0]
        output_file = base_name.replace('_raw', '_enriched_optimized') + '.csv'
        
        # Standard fieldnames
        fieldnames = [
            'username', 'display_name', 'bio', 'avatar_url', 'profile_url',
            'platform', 'type', 'follower_count', 'following_count', 'public_repos',
            'company', 'location', 'website', 'twitter', 'email', 'scraped_at'
        ]
        
        try:
            async with aiofiles.open(output_file, 'w', encoding='utf-8') as csvfile:
                # Write header
                await csvfile.write(','.join(fieldnames) + '\n')
                
                # Write data rows
                for user in users:
                    row = []
                    for field in fieldnames:
                        value = str(user.get(field, ''))
                        # Escape commas and quotes
                        if ',' in value or '"' in value:
                            value = f'"{value.replace("""", """""")}"'
                        row.append(value)
                    await csvfile.write(','.join(row) + '\n')
            
            print(f"✅ Enriched data saved to: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"Error saving enriched CSV: {e}")
            return ""

# Performance comparison function
async def compare_performance():
    """Compare performance between original and optimized scrapers"""
    print("🔬 Performance Comparison Test")
    print("=" * 50)
    
    # Test data
    test_usernames = [
        {'username': 'octocat', 'type': 'follower'},
        {'username': 'torvalds', 'type': 'follower'},
        {'username': 'gaearon', 'type': 'follower'},
        {'username': 'sindresorhus', 'type': 'follower'},
        {'username': 'tj', 'type': 'follower'}
    ]
    
    # Test optimized scraper
    optimized_scraper = OptimizedGitHubProfileScraper(max_concurrent=5)
    
    print("🚀 Testing Optimized Scraper...")
    start_time = time.time()
    optimized_results = await optimized_scraper.scrape_profiles_batch_optimized(test_usernames, batch_size=5)
    optimized_time = time.time() - start_time
    
    print(f"\n📊 Results:")
    print(f"Optimized: {len(optimized_results)} users in {optimized_time:.2f}s ({optimized_time/len(test_usernames):.2f}s per user)")
    
    return optimized_results

if __name__ == "__main__":
    asyncio.run(compare_performance()) 