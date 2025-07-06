import asyncio
import csv
import os
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import async_playwright
import time

class OptimizedGitHubFollowersListScraper:
    """Optimized GitHub Stage 1: Fast batch scraping of followers/stargazers username lists"""
    
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def scrape_followers_list_optimized(self, username: str, max_pages: int = 10) -> Dict[str, Any]:
        """
        Optimized scrape user's followers list with performance improvements
        
        Args:
            username: GitHub username
            max_pages: Maximum pages to scrape
            
        Returns:
            Dict containing CSV file path, total_followers, and total_pages
        """
        print(f"🚀 Stage 1 (Optimized): Starting to scrape followers list for {username}...")
        start_time = time.time()
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-gpu',
                '--disable-web-security'
            ]
        )
        page = await browser.new_page()
        
        # Optimized headers and settings
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        
        # Disable images and CSS for faster loading
        await page.route('**/*.{png,jpg,jpeg,gif,svg,css,woff,woff2}', lambda route: route.abort())
        
        followers = []
        total_followers = 0
        
        try:
            # First, get total followers count from profile page (optimized)
            if max_pages > 0:
                profile_url = f"https://github.com/{username}"
                print(f"📊 Getting total followers count from: {profile_url}")
                
                await page.goto(profile_url, wait_until="domcontentloaded", timeout=15000)
                
                # Quick wait for essential elements
                try:
                    await page.wait_for_selector('.js-profile-editable-area', timeout=5000)
                except:
                    print("⚠️ Profile area not found quickly, continuing...")
                
                # Try to find followers count with optimized selectors
                followers_selectors = [
                    'a[href$="tab=followers"] .text-bold',
                    'a[href*="followers"] .Counter',
                    'a[href*="followers"] span'
                ]
                
                for selector in followers_selectors:
                    try:
                        followers_element = await page.query_selector(selector)
                        if followers_element:
                            followers_text = await followers_element.text_content()
                            if followers_text and followers_text.strip():
                                # Parse followers count (handle "1.2k" format)
                                followers_text = followers_text.strip().replace(',', '')
                                if 'k' in followers_text.lower():
                                    total_followers = int(float(followers_text.lower().replace('k', '')) * 1000)
                                elif 'm' in followers_text.lower():
                                    total_followers = int(float(followers_text.lower().replace('m', '')) * 1000000)
                                else:
                                    total_followers = int(followers_text)
                                print(f"📊 Total followers found: {total_followers}")
                                break
                    except Exception as e:
                        continue
            
            # Optimized pagination scraping
            for page_num in range(1, max_pages + 1):
                page_start_time = time.time()
                
                # GitHub followers pagination URL format
                url = f"https://github.com/{username}?page={page_num}&tab=followers"
                print(f"📄 Scraping page {page_num}: {url}")
                
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                # Quick check for user links
                try:
                    await page.wait_for_selector('a[data-hovercard-type="user"]', timeout=3000)
                except:
                    print(f"⚠️ No user links found on page {page_num}, stopping")
                    break
                
                # Get user links on current page
                user_links = await page.query_selector_all('a[data-hovercard-type="user"]')
                
                if not user_links:
                    print(f"Page {page_num} has no user links found, stopping scrape")
                    break
                
                page_followers = []
                seen_usernames = set()
                
                # Optimized link processing
                for link in user_links:
                    try:
                        href = await link.get_attribute('href')
                        if href and href.startswith('/'):
                            follower_username = href.strip('/')
                            if follower_username and follower_username not in seen_usernames:
                                seen_usernames.add(follower_username)
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
                
                page_time = time.time() - page_start_time
                print(f"📦 Page {page_num} found {len(page_followers)} followers in {page_time:.2f}s")
                followers.extend(page_followers)
                
                # Quick next page check (optimized)
                has_next_page = False
                try:
                    # Check for pagination buttons
                    pagination = await page.query_selector('.pagination')
                    if pagination:
                        next_links = await pagination.query_selector_all('a')
                        for next_link in next_links:
                            href = await next_link.get_attribute('href')
                            if href and f'page={page_num + 1}' in href:
                                has_next_page = True
                                break
                except:
                    pass
                
                if not has_next_page:
                    print(f"No next page found, scraped {page_num} pages in total")
                    break
                
                # Minimal delay between pages
                await asyncio.sleep(0.3)
            
            # Save to CSV file (even if empty, create a file)
            if len(followers) == 0:
                # Create empty CSV file for consistency
                csv_file = await self._save_empty_csv(f"{username}_followers_raw.csv")
                print(f"⚠️ No followers found for {username}, created empty CSV file: {csv_file}")
            else:
                csv_file = await self._save_to_csv(followers, f"{username}_followers_raw.csv")
                
            # Calculate total pages
            total_pages = (total_followers + 49) // 50 if total_followers > 0 else 1
            
            total_time = time.time() - start_time
            print(f"✅ Stage 1 complete! Total {len(followers)} followers obtained in {total_time:.2f}s")
            print(f"📊 Total followers: {total_followers}, Total pages: {total_pages}")
            print(f"⚡ Speed: {len(followers)/total_time:.1f} users/second")
            
            return {
                "csv_file": csv_file,
                "total_followers": total_followers,
                "total_pages": total_pages,
                "scraped_followers": len(followers)
            }
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return {
                "csv_file": "",
                "total_followers": 0,
                "total_pages": 1,
                "scraped_followers": 0
            }
        finally:
            await browser.close()
            await playwright.stop()
    
    async def scrape_stargazers_list_optimized(self, owner: str, repo: str, max_pages: int = 10) -> str:
        """
        Optimized scrape repository's stargazers list
        
        Args:
            owner: Repository owner
            repo: Repository name
            max_pages: Maximum pages to scrape
            
        Returns:
            CSV file path
        """
        print(f"🚀 Stage 1 (Optimized): Starting to scrape stargazers list for {owner}/{repo}...")
        start_time = time.time()
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox']
        )
        page = await browser.new_page()
        
        # Disable images for faster loading
        await page.route('**/*.{png,jpg,jpeg,gif,svg}', lambda route: route.abort())
        
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        stargazers = []
        
        try:
            for page_num in range(1, max_pages + 1):
                # GitHub stargazers pagination URL format
                url = f"https://github.com/{owner}/{repo}/stargazers?page={page_num}"
                print(f"📄 Scraping page {page_num}: {url}")
                
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                
                # Quick wait for user links
                try:
                    await page.wait_for_selector('a[data-hovercard-type="user"]', timeout=3000)
                except:
                    print(f"No user links found on page {page_num}, stopping")
                    break
                
                # Get user links on current page
                user_links = await page.query_selector_all('a[data-hovercard-type="user"]')
                
                if not user_links:
                    print(f"Page {page_num} has no user links found, stopping scrape")
                    break
                
                page_stargazers = []
                seen_usernames = set()
                
                for link in user_links:
                    try:
                        href = await link.get_attribute('href')
                        if href and href.startswith('/'):
                            stargazer_username = href.strip('/')
                            if stargazer_username and stargazer_username not in seen_usernames:
                                seen_usernames.add(stargazer_username)
                                page_stargazers.append({
                                    'username': stargazer_username,
                                    'profile_url': f'https://github.com/{stargazer_username}',
                                    'type': 'stargazer',
                                    'source_repo': f'{owner}/{repo}',
                                    'page_number': page_num,
                                    'scraped_at': datetime.now().isoformat()
                                })
                    except Exception as e:
                        continue
                
                print(f"Page {page_num} found {len(page_stargazers)} stargazers")
                stargazers.extend(page_stargazers)
                
                # Quick next page check
                has_next_page = False
                try:
                    pagination = await page.query_selector('.pagination')
                    if pagination:
                        next_links = await pagination.query_selector_all('a')
                        for next_link in next_links:
                            href = await next_link.get_attribute('href')
                            if href and f'page={page_num + 1}' in href:
                                has_next_page = True
                                break
                except:
                    pass
                
                if not has_next_page:
                    print(f"No next page found, scraped {page_num} pages in total")
                    break
                
                # Minimal delay
                await asyncio.sleep(0.3)
            
            # Save to CSV file
            csv_file = await self._save_to_csv(stargazers, f"{owner}_{repo}_stargazers_raw.csv")
            
            total_time = time.time() - start_time
            print(f"✅ Stage 1 complete! Total {len(stargazers)} stargazers obtained in {total_time:.2f}s")
            print(f"⚡ Speed: {len(stargazers)/total_time:.1f} users/second")
            
            return csv_file
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            return ""
        finally:
            await browser.close()
            await playwright.stop()
    
    async def _save_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """Save data to CSV file"""
        if not data:
            return ""
        
        csv_file_path = os.path.join(self.data_dir, filename)
        
        try:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                if data:
                    fieldnames = data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(data)
            
            return csv_file_path
        except Exception as e:
            print(f"Error saving CSV file: {e}")
            return ""
    
    async def _save_empty_csv(self, filename: str) -> str:
        """Create empty CSV file with headers"""
        csv_file_path = os.path.join(self.data_dir, filename)
        
        try:
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['username', 'profile_url', 'type', 'source_user', 'page_number', 'scraped_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
            
            return csv_file_path
        except Exception as e:
            print(f"Error creating empty CSV file: {e}")
            return ""

# Performance test
async def test_optimized_performance():
    """Test the optimized scraper performance"""
    scraper = OptimizedGitHubFollowersListScraper()
    
    print("🔬 Testing Optimized Stage 1 Performance")
    print("=" * 50)
    
    # Test with a user that has followers
    result = await scraper.scrape_followers_list_optimized("octocat", max_pages=2)
    
    print(f"\n📊 Results:")
    print(f"CSV file: {result['csv_file']}")
    print(f"Total followers: {result['total_followers']}")
    print(f"Scraped followers: {result['scraped_followers']}")
    print(f"Total pages: {result['total_pages']}")

if __name__ == "__main__":
    asyncio.run(test_optimized_performance()) 