import asyncio
import re
from datetime import datetime
from typing import List, Dict, Any
from playwright.async_api import async_playwright
from .base import BaseScraper

class GitHubScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.platform = "github"
    
    def get_current_time(self) -> str:
        """获取当前时间的ISO格式字符串"""
        return datetime.now().isoformat()
    
    async def scrape(self, url: str) -> List[Dict[str, Any]]:
        """
        爬取GitHub数据
        支持两种模式：
        1. RepositoriesURL -> 爬取stargazers
        2. 用户URL -> 爬取followers
        """
        print(f"GitHub爬取器收到URL: {url}")
        
        # 分析URL类型
        url_parts = url.rstrip('/').split('/')
        print(f"URL部分: {url_parts}")
        
        if len(url_parts) >= 5 and url_parts[3] and url_parts[4]:
            # RepositoriesURL: https://github.com/owner/repo
            owner = url_parts[3]
            repo = url_parts[4]
            print(f"识别为Repositories页面: {owner}/{repo}")
            return await self._scrape_stargazers(owner, repo)
        elif len(url_parts) >= 4 and url_parts[3]:
            # 用户URL: https://github.com/username
            username = url_parts[3]
            print(f"识别为用户页面: {username}")
            return await self._scrape_followers(username)
        else:
            print("无法识别URL类型")
            return []
    
    async def _scrape_stargazers(self, owner: str, repo: str) -> List[Dict[str, Any]]:
        """爬取Repositories的stargazers"""
        stargazers_url = f"https://github.com/{owner}/{repo}/stargazers"
        print(f"开始爬取stargazers页面: {stargazers_url}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(stargazers_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            # 获取stargazers列表
            user_links = await page.query_selector_all('a[data-hovercard-type="user"]')
            print(f"找到 {len(user_links)} 个用户链接元素")
            
            users = []
            seen_usernames = set()
            
            for link in user_links:
                try:
                    href = await link.get_attribute('href')
                    if href and href.startswith('/'):
                        username = href.strip('/')
                        if username and username not in seen_usernames:
                            seen_usernames.add(username)
                            
                            # 获取用户详细信息
                            user_info = await self._get_user_details(page, username)
                            user_info['type'] = 'stargazer'
                            users.append(user_info)
                            
                            if len(users) >= 20:  # 限制数量
                                break
                except Exception as e:
                    print(f"处理用户链接时出错: {e}")
                    continue
            
            print(f"成功提取了 {len(users)} 个stargazers")
            return users
            
        except Exception as e:
            print(f"Error scraping stargazers: {e}")
            return []
        finally:
            await browser.close()
            await playwright.stop()
    
    async def _scrape_followers(self, username: str) -> List[Dict[str, Any]]:
        """爬取用户的followers"""
        followers_url = f"https://github.com/{username}?tab=followers"
        print(f"开始爬取关注者页面: {followers_url}")
        
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(followers_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)
            
            # 获取followers列表
            user_links = await page.query_selector_all('a[data-hovercard-type="user"]')
            print(f"找到 {len(user_links)} 个用户链接元素")
            
            users = []
            seen_usernames = set()
            
            for link in user_links:
                try:
                    href = await link.get_attribute('href')
                    if href and href.startswith('/'):
                        follower_username = href.strip('/')
                        if follower_username and follower_username not in seen_usernames:
                            seen_usernames.add(follower_username)
                            
                            # 创建基本用户信息
                            user_info = {
                                'username': follower_username,
                                'display_name': follower_username,
                                'bio': '',
                                'avatar_url': f'https://github.com/{follower_username}.png',
                                'profile_url': f'https://github.com/{follower_username}',
                                'platform': 'github',
                                'type': 'follower',
                                'follower_count': 0,
                                'following_count': 0,
                                'company': '',
                                'location': '',
                                'website': '',
                                'twitter': '',
                                'scraped_at': self.get_current_time()
                            }
                            
                            users.append(user_info)
                            
                            if len(users) >= 50:  # 增加数量限制
                                break
                except Exception as e:
                    print(f"处理用户链接时出错: {e}")
                    continue
            
            # 为前5个用户获取详细信息
            print(f"为前5个用户获取详细信息...")
            for i, user in enumerate(users[:5]):
                try:
                    detailed_info = await self._get_user_details_simple(browser, user['username'])
                    users[i].update(detailed_info)
                except Exception as e:
                    print(f"获取用户 {user['username']} 详细信息时出错: {e}")
            
            print(f"成功提取了 {len(users)} 个关注者")
            return users
            
        except Exception as e:
            print(f"Error scraping followers: {e}")
            return []
        finally:
            await browser.close()
            await playwright.stop()
    
    async def _get_user_details_simple(self, browser, username: str) -> Dict[str, Any]:
        """获取用户详细信息（简化版）"""
        user_url = f"https://github.com/{username}"
        
        try:
            # 创建新页面
            user_page = await browser.new_page()
            await user_page.goto(user_url, wait_until="networkidle", timeout=15000)
            await asyncio.sleep(1)
            
            details = {}
            
            # 获取真实姓名
            try:
                name_elem = await user_page.query_selector('.vcard-fullname')
                if name_elem:
                    name = await name_elem.text_content()
                    if name:
                        details['display_name'] = name.strip()
            except:
                pass
            
            # 获取bio
            try:
                bio_elem = await user_page.query_selector('.user-profile-bio')
                if bio_elem:
                    bio = await bio_elem.text_content()
                    if bio:
                        details['bio'] = bio.strip()
            except:
                pass
            
            # 获取公司信息
            try:
                company_elem = await user_page.query_selector('.p-org')
                if company_elem:
                    company = await company_elem.text_content()
                    if company:
                        details['company'] = company.strip()
            except:
                pass
            
            # 获取位置信息
            try:
                location_elem = await user_page.query_selector('.p-label')
                if location_elem:
                    location = await location_elem.text_content()
                    if location:
                        details['location'] = location.strip()
            except:
                pass
            
            # 获取网站和Twitter链接
            try:
                link_elems = await user_page.query_selector_all('.Link--primary')
                for link_elem in link_elems:
                    href = await link_elem.get_attribute('href')
                    text = await link_elem.text_content()
                    if href and text:
                        text = text.strip()
                        if 'twitter.com' in href or text.startswith('@'):
                            details['twitter'] = text
                        elif href.startswith('http') and 'github.com' not in href:
                            details['website'] = text
            except:
                pass
            
            # 获取follower和following数量
            try:
                follower_links = await user_page.query_selector_all('.js-profile-editable-area a')
                for link in follower_links:
                    href = await link.get_attribute('href')
                    text = await link.text_content()
                    if href and text:
                        text = text.strip()
                        if 'followers' in href:
                            # 提取数字
                            numbers = re.findall(r'\d+', text.replace(',', ''))
                            if numbers:
                                details['follower_count'] = int(numbers[0])
                        elif 'following' in href:
                            numbers = re.findall(r'\d+', text.replace(',', ''))
                            if numbers:
                                details['following_count'] = int(numbers[0])
            except:
                pass
            
            await user_page.close()
            return details
            
        except Exception as e:
            print(f"获取用户 {username} 详细信息时出错: {e}")
            return {}
    
    async def _get_user_details(self, page, username: str) -> Dict[str, Any]:
        """获取用户详细信息（保留原方法以兼容stargazers）"""
        user_url = f"https://github.com/{username}"
        
        try:
            # 返回基本信息
            return {
                'username': username,
                'display_name': username,
                'bio': '',
                'avatar_url': f'https://github.com/{username}.png',
                'profile_url': user_url,
                'platform': 'github',
                'follower_count': 0,
                'following_count': 0,
                'company': '',
                'location': '',
                'website': '',
                'twitter': '',
                'scraped_at': self.get_current_time()
            }
            
        except Exception as e:
            print(f"获取用户 {username} 详细信息时出错: {e}")
            # 返回基本信息
            return {
                'username': username,
                'display_name': username,
                'bio': '',
                'avatar_url': f'https://github.com/{username}.png',
                'profile_url': user_url,
                'platform': 'github',
                'type': 'user',
                'follower_count': 0,
                'following_count': 0,
                'company': '',
                'location': '',
                'website': '',
                'twitter': '',
                'scraped_at': self.get_current_time()
            } 