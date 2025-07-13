import asyncio
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
import re
import time

class GitHubProfileScraperOptimized:
    """GitHub第二阶段：高并发获取用户详细资料信息"""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    async def scrape_profiles_from_csv_concurrent(self, csv_file_path: str, max_users: Optional[int] = None, 
                                                max_concurrent: int = 8, max_browsers: int = 3):
        """
        高并发异步获取用户详细资料
        
        Args:
            csv_file_path: 第一阶段生成的CSV文件路径
            max_users: 最大处理用户数，None表示处理所有用户
            max_concurrent: 最大并发数
            max_browsers: 最大浏览器实例数
        """
        print(f"🚀 开始高并发获取用户详细资料，并发数: {max_concurrent}, 浏览器数: {max_browsers}")
        
        # 读取用户列表
        usernames = await self._read_usernames_from_csv(csv_file_path)
        if not usernames:
            print("❌ 没有找到用户列表")
            return ""
        
        # 限制处理数量
        if max_users is not None:
            usernames = usernames[:max_users]
        total_users = len(usernames)
        
        print(f"📊 将处理 {total_users} 个用户")
        
        # 创建浏览器池
        browser_pool = await self._create_browser_pool(max_browsers)
        
        # 创建信号量控制并发数
        semaphore = asyncio.Semaphore(max_concurrent)
        
        # 存储结果
        results = []
        completed = 0
        start_time = time.time()
        
        async def process_user_with_semaphore(username_data, browser_pool):
            nonlocal completed
            async with semaphore:
                browser = browser_pool[completed % len(browser_pool)]
                page = await browser.new_page()
                
                try:
                    # 设置页面优化
                    await self._optimize_page(page)
                    
                    # 添加随机延迟，避免过于频繁的请求
                    import random
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    
                    # 获取用户详细信息
                    user_details = await self._get_user_details_fast(username_data['username'], page, username_data)
                    
                    if user_details:
                        results.append(user_details)
                        completed += 1
                        
                        # 显示进度
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        remaining = (total_users - completed) / rate if rate > 0 else 0
                        
                        print(f"✅ {completed}/{total_users} - {username_data['username']} - 速度: {rate:.1f}/s - 剩余: {remaining:.0f}s")
                        
                    return user_details
                    
                except Exception as e:
                    completed += 1
                    print(f"❌ {completed}/{total_users} - {username_data['username']} 错误: {e}")
                    return None
                    
                finally:
                    await page.close()
        
        # 创建所有任务
        tasks = [process_user_with_semaphore(username_data, browser_pool) for username_data in usernames]
        
        # 并发执行所有任务
        print(f"🔄 开始并发执行 {len(tasks)} 个任务...")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # 关闭浏览器池
        await self._close_browser_pool(browser_pool)
        
        # 保存结果
        if results:
            enriched_csv_path = await self._save_enriched_csv(results, csv_file_path)
            
            total_time = time.time() - start_time
            avg_speed = len(results) / total_time
            
            print(f"🎉 完成！获取了 {len(results)} 个用户详细信息")
            print(f"📊 总耗时: {total_time:.1f}s, 平均速度: {avg_speed:.1f} users/s")
            
            return enriched_csv_path
        else:
            print("❌ 没有获取到任何用户详细信息")
            return ""

    async def _create_browser_pool(self, max_browsers: int):
        """创建浏览器池"""
        print(f"🌐 创建 {max_browsers} 个浏览器实例...")
        
        playwright = await async_playwright().start()
        browser_pool = []
        
        for i in range(max_browsers):
            browser = await playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding',
                    '--disable-field-trial-config',
                    '--disable-back-forward-cache',
                    '--disable-ipc-flooding-protection',
                    '--memory-pressure-off',
                    '--max_old_space_size=4096'
                ]
            )
            browser_pool.append(browser)
            
        print(f"✅ 浏览器池创建完成")
        return browser_pool

    async def _close_browser_pool(self, browser_pool):
        """关闭浏览器池"""
        print("🔒 关闭浏览器池...")
        for browser in browser_pool:
            await browser.close()

    async def _optimize_page(self, page):
        """优化页面设置"""
        # 轮换用户代理，避免被识别
        import random
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
        ]
        
        await page.set_extra_http_headers({
            'User-Agent': random.choice(user_agents)
        })
        
        # 阻止不必要的资源加载
        await page.route('**/*.{png,jpg,jpeg,gif,svg,webp,ico,css,woff,woff2,ttf,eot}', lambda route: route.abort())
        await page.route('**/analytics.js', lambda route: route.abort())
        await page.route('**/gtag.js', lambda route: route.abort())
        await page.route('**/ads*.js', lambda route: route.abort())

    async def _get_user_details_fast(self, username: str, page, original_data: Dict) -> Optional[Dict]:
        """快速获取用户详细信息"""
        profile_url = f"https://github.com/{username}"
        
        try:
            # 导航到用户页面（增加超时时间）
            await page.goto(profile_url, wait_until="domcontentloaded", timeout=30000)
            
            # 并发获取所有用户信息（只获取表格需要的字段）
            tasks = [
                self._get_display_name_fast(page),
                self._get_bio_fast(page),
                self._get_avatar_fast(page),
                self._get_follower_counts_fast(page),
                self._get_website_fast(page),
                self._get_repos_count_fast(page)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 组合结果 - 只保留表格需要的字段
            user_info = {
                'username': username,
                'display_name': results[0] if not isinstance(results[0], Exception) else '',
                'bio': results[1] if not isinstance(results[1], Exception) else '',
                'avatar_url': results[2] if not isinstance(results[2], Exception) else '',
                'follower_count': results[3][0] if not isinstance(results[3], Exception) and isinstance(results[3], (tuple, list)) else 0,
                'following_count': results[3][1] if not isinstance(results[3], Exception) and isinstance(results[3], (tuple, list)) else 0,
                'public_repos': results[5] if not isinstance(results[5], Exception) else 0,
                'actions': results[4] if not isinstance(results[4], Exception) else '',  # 网站链接放到actions列
                'profile_url': profile_url,
                'platform': 'github',
                'type': 'user',
                'scraped_at': datetime.now().isoformat(),
                'source_user': original_data.get('source_user', ''),
                'source_repo': original_data.get('source_repo', ''),
                'page_number': original_data.get('page_number', '')
            }
            
            return user_info
            
        except Exception as e:
            print(f"❌ 获取 {username} 详细信息时出错: {e}")
            return None

    async def _get_display_name_fast(self, page):
        """快速获取显示名称"""
        selectors = [
            '.js-profile-editable-area .p-name',
            '.js-profile-editable-area h1 span',
            '.js-profile-editable-area h1'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    name = await element.text_content()
                    return name.strip() if name else ''
            except:
                continue
        return ''

    async def _get_bio_fast(self, page):
        """快速获取简介"""
        # 基于你提供的HTML结构，优化选择器顺序
        selectors = [
            # 直接通过data-bio-text属性获取（最可靠）
            '[data-bio-text]',
            # 通过class组合获取
            '.p-note.user-profile-bio.mb-3.js-user-profile-bio',
            '.p-note.user-profile-bio',
            '.js-user-profile-bio',
            '.user-profile-bio',
            '.p-note',
            # 更广泛的选择器
            '.js-profile-editable-area .p-note',
            '.js-profile-editable-area .user-profile-bio',
            '.js-profile-editable-area [data-testid="bio"]',
            '.js-profile-editable-area div[data-testid="user.bio"]',
            'div[data-testid="profile-bio"]',
            # 包含emoji的bio
            '.user-profile-bio > div',
            '.p-note > div'
        ]
        
        for i, selector in enumerate(selectors):
            try:
                element = await page.query_selector(selector)
                if element:
                    # 首先尝试从data-bio-text属性获取
                    if 'data-bio-text' in selector:
                        bio = await element.get_attribute('data-bio-text')
                        if bio and bio.strip():
                            print(f"✅ Bio found with selector {i+1}: {selector} -> {bio}")
                            return bio.strip()
                    
                    # 然后尝试从文本内容获取
                    bio = await element.text_content()
                    if bio and bio.strip():
                        print(f"✅ Bio found with selector {i+1}: {selector} -> {bio}")
                        return bio.strip()
            except Exception as e:
                print(f"❌ Bio selector {i+1} '{selector}' failed: {e}")
                continue
        
        print("❌ No bio found with any selector")
        return ''

    async def _get_avatar_fast(self, page):
        """快速获取头像"""
        selectors = [
            '.js-profile-editable-area img.avatar',
            '.js-profile-editable-area .avatar img'
        ]
        
        for selector in selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    return await element.get_attribute('src') or ''
            except:
                continue
        return ''

    async def _get_follower_counts_fast(self, page):
        """快速获取关注数"""
        try:
            links = await page.query_selector_all('.js-profile-editable-area a')
            follower_count = 0
            following_count = 0
            
            for link in links:
                href = await link.get_attribute('href')
                if href and 'followers' in href:
                    text = await link.text_content()
                    follower_count = self._parse_count(text)
                elif href and 'following' in href:
                    text = await link.text_content()
                    following_count = self._parse_count(text)
            
            return follower_count, following_count
        except:
            return 0, 0



    async def _get_website_fast(self, page):
        """快速获取网站"""
        try:
            link = await page.query_selector('.js-profile-editable-area a[rel="nofollow me"]')
            if link:
                return await link.get_attribute('href') or ''
        except:
            pass
        return ''

    async def _get_repos_count_fast(self, page):
        """快速获取仓库数"""
        try:
            element = await page.query_selector('.js-profile-editable-area .Counter')
            if element:
                count_text = await element.text_content()
                return self._parse_count(count_text)
        except:
            pass
        return 0

    def _parse_count(self, count_str: str) -> int:
        """解析数字字符串"""
        if not count_str:
            return 0
        
        count_str = count_str.strip().replace(',', '')
        
        try:
            if 'k' in count_str.lower():
                return int(float(count_str.lower().replace('k', '')) * 1000)
            elif 'm' in count_str.lower():
                return int(float(count_str.lower().replace('m', '')) * 1000000)
            else:
                return int(count_str)
        except:
            return 0

    async def _read_usernames_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """读取用户名列表"""
        users = []
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    users.append(row)
        except Exception as e:
            print(f"读取CSV文件时出错: {e}")
        return users

    async def _save_enriched_csv(self, users: List[Dict[str, Any]], original_csv_path: str) -> str:
        """保存enriched数据到CSV"""
        base_name = os.path.splitext(os.path.basename(original_csv_path))[0]
        enriched_csv_path = os.path.join(self.data_dir, f"{base_name}_enriched.csv")
        
        if not users:
            return enriched_csv_path
        
        # 定义字段顺序 - 只保留表格需要的字段
        fieldnames = [
            'username', 'display_name', 'bio', 'avatar_url', 'profile_url',
            'platform', 'type', 'follower_count', 'following_count',
            'public_repos', 'actions', 'scraped_at',
            'source_user', 'source_repo', 'page_number'
        ]
        
        try:
            with open(enriched_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)
            
            print(f"✅ 详细信息已保存到: {enriched_csv_path}")
            return enriched_csv_path
            
        except Exception as e:
            print(f"保存CSV文件时出错: {e}")
            return "" 