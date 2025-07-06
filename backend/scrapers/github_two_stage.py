import asyncio
import os
from typing import List, Dict, Any
from .base import BaseScraper
from .github.get_followers_list import GitHubFollowersListScraper
from .github.scrape_profiles import GitHubProfileScraper
from .performance_config import PERFORMANCE_CONFIG, BROWSER_ARGS, OPTIMIZED_HEADERS
from playwright.async_api import async_playwright
from datetime import datetime

class GitHubTwoStageScraper(BaseScraper):
    """GitHub两阶段爬取器 - 整合版本"""

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
            
            # Use standard mode for small datasets (< 500 followers)
            if actual_followers_count < 500:
                print(f"🚀 Using optimized standard mode for {actual_followers_count} followers")
                async for result in self._scrape_with_progress_optimized(url, max_pages):
                    yield result
                return
            
            # Use unlimited mode only for large datasets
            elif unlimited or max_users > actual_followers_count:
                print(f"🚀 Using unlimited mode for {actual_followers_count} followers")
                # Calculate appropriate max_pages based on actual followers
                unlimited_pages = min((actual_followers_count + 49) // 50, 20)
                async for result in self._scrape_with_progress_original(url, unlimited_pages):
                    if result.get('type') == 'complete':
                        result['unlimited_mode'] = 'true'
                        result['target_users'] = str(min(max_users, actual_followers_count))
                    yield result
                return
        
        # Default to standard mode
        print(f"🚀 Using standard mode (max_pages: {max_pages})")
        async for result in self._scrape_with_progress_original(url, max_pages):
            yield result
    
    async def _scrape_with_progress_original(self, url: str, max_pages: int = 5):
        """
        执行完整的两阶段爬取流程，边爬边返回进度

        Args:
            url: GitHub URL
            max_pages: 第一阶段最大爬取页数
            max_users: 第二阶段最大处理用户数

        Yields:
            包含进度信息的字典
        """
        print(f"🚀 开始GitHub两阶段流式爬取: {url}")

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

        # 默认爬取所有页面，最多不超过max_pages
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
            # 对于stargazers，我们设置默认值
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

        # 第二阶段：获取用户详细信息
        # 检查是否有用户数据需要处理
        has_users_to_process = False
        if os.path.exists(stage1_csv):
            # 读取CSV文件来检查是否有用户数据
            try:
                with open(stage1_csv, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    has_users_to_process = len(lines) > 1  # 除了header之外还有数据
            except Exception as e:
                print(f"Error reading CSV file: {e}")
                has_users_to_process = False

        if has_users_to_process:
            yield {
                'type': 'progress',
                'stage': 2,
                'message': f'Starting Stage 2: Getting detailed info for all scraped users...',
                'progress': 60
            }

            # 使用带进度的第二阶段爬取（处理所有用户）
            async for progress in self.stage2_scraper.scrape_profiles_from_csv_with_progress(
                stage1_csv,
                batch_size=5
            ):
                # 调整进度范围 60-95%
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
            # 对于没有用户数据的情况，跳过第二阶段，直接返回空结果
            yield {
                'type': 'progress',
                'stage': 2,
                'message': 'No users found, skipping detailed scraping...',
                'progress': 95
            }
            final_data = []

        # 确定消息类型（followers还是stargazers）
        is_user_followers = len(url_parts) >= 4 and len(url_parts) < 5
        if is_user_followers:
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
        import csv

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

    async def _get_user_details(self, username: str, page_obj) -> Dict:
        """获取用户详细信息"""
        try:
            # 访问用户主页
            user_url = f"https://github.com/{username}"
            await page_obj.goto(user_url, wait_until='networkidle', timeout=15000)

            # 等待页面加载
            await page_obj.wait_for_timeout(1000)

            # 提取用户信息
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
                'scraped_at': datetime.now().isoformat()
            }

            # 获取用户名和显示名
            try:
                name_element = await page_obj.query_selector('h1.vcard-names .p-name')
                if name_element:
                    display_name = await name_element.text_content()
                    if display_name and display_name.strip():
                        user_info['display_name'] = display_name.strip()
            except:
                pass

            # 获取bio
            try:
                bio_element = await page_obj.query_selector('.p-note .user-profile-bio')
                if bio_element:
                    bio = await bio_element.text_content()
                    if bio and bio.strip():
                        user_info['bio'] = bio.strip()
            except:
                pass

            # 获取follower和following数量 - 使用原scrape_profiles.py的成功方法
            try:
                import re
                # 获取.js-profile-editable-area下的所有链接
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
                                print(f"用户 {username} followers: {numbers[0]}")
                        elif 'following' in href:
                            numbers = re.findall(r'\d+', text.replace(',', ''))
                            if numbers:
                                user_info['following_count'] = int(numbers[0])
                                print(f"用户 {username} following: {numbers[0]}")

                # 如果上面的方法没有找到，尝试备用选择器
                if user_info['follower_count'] == 0:
                    # 调试：输出页面上所有包含followers的链接
                    try:
                        all_links = await page_obj.query_selector_all('a')
                        for link in all_links:
                            href = await link.get_attribute('href')
                            text = await link.text_content()
                            if href and 'followers' in href:
                                print(f"找到followers链接: href={href}, text='{text}'")
                                # 尝试从链接文本中提取数字
                                if text:
                                    numbers = re.findall(r'\d+', text.replace(',', ''))
                                    if numbers:
                                        user_info['follower_count'] = int(numbers[0])
                                        print(f"备用方法获取到用户 {username} followers: {numbers[0]}")
                                        break
                            if href and 'following' in href:
                                print(f"找到following链接: href={href}, text='{text}'")
                                if text:
                                    numbers = re.findall(r'\d+', text.replace(',', ''))
                                    if numbers:
                                        user_info['following_count'] = int(numbers[0])
                                        print(f"备用方法获取到用户 {username} following: {numbers[0]}")
                    except:
                        pass

            except Exception as e:
                print(f"获取 {username} 关注数据失败: {e}")
                pass

            # 获取公司信息
            try:
                company_selectors = [
                    '[data-test-selector="profile-company"] .p-org',
                    '.vcard-detail[itemprop="worksFor"] .p-org',
                    '.vcard-detail .p-org',
                    '.js-profile-editable-area [data-test-selector="profile-company"]'
                ]

                for selector in company_selectors:
                    company_element = await page_obj.query_selector(selector)
                    if company_element:
                        company = await company_element.text_content()
                        if company and company.strip():
                            user_info['company'] = company.strip()
                            print(f"User {username} company: {company.strip()}")
                            break
            except Exception as e:
                print(f"Failed to get user {username} company info: {e}")
                pass

            # 获取位置信息
            try:
                location_selectors = [
                    '[data-test-selector="profile-location"] .p-label',
                    '.vcard-detail[itemprop="homeLocation"] .p-label',
                    '.vcard-detail .p-label',
                    '.js-profile-editable-area [data-test-selector="profile-location"]'
                ]

                for selector in location_selectors:
                    location_element = await page_obj.query_selector(selector)
                    if location_element:
                        location = await location_element.text_content()
                        if location and location.strip():
                            user_info['location'] = location.strip()
                            print(f"User {username} location: {location.strip()}")
                            break
            except Exception as e:
                print(f"Failed to get user {username} location info: {e}")
                pass

            # 获取邮箱信息，只保留 itemprop="email" aria-label 方式
            try:
                itemprop_email = await page_obj.query_selector('li[itemprop="email"]')
                if itemprop_email:
                    aria_label = await itemprop_email.get_attribute('aria-label')
                    if aria_label and 'Email:' in aria_label:
                        # 提取 "Email: xxx@xxx.com" 中的邮箱部分
                        email_match = aria_label.split('Email:', 1)
                        if len(email_match) > 1:
                            email = email_match[1].strip()
                            if '@' in email and '.' in email:
                                user_info['email'] = email
                                print(f"User {username} email (from itemprop): {email}")
            except Exception as e:
                print(f"Failed to get user {username} email info: {e}")
                pass

            # 获取网站
            try:
                website_element = await page_obj.query_selector('[data-test-selector="profile-website"] .Link--primary')
                if website_element:
                    website = await website_element.get_attribute('href')
                    if website and website.strip():
                        user_info['website'] = website.strip()
            except:
                pass

            # 获取公开Repositories数量
            try:
                repos_element = await page_obj.query_selector('a[href$="?tab=repositories"] .Counter')
                if repos_element:
                    repos_text = await repos_element.text_content()
                    if repos_text:
                        repos_count = self._parse_count(repos_text.strip())
                        user_info['public_repos'] = repos_count
            except:
                pass

            return user_info

        except Exception as e:
            print(f"获取用户 {username} 详细信息失败: {e}")
            # 返回基本信息
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
                'scraped_at': datetime.now().isoformat()
            }

    def _parse_count(self, count_str: str) -> int:
        """解析GitHub的数量显示（支持k, m等单位）"""
        try:
            count_str = count_str.lower().replace(',', '')
            if 'k' in count_str:
                return int(float(count_str.replace('k', '')) * 1000)
            elif 'm' in count_str:
                return int(float(count_str.replace('m', '')) * 1000000)
            else:
                return int(count_str)
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
                            user_info = await self._get_user_details(username, page_obj)
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
            print(f"爬取followers第{page}页时出错: {e}")
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
                            user_info = await self._get_user_details(username, page_obj)
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
            print(f"爬取stargazers第{page}页时出错: {e}")
            return {
                'data': [],
                'has_next_page': False,
                'current_page': page
            }

    async def _scrape_with_progress_optimized(self, url: str, max_pages: int = 5):
        """Optimized version for small datasets with faster processing"""
        print(f"🚀 Starting optimized GitHub scraping: {url}")

        yield {
            'type': 'progress',
            'stage': 1,
            'message': 'Starting optimized scraping for small dataset...',
            'progress': 0
        }

        # Parse URL and get basic info
        url_parts = url.rstrip('/').split('/')
        stage1_csv = ""
        
        if len(url_parts) >= 4 and url_parts[3]:
            username = url_parts[3]
            if len(url_parts) == 4:  # User profile
                print(f"识别为用户页面: {username}")
                
                yield {
                    'type': 'progress',
                    'stage': 1,
                    'message': f'Scraping followers for user {username} (optimized)...',
                    'progress': 10
                }
                
                # Stage 1: Get followers list
                stage1_result = await self.stage1_scraper.scrape_followers_list(username, max_pages)
                if isinstance(stage1_result, dict):
                    stage1_csv = stage1_result.get("csv_file", "")
                    total_followers = stage1_result.get("total_followers", 0)
                    total_pages = stage1_result.get("total_pages", 1)
                else:
                    stage1_csv = stage1_result or ""
                    total_followers = 0
                    total_pages = 1
                
                if not stage1_csv or not os.path.exists(stage1_csv):
                    yield {
                        'type': 'error',
                        'message': 'Stage 1 failed, no user list file generated'
                    }
                    return
                
                yield {
                    'type': 'progress',
                    'stage': 1,
                    'message': f'Stage 1 complete, found {total_followers} followers',
                    'progress': 50,
                    'total_followers': total_followers,
                    'total_pages': total_pages,
                    'current_page': 1
                }
                
                # Stage 2: Get detailed profiles with optimized batch size for small datasets
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
                        'message': f'Stage 2: Getting detailed profiles (optimized for small dataset)...',
                        'progress': 60
                    }
                    
                    # Use smaller batch size for faster processing of small datasets
                    optimized_batch_size = min(10, total_followers) if total_followers > 0 else 10
                    
                    async for progress in self.stage2_scraper.scrape_profiles_from_csv_with_progress(
                        stage1_csv,
                        batch_size=optimized_batch_size
                    ):
                        # Adjust progress range 60-95%
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
                    
                    final_data = await self._read_enriched_data(stage1_csv.replace('_raw.csv', '_enriched.csv'))
                else:
                    yield {
                        'type': 'progress',
                        'stage': 2,
                        'message': 'No users found, skipping detailed scraping...',
                        'progress': 95
                    }
                    final_data = []
                
                # Complete
                yield {
                    'type': 'complete',
                    'data': final_data,
                    'total': len(final_data),
                    'message': f'Optimized scraping complete! Found {total_followers} followers, retrieved {len(final_data)} detailed profiles',
                    'progress': 100,
                    'platform': 'github',
                    'total_followers': total_followers,
                    'total_pages': total_pages,
                    'current_page': 1,
                    'has_next_page': total_pages > 1
                }
                
        # Handle repository stargazers
        elif len(url_parts) >= 5 and url_parts[3] and url_parts[4]:
            owner = url_parts[3]
            repo = url_parts[4]
            
            yield {
                'type': 'progress',
                'stage': 1,
                'message': f'Scraping stargazers for repository {owner}/{repo} (optimized)...',
                'progress': 10
            }
            
            stage1_csv = await self.stage1_scraper.scrape_stargazers_list(owner, repo, max_pages)
            
            if not stage1_csv:
                yield {
                    'type': 'error',
                    'message': 'Stage 1 failed, no stargazers list generated'
                }
                return
            
            final_data = await self._read_enriched_data(stage1_csv.replace('_raw.csv', '_enriched.csv'))
            
            yield {
                'type': 'complete',
                'data': final_data,
                'total': len(final_data),
                'message': f'Optimized scraping complete! Retrieved {len(final_data)} stargazers',
                'progress': 100,
                'platform': 'github',
                'total_followers': 0,
                'total_pages': 1,
                'current_page': 1,
                'has_next_page': False
            }
        else:
            yield {
                'type': 'error',
                'message': 'Unable to recognize URL type'
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