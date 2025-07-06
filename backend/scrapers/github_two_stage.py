import asyncio
import os
from typing import List, Dict, Any
from .base import BaseScraper
from .github.get_followers_list import GitHubFollowersListScraper
from .github.scrape_profiles import GitHubProfileScraper
from .performance_config import PERFORMANCE_CONFIG, BROWSER_ARGS, OPTIMIZED_HEADERS
from playwright.async_api import async_playwright
from datetime import datetime
import csv
import re

class GitHubTwoStageScraper(BaseScraper):
    """GitHub两阶段爬取器 - 优化版本"""

    def __init__(self, optimize_performance: bool = True):
        super().__init__()
        self.platform = "github"
        self.stage1_scraper = GitHubFollowersListScraper()
        self.stage2_scraper = GitHubProfileScraper()
        self.optimize_performance = optimize_performance
        self.perf_config = PERFORMANCE_CONFIG if optimize_performance else None

    def get_current_time(self) -> str:
        """获取当前时间的ISO格式字符串"""
        return datetime.now().isoformat()

    async def scrape_with_progress(self, url: str, max_pages: int = 5, max_users: int = 0, unlimited: bool = False):
        """Enhanced scrape method with intelligent mode selection"""
        
        # First, do a quick check to get the actual followers count
        url_parts = url.rstrip('/').split('/')
        actual_followers_count = 0
        
        if len(url_parts) >= 4 and url_parts[3]:
            username = url_parts[3]
            if len(url_parts) == 4:  # User profile
                try:
                    # Quick check to get actual followers count
                    playwright = await async_playwright().start()
                    browser = await playwright.chromium.launch(headless=True)
                    page = await browser.new_page()
                    
                    profile_url = f"https://github.com/{username}"
                    await page.goto(profile_url, wait_until="domcontentloaded", timeout=30000)
                    
                    # Try to get followers count quickly
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
                                    followers_text = followers_text.strip().replace(',', '')
                                    if 'k' in followers_text.lower():
                                        actual_followers_count = int(float(followers_text.lower().replace('k', '')) * 1000)
                                    elif 'm' in followers_text.lower():
                                        actual_followers_count = int(float(followers_text.lower().replace('m', '')) * 1000000)
                                    else:
                                        actual_followers_count = int(followers_text)
                                    break
                        except:
                            continue
                    
                    await browser.close()
                    await playwright.stop()
                except Exception as e:
                    print(f"Quick followers check failed: {e}")
                    actual_followers_count = 0
        
        # Smart mode selection based on actual data size
        if actual_followers_count > 0:
            print(f"📊 Detected {actual_followers_count} followers for this user")
            
            # Auto-adjust pages based on actual followers count
            if actual_followers_count > max_pages * 50:
                recommended_pages = min((actual_followers_count + 49) // 50, 20)  # 最多20页
                print(f"⚠️  User has {actual_followers_count} followers, but max_pages is {max_pages}")
                print(f"📈 Recommending {recommended_pages} pages to get all followers")
                print(f"🚀 Using optimized concurrent mode with {max_pages} pages (will get ~{max_pages * 50} followers)")
            else:
                print(f"🚀 Using optimized concurrent mode for {actual_followers_count} followers")
            
            async for result in self._scrape_with_progress_optimized(url, max_pages):
                yield result
            return
        
        # Default to optimized mode
        print(f"🚀 Using optimized concurrent mode (max_pages: {max_pages})")
        async for result in self._scrape_with_progress_optimized(url, max_pages):
            yield result

    async def _scrape_with_progress_optimized(self, url: str, max_pages: int = 5):
        """
        优化版本的两阶段爬取流程，使用并发处理用户详细信息
        """
        print(f"🚀 开始GitHub两阶段并发爬取: {url}")

        # 发送开始消息
        yield {
            'type': 'progress',
            'stage': 1,
            'message': 'Analyzing URL and preparing to scrape...',
            'progress': 0
        }

        # 分析URL类型
        url_parts = url.rstrip('/').split('/')
        print(f"URL部分: {url_parts}")

        stage1_csv = ""
        calculated_pages = max_pages
        print(f"计算需要爬取 {calculated_pages} 页（最多{max_pages}页）")

        yield {
            'type': 'progress',
            'stage': 1,
            'message': f'Preparing to scrape {calculated_pages} pages of user list...',
            'progress': 5
        }

        if len(url_parts) >= 5 and url_parts[3] and url_parts[4]:
            # 仓库URL: https://github.com/owner/repo
            owner = url_parts[3]
            repo = url_parts[4]
            print(f"识别为仓库页面: {owner}/{repo}")

            yield {
                'type': 'progress',
                'stage': 1,
                'message': f'Scraping stargazers for repository {owner}/{repo}...',
                'progress': 10
            }

            # 第一阶段：获取stargazers列表
            stage1_csv = await self.stage1_scraper.scrape_stargazers_list(owner, repo, calculated_pages)
            total_followers = 0  # stargazers数量暂时设为0，因为没有实现获取总数的功能
            total_pages = 1

        elif len(url_parts) >= 4 and url_parts[3]:
            # 用户URL: https://github.com/username
            username = url_parts[3]
            print(f"识别为用户页面: {username}")

            yield {
                'type': 'progress',
                'stage': 1,
                'message': f'Scraping followers for user {username}...',
                'progress': 10
            }

            # 第一阶段：获取followers列表
            stage1_result = await self.stage1_scraper.scrape_followers_list(username, calculated_pages)
            if isinstance(stage1_result, dict):
                stage1_csv = stage1_result.get("csv_file", "")
                total_followers = stage1_result.get("total_followers", 0)
                total_pages = stage1_result.get("total_pages", 1)
            else:
                stage1_csv = stage1_result or ""
                total_followers = 0
                total_pages = 1

        else:
            yield {
                'type': 'error',
                'message': 'Unable to recognize URL type'
            }
            return

        if not stage1_csv or not os.path.exists(stage1_csv):
            yield {
                'type': 'error',
                'message': 'Stage 1 failed, no user list file generated'
            }
            return

        yield {
            'type': 'progress',
            'stage': 1,
            'message': f'Stage 1 complete, generated file: {os.path.basename(stage1_csv)}',
            'progress': 50,
            'total_followers': total_followers,
            'total_pages': total_pages,
            'current_page': 1
        }

        # 第二阶段：使用并发获取用户详细信息
        has_users_to_process = False
        if os.path.exists(stage1_csv):
            try:
                with open(stage1_csv, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    has_users_to_process = len(lines) > 1
            except Exception as e:
                print(f"Error reading CSV file: {e}")
                has_users_to_process = False

        if has_users_to_process:
            yield {
                'type': 'progress',
                'stage': 2,
                'message': f'Starting Stage 2: Getting detailed info with concurrent processing...',
                'progress': 60
            }

            # 使用优化的并发处理
            async for progress in self._scrape_profiles_concurrent(stage1_csv):
                progress_value = progress.get('progress', 0)
                if isinstance(progress_value, str):
                    progress_value = float(progress_value) if progress_value.replace('.', '').isdigit() else 0
                adjusted_progress = 60 + (progress_value * 0.35)
                yield {
                    'type': 'progress',
                    'stage': 2,
                    'message': progress.get('message', 'Processing user details...'),
                    'progress': min(95, adjusted_progress),
                    'current_user': progress.get('current_user', ''),
                    'processed_count': progress.get('processed_count', 0),
                    'total_count': progress.get('total_count', 0)
                }

            # 读取最终结果
            yield {
                'type': 'progress',
                'stage': 2,
                'message': 'Reading final results...',
                'progress': 95
            }

            final_data = await self._read_enriched_data(stage1_csv.replace('_raw.csv', '_enriched.csv'))
        else:
            yield {
                'type': 'progress',
                'stage': 2,
                'message': 'No users found, skipping detailed scraping...',
                'progress': 95
            }
            final_data = []

        # 确定消息类型
        is_user_followers = len(url_parts) >= 4 and len(url_parts) < 5
        if is_user_followers:
            if total_followers > len(final_data) and len(final_data) >= max_pages * 50:
                message = f'Scraping complete! Found {total_followers} total followers, retrieved detailed info for {len(final_data)} users (limited by max_pages={max_pages}). Consider using Advanced Settings for more results.'
            else:
                message = f'Scraping complete! Found {total_followers} total followers, retrieved detailed info for {len(final_data)} users'
        else:
            message = f'Scraping complete! Retrieved detailed info for {len(final_data)} stargazers'

        yield {
            'type': 'complete',
            'data': final_data,
            'total': len(final_data),
            'message': message,
            'progress': 100,
            'platform': 'github',
            'total_followers': total_followers if is_user_followers else len(final_data),
            'total_pages': total_pages,
            'current_page': 1,
            'has_next_page': total_pages > 1
        }

    async def _scrape_profiles_concurrent(self, csv_file_path: str, max_concurrent: int = 3):
        """
        并发获取用户详细信息的优化版本
        """
        print(f"🔍 开始并发获取用户详细信息: {csv_file_path}")
        
        # 读取用户列表
        usernames = await self._read_usernames_from_csv(csv_file_path)
        if not usernames:
            yield {
                'type': 'error',
                'message': 'No username list found'
            }
            return

        total_users = len(usernames)
        print(f"将并发处理 {total_users} 个用户，并发数: {max_concurrent}")

        yield {
            'type': 'progress',
            'message': f'Starting concurrent processing of {total_users} users',
            'progress': 0,
            'total_count': total_users,
            'processed_count': 0
        }

        # 启动多个浏览器实例
        playwright = await async_playwright().start()
        browsers = []
        pages = []
        
        try:
            # 创建多个浏览器实例
            for i in range(max_concurrent):
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
                )
                browsers.append(browser)
                
                page = await browser.new_page()
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                pages.append(page)

            enriched_users = []
            processed_count = 0
            
            # 创建任务队列
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_user(username_data, page_index):
                nonlocal processed_count
                async with semaphore:
                    username = username_data['username']
                    page = pages[page_index % len(pages)]
                    
                    try:
                        user_details = await self._get_user_details_optimized(username, page, username_data)
                        if user_details:
                            enriched_users.append(user_details)
                            processed_count += 1
                            yield {
                                'type': 'user_completed',
                                'message': f'✅ {username} ({processed_count}/{total_users})',
                                'progress': (processed_count / total_users) * 100,
                                'current_user': username,
                                'total_count': total_users,
                                'processed_count': processed_count
                            }
                        else:
                            processed_count += 1
                            yield {
                                'type': 'user_failed',
                                'message': f'❌ {username} ({processed_count}/{total_users})',
                                'progress': (processed_count / total_users) * 100,
                                'current_user': username,
                                'total_count': total_users,
                                'processed_count': processed_count
                            }
                    except Exception as e:
                        processed_count += 1
                        yield {
                            'type': 'user_error',
                            'message': f'Error {username}: {str(e)[:50]}...',
                            'progress': (processed_count / total_users) * 100,
                            'current_user': username,
                            'total_count': total_users,
                            'processed_count': processed_count
                        }

            # 并发处理用户
            batch_size = 10  # 每批处理10个用户
            for i in range(0, len(usernames), batch_size):
                batch = usernames[i:i + batch_size]
                tasks = []
                
                for j, username_data in enumerate(batch):
                    task = process_user(username_data, j)
                    tasks.append(task)
                
                # 等待当前批次完成
                for task in tasks:
                    async for result in task:
                        yield result

                # 批次间稍微暂停
                if i + batch_size < len(usernames):
                    await asyncio.sleep(0.5)

            # 保存结果
            yield {
                'type': 'progress',
                'message': f'Saving results for {len(enriched_users)} users...',
                'progress': 95,
                'total_count': total_users,
                'processed_count': processed_count
            }

            output_file = await self._save_enriched_csv(enriched_users, csv_file_path)
            
            yield {
                'type': 'complete',
                'message': f'✅ Concurrent processing complete! {len(enriched_users)} users processed',
                'progress': 100,
                'total_count': total_users,
                'processed_count': processed_count,
                'output_file': output_file
            }

        finally:
            # 关闭所有浏览器
            for browser in browsers:
                await browser.close()
            await playwright.stop()

    async def _get_user_details_optimized(self, username: str, page_obj, original_data: Dict) -> Dict:
        """优化的用户详细信息获取方法"""
        try:
            # 访问用户主页 - 优化加载策略
            user_url = f"https://github.com/{username}"
            await page_obj.goto(user_url, wait_until='domcontentloaded', timeout=10000)
            
            # 减少等待时间
            await page_obj.wait_for_timeout(500)

            # 基础信息
            user_info = {
                'username': username,
                'display_name': username,
                'bio': '',
                'avatar_url': f"https://github.com/{username}.png",
                'profile_url': user_url,
                'platform': 'github',
                'type': 'follower',
                'follower_count': 0,
                'following_count': 0,
                'company': '',
                'location': '',
                'website': '',
                'twitter': '',
                'email': '',
                'public_repos': 0,
                'scraped_at': datetime.now().isoformat(),
                'source_user': original_data.get('source_user', ''),
                'source_repo': original_data.get('source_repo', ''),
                'page_number': original_data.get('page_number', ''),
                'profile_scraped_at': datetime.now().isoformat()
            }

            # 并发获取各种信息
            tasks = [
                self._get_display_name(page_obj, user_info),
                self._get_bio(page_obj, user_info),
                self._get_follower_counts(page_obj, user_info),
                self._get_company_location(page_obj, user_info),
                self._get_website_email(page_obj, user_info),
                self._get_repos_count(page_obj, user_info)
            ]

            await asyncio.gather(*tasks, return_exceptions=True)
            return user_info

        except Exception as e:
            print(f"获取用户 {username} 详细信息失败: {e}")
            # 返回基础信息而不是None
            return {
                'username': username,
                'display_name': username,
                'bio': '',
                'avatar_url': f"https://github.com/{username}.png",
                'profile_url': f"https://github.com/{username}",
                'platform': 'github',
                'type': 'follower',
                'follower_count': 0,
                'following_count': 0,
                'company': '',
                'location': '',
                'website': '',
                'twitter': '',
                'email': '',
                'public_repos': 0,
                'scraped_at': datetime.now().isoformat(),
                'source_user': original_data.get('source_user', ''),
                'source_repo': original_data.get('source_repo', ''),
                'page_number': original_data.get('page_number', ''),
                'profile_scraped_at': datetime.now().isoformat()
            }

    async def _get_display_name(self, page_obj, user_info: Dict):
        """获取显示名称"""
        try:
            name_element = await page_obj.query_selector('h1.vcard-names .p-name')
            if name_element:
                display_name = await name_element.text_content()
                if display_name and display_name.strip():
                    user_info['display_name'] = display_name.strip()
        except:
            pass

    async def _get_bio(self, page_obj, user_info: Dict):
        """获取bio"""
        try:
            bio_element = await page_obj.query_selector('.p-note .user-profile-bio')
            if bio_element:
                bio = await bio_element.text_content()
                if bio and bio.strip():
                    user_info['bio'] = bio.strip()
        except:
            pass

    async def _get_follower_counts(self, page_obj, user_info: Dict):
        """获取关注者数量"""
        try:
            follower_links = await page_obj.query_selector_all('.js-profile-editable-area a')
            for link in follower_links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                if href and text:
                    text = text.strip()
                    if 'followers' in href:
                        numbers = re.findall(r'\d+', text.replace(',', ''))
                        if numbers:
                            user_info['follower_count'] = int(numbers[0])
                    elif 'following' in href:
                        numbers = re.findall(r'\d+', text.replace(',', ''))
                        if numbers:
                            user_info['following_count'] = int(numbers[0])
        except:
            pass

    async def _get_company_location(self, page_obj, user_info: Dict):
        """获取公司和位置信息"""
        try:
            # 获取公司信息
            company_selectors = [
                '[data-test-selector="profile-company"] .p-org',
                '.vcard-detail[itemprop="worksFor"] .p-org',
                '.vcard-detail .p-org'
            ]
            for selector in company_selectors:
                company_element = await page_obj.query_selector(selector)
                if company_element:
                    company = await company_element.text_content()
                    if company and company.strip():
                        user_info['company'] = company.strip()
                        break

            # 获取位置信息
            location_selectors = [
                '[data-test-selector="profile-location"] .p-label',
                '.vcard-detail[itemprop="homeLocation"] .p-label',
                '.vcard-detail .p-label'
            ]
            for selector in location_selectors:
                location_element = await page_obj.query_selector(selector)
                if location_element:
                    location = await location_element.text_content()
                    if location and location.strip():
                        user_info['location'] = location.strip()
                        break
        except:
            pass

    async def _get_website_email(self, page_obj, user_info: Dict):
        """获取网站和邮箱信息"""
        try:
            # 获取网站
            website_element = await page_obj.query_selector('[data-test-selector="profile-website"] .Link--primary')
            if website_element:
                website = await website_element.get_attribute('href')
                if website and website.strip():
                    user_info['website'] = website.strip()

            # 获取邮箱
            itemprop_email = await page_obj.query_selector('li[itemprop="email"]')
            if itemprop_email:
                aria_label = await itemprop_email.get_attribute('aria-label')
                if aria_label and 'Email:' in aria_label:
                    email_match = aria_label.split('Email:', 1)
                    if len(email_match) > 1:
                        email = email_match[1].strip()
                        if '@' in email and '.' in email:
                            user_info['email'] = email
        except:
            pass

    async def _get_repos_count(self, page_obj, user_info: Dict):
        """获取仓库数量"""
        try:
            repos_element = await page_obj.query_selector('a[href$="?tab=repositories"] .Counter')
            if repos_element:
                repos_text = await repos_element.text_content()
                if repos_text:
                    repos_count = self._parse_count(repos_text.strip())
                    user_info['public_repos'] = repos_count
        except:
            pass

    async def _read_usernames_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """读取CSV文件中的用户名列表"""
        usernames = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    usernames.append({
                        'username': row.get('username', ''),
                        'source_user': row.get('source_user', ''),
                        'source_repo': row.get('source_repo', ''),
                        'page_number': row.get('page_number', ''),
                        'scraped_at': row.get('scraped_at', '')
                    })
        except Exception as e:
            print(f"Error reading usernames from CSV: {e}")
        return usernames

    async def _save_enriched_csv(self, users: List[Dict[str, Any]], original_csv_path: str) -> str:
        """保存详细信息到CSV文件"""
        output_file = original_csv_path.replace('_raw.csv', '_enriched.csv')
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                if users:
                    fieldnames = list(users[0].keys())
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for user in users:
                        writer.writerow(user)
            print(f"保存详细信息到: {output_file}")
            return output_file
        except Exception as e:
            print(f"Error saving enriched CSV: {e}")
            return ""

    def _parse_count(self, count_str: str) -> int:
        """解析数量字符串"""
        if not count_str:
            return 0
        
        count_str = count_str.replace(',', '').lower()
        
        if 'k' in count_str:
            return int(float(count_str.replace('k', '')) * 1000)
        elif 'm' in count_str:
            return int(float(count_str.replace('m', '')) * 1000000)
        else:
            try:
                return int(count_str)
            except:
                return 0

    async def scrape(self, url: str, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        执行完整的两阶段爬取流程

        Args:
            url: GitHub URL
            max_pages: 第一阶段最大爬取页数

        Returns:
            包含详细信息的用户列表
        """
        print(f"🚀 开始GitHub两阶段爬取: {url}")

        # 分析URL类型
        url_parts = url.rstrip('/').split('/')
        print(f"URL部分: {url_parts}")

        stage1_csv = ""

        # 默认爬取所有页面，最多不超过max_pages
        calculated_pages = max_pages
        print(f"计算需要爬取 {calculated_pages} 页（最多{max_pages}页）")

        if len(url_parts) >= 5 and url_parts[3] and url_parts[4]:
            # RepositoriesURL: https://github.com/owner/repo
            owner = url_parts[3]
            repo = url_parts[4]
            print(f"识别为Repositories页面: {owner}/{repo}")

            # 第一阶段：获取stargazers列表
            stage1_csv = await self.stage1_scraper.scrape_stargazers_list(owner, repo, calculated_pages)

        elif len(url_parts) >= 4 and url_parts[3]:
            # 用户URL: https://github.com/username
            username = url_parts[3]
            print(f"识别为用户页面: {username}")

            # 第一阶段：获取followers列表
            stage1_result = await self.stage1_scraper.scrape_followers_list(username, calculated_pages)
            if isinstance(stage1_result, dict):
                stage1_csv = stage1_result.get("csv_file", "")
            else:
                stage1_csv = stage1_result or ""

        else:
            print("无法识别URL类型")
            return []

        if not stage1_csv or not os.path.exists(stage1_csv):
            print("第一阶段失败，没有生成用户列表文件")
            return []

        print(f"第一阶段完成，生成文件: {stage1_csv}")

        # 第二阶段：获取用户详细信息
        print("🔍 开始第二阶段：获取用户详细信息...")
        stage2_csv = await self.stage2_scraper.scrape_profiles_from_csv(
            stage1_csv,
            batch_size=5  # 小批次处理，避免过载
        )

        if not stage2_csv or not os.path.exists(stage2_csv):
            print("第二阶段失败，没有生成详细信息文件")
            return []

        print(f"第二阶段完成，生成文件: {stage2_csv}")

        # 读取最终结果
        return await self._read_enriched_data(stage2_csv)

    async def _read_enriched_data(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """读取详细信息CSV文件并返回数据"""
        users = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # 标准化数据格式
                    user_data = {
                        'username': row.get('username', ''),
                        'display_name': row.get('display_name', ''),
                        'bio': row.get('bio', ''),
                        'avatar_url': row.get('avatar_url', ''),
                        'profile_url': row.get('profile_url', ''),
                        'platform': 'github',
                        'type': row.get('type', 'user'),
                        'follower_count': self._safe_int(row.get('follower_count', '0')),
                        'following_count': self._safe_int(row.get('following_count', '0')),
                        'company': row.get('company', ''),
                        'location': row.get('location', ''),
                        'website': row.get('website', ''),
                        'twitter': row.get('twitter', ''),
                        'public_repos': self._safe_int(row.get('public_repos', '0')),
                        'scraped_at': row.get('profile_scraped_at', self.get_current_time()),
                        'additional_info': f"Source: {row.get('source_user', '')}{row.get('source_repo', '')}, Page: {row.get('page_number', '')}"
                    }
                    users.append(user_data)

            print(f"成功读取 {len(users)} 个用户的详细信息")
            return users

        except Exception as e:
            print(f"读取详细信息文件时出错: {e}")
            return []

    def _safe_int(self, value: str) -> int:
        """安全转换字符串为整数"""
        try:
            return int(value) if value else 0
        except:
            return 0

    def _parse_url(self, url: str) -> tuple:
        """解析GitHub URL，确定爬取类型"""
        try:
            # 移除协议和域名，获取路径部分
            if '://' in url:
                path_part = url.split('://', 1)[1]
                if '/' in path_part:
                    path = path_part.split('/', 1)[1]
                else:
                    path = ''
            else:
                path = url.strip('/')

            # 分割路径
            parts = [p for p in path.split('/') if p]
            print(f"解析URL路径部分: {parts}")

            if not parts:
                raise ValueError("URL路径为空")

            # 检查是否包含tab参数
            if '?' in url and 'tab=followers' in url:
                return "followers", parts[0] if parts else "", ""
            elif '?' in url and 'tab=stargazers' in url:
                return "stargazers", parts[0] if parts else "", ""
            elif len(parts) >= 2 and parts[1] == 'stargazers':
                # https://github.com/owner/repo/stargazers
                return "stargazers", parts[0], parts[1] if len(parts) > 1 else ""
            elif len(parts) >= 2:
                # https://github.com/owner/repo
                return "repo", parts[0], parts[1]
            elif len(parts) == 1:
                # https://github.com/username
                return "user", parts[0], ""
            else:
                raise ValueError(f"无法解析的URL格式: {url}")

        except Exception as e:
            print(f"解析URL失败: {e}")
            raise ValueError(f"URL解析错误: {e}")

    async def scrape_page(self, url: str, page: int = 1) -> Dict:
        """分页爬取方法"""
        try:
            print(f"GitHub分页爬取器收到URL: {url}, 页码: {page}")

            # 解析URL确定爬取类型
            scrape_type, target_user, target_repo = self._parse_url(url)

            if scrape_type == "followers":
                print(f"识别为followers页面，第{page}页")
                return await self._scrape_followers_page(url, page)
            elif scrape_type == "stargazers":
                print(f"识别为stargazers页面，第{page}页")
                return await self._scrape_stargazers_page(url, target_user, target_repo, page)
            elif scrape_type == "user":
                print(f"识别为用户页面: {target_user}，第{page}页")
                # 默认爬取用户的followers
                followers_url = f"https://github.com/{target_user}?tab=followers"
                return await self._scrape_followers_page(followers_url, page)
            elif scrape_type == "repo":
                print(f"识别为Repositories页面: {target_user}/{target_repo}，第{page}页")
                # 默认爬取Repositories的stargazers
                stargazers_url = f"https://github.com/{target_user}/{target_repo}/stargazers"
                return await self._scrape_stargazers_page(stargazers_url, target_user, target_repo, page)
            else:
                raise ValueError(f"无法识别的URL类型: {url}")

        except Exception as e:
            print(f"GitHub分页爬取失败: {e}")
            raise e

    async def _scrape_followers_page(self, url: str, page: int) -> Dict:
        """分页爬取followers"""
        try:
            print(f"开始爬取关注者页面第{page}页: {url}")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page_obj = await context.new_page()

                try:
                    # 构建分页URL
                    if '?' in url:
                        page_url = f"{url}&page={page}"
                    else:
                        page_url = f"{url}?page={page}"

                    print(f"访问分页URL: {page_url}")
                    await page_obj.goto(page_url, wait_until='networkidle', timeout=30000)

                    # 等待用户列表加载
                    await page_obj.wait_for_selector('a[data-hovercard-type="user"]', timeout=10000)

                    # 获取用户链接
                    user_links = await page_obj.query_selector_all('a[data-hovercard-type="user"]')
                    print(f"找到 {len(user_links)} 个用户链接元素")

                    # 提取用户名列表，使用set去重
                    usernames = []
                    seen_usernames = set()
                    for link in user_links:
                        try:
                            href = await link.get_attribute('href')
                            if href and href.startswith('/'):
                                username = href.strip('/')
                                # 去重：如果用户名已经存在，跳过
                                if username and username not in seen_usernames:
                                    seen_usernames.add(username)
                                    usernames.append(username)

                                    # 限制每页最多50个用户
                                    if len(usernames) >= 50:
                                        break
                        except Exception as e:
                            print(f"提取用户名失败: {e}")
                            continue

                    print(f"开始获取 {len(usernames)} 个用户的详细信息...")

                    # 获取用户详细信息
                    users = []
                    for i, username in enumerate(usernames):
                        try:
                            print(f"正在获取用户 {i+1}/{len(usernames)}: {username}")
                            user_info = await self._get_user_details_optimized(username, page_obj, {'username': username, 'source_user': '', 'source_repo': '', 'page_number': str(page), 'scraped_at': datetime.now().isoformat()})
                            user_info['type'] = 'follower'
                            users.append(user_info)
                        except Exception as e:
                            print(f"获取用户 {username} 详细信息失败: {e}")
                            # 添加基本信息
                            users.append({
                                'username': username,
                                'display_name': username,
                                'bio': '',
                                'avatar_url': f"https://github.com/{username}.png",
                                'profile_url': f"https://github.com/{username}",
                                'platform': 'github',
                                'type': 'follower',
                                'follower_count': 0,
                                'following_count': 0,
                                'company': '',
                                'location': '',
                                'website': '',
                                'twitter': '',
                                'email': '',
                                'public_repos': 0,
                                'scraped_at': datetime.now().isoformat()
                            })

                    # 按follower数量排序（降序）
                    users.sort(key=lambda x: x['follower_count'], reverse=True)
                    print(f"用户按follower数量排序完成，最高: {users[0]['follower_count'] if users else 0}")

                    # 检查是否有下一页 - 使用多种策略
                    has_next_page = False
                    try:
                        # GitHub可能使用不同的分页选择器
                        selectors_to_check = [
                            '.pagination a[rel="next"]',
                            '.paginate-container .next_page',
                            '.paginate-container a[rel="next"]',
                            'a[aria-label="Next"]',
                            '.BtnGroup a[rel="next"]',
                            '.pagination .next_page:not(.disabled)',
                            '.paginate-container .next_page:not(.disabled)'
                        ]

                        for selector in selectors_to_check:
                            next_button = await page_obj.query_selector(selector)
                            if next_button:
                                # 检查按钮是否被禁用
                                is_disabled = await next_button.get_attribute('aria-disabled')
                                class_name = await next_button.get_attribute('class') or ''
                                if is_disabled != 'true' and 'disabled' not in class_name:
                                    has_next_page = True
                                    print(f"找到有效的下一页按钮: {selector}")
                                    break

                        # 如果没有找到明确的下一页按钮，检查当前页面的用户数量
                        # 如果正好是50个用户，很可能还有下一页
                        if not has_next_page and len(users) >= 50:
                            has_next_page = True
                            print(f"基于用户数量({len(users)})判断可能有下一页")

                    except Exception as e:
                        print(f"检查下一页时出错: {e}")
                        # 如果出错且用户数量达到50，假设有下一页
                        if len(users) >= 50:
                            has_next_page = True

                    print(f"成功提取了第{page}页 {len(users)} 个关注者")

                    return {
                        'data': users,
                        'has_next_page': has_next_page,
                        'current_page': page
                    }

                finally:
                    await browser.close()

        except Exception as e:
            print(f"Error scraping followers page {page}: {e}")
            return {
                'data': [],
                'has_next_page': False,
                'current_page': page
            }

    async def _scrape_stargazers_page(self, url: str, owner: str, repo: str, page: int) -> Dict:
        """分页爬取stargazers"""
        try:
            print(f"开始爬取stargazers页面第{page}页: {url}")

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page_obj = await context.new_page()

                try:
                    # 构建分页URL
                    page_url = f"{url}?page={page}"

                    print(f"访问分页URL: {page_url}")
                    await page_obj.goto(page_url, wait_until='networkidle', timeout=30000)

                    # 等待用户列表加载
                    await page_obj.wait_for_selector('a[data-hovercard-type="user"]', timeout=10000)

                    # 获取用户链接
                    user_links = await page_obj.query_selector_all('a[data-hovercard-type="user"]')
                    print(f"找到 {len(user_links)} 个用户链接元素")

                    # 提取用户名列表，使用set去重
                    usernames = []
                    seen_usernames = set()
                    for link in user_links:
                        try:
                            href = await link.get_attribute('href')
                            if href and href.startswith('/'):
                                username = href.strip('/')
                                # 去重：如果用户名已经存在，跳过
                                if username and username not in seen_usernames:
                                    seen_usernames.add(username)
                                    usernames.append(username)

                                    # 限制每页最多50个用户
                                    if len(usernames) >= 50:
                                        break
                        except Exception as e:
                            print(f"提取用户名失败: {e}")
                            continue

                    print(f"开始获取 {len(usernames)} 个用户的详细信息...")

                    # 获取用户详细信息
                    users = []
                    for i, username in enumerate(usernames):
                        try:
                            print(f"正在获取用户 {i+1}/{len(usernames)}: {username}")
                            user_info = await self._get_user_details_optimized(username, page_obj, {'username': username, 'source_user': '', 'source_repo': f"{owner}/{repo}", 'page_number': str(page), 'scraped_at': datetime.now().isoformat()})
                            user_info['type'] = 'stargazer'
                            users.append(user_info)
                        except Exception as e:
                            print(f"获取用户 {username} 详细信息失败: {e}")
                            # 添加基本信息
                            users.append({
                                'username': username,
                                'display_name': username,
                                'bio': '',
                                'avatar_url': f"https://github.com/{username}.png",
                                'profile_url': f"https://github.com/{username}",
                                'platform': 'github',
                                'type': 'stargazer',
                                'follower_count': 0,
                                'following_count': 0,
                                'company': '',
                                'location': '',
                                'website': '',
                                'twitter': '',
                                'email': '',
                                'public_repos': 0,
                                'scraped_at': datetime.now().isoformat()
                            })

                    # 按follower数量排序（降序）
                    users.sort(key=lambda x: x['follower_count'], reverse=True)
                    print(f"用户按follower数量排序完成，最高: {users[0]['follower_count'] if users else 0}")

                    # 检查是否有下一页 - 使用多种策略
                    has_next_page = False
                    try:
                        # GitHub可能使用不同的分页选择器
                        selectors_to_check = [
                            '.pagination a[rel="next"]',
                            '.paginate-container .next_page',
                            '.paginate-container a[rel="next"]',
                            'a[aria-label="Next"]',
                            '.BtnGroup a[rel="next"]',
                            '.pagination .next_page:not(.disabled)',
                            '.paginate-container .next_page:not(.disabled)'
                        ]

                        for selector in selectors_to_check:
                            next_button = await page_obj.query_selector(selector)
                            if next_button:
                                # 检查按钮是否被禁用
                                is_disabled = await next_button.get_attribute('aria-disabled')
                                class_name = await next_button.get_attribute('class') or ''
                                if is_disabled != 'true' and 'disabled' not in class_name:
                                    has_next_page = True
                                    print(f"找到有效的下一页按钮: {selector}")
                                    break

                        # 如果没有找到明确的下一页按钮，检查当前页面的用户数量
                        # 如果正好是50个用户，很可能还有下一页
                        if not has_next_page and len(users) >= 50:
                            has_next_page = True
                            print(f"基于用户数量({len(users)})判断可能有下一页")

                    except Exception as e:
                        print(f"检查下一页时出错: {e}")
                        # 如果出错且用户数量达到50，假设有下一页
                        if len(users) >= 50:
                            has_next_page = True

                    print(f"成功提取了第{page}页 {len(users)} 个stargazers")

                    return {
                        'data': users,
                        'has_next_page': has_next_page,
                        'current_page': page
                    }

                finally:
                    await browser.close()

        except Exception as e:
            print(f"Error scraping stargazers page {page}: {e}")
            return {
                'data': [],
                'has_next_page': False,
                'current_page': page
            }

# 测试函数
async def test_two_stage_scraper():
    """测试两阶段爬取器"""
    scraper = GitHubTwoStageScraper()

    # 测试用户followers
    print("=== 测试用户followers爬取 ===")
    users = await scraper.scrape("https://github.com/connor4312", max_pages=2)
    print(f"获取到 {len(users)} 个用户的详细信息")

    if users:
        print("\n前3个用户详细信息:")
        for i, user in enumerate(users[:3]):
            print(f"\n用户 {i+1}:")
            for key, value in user.items():
                if key in ['username', 'display_name', 'bio', 'company', 'location', 'follower_count', 'following_count']:
                    print(f"  {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_two_stage_scraper())