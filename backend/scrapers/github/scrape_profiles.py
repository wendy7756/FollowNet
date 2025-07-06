import asyncio
import csv
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright
import re

class GitHubProfileScraper:
    """GitHub第二阶段：获取用户详细资料信息"""

    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        os.makedirs(self.data_dir, exist_ok=True)

    async def scrape_profiles_from_csv_with_progress(self, csv_file_path: str, max_users: Optional[int] = None, batch_size: int = 5):
        """
        从CSV文件读取用户列表，获取每个用户的详细资料，带进度报告

        Args:
            csv_file_path: 第一阶段生成的CSV文件路径
            max_users: 最大处理用户数，None表示处理所有用户
            batch_size: 批次大小

        Yields:
            包含进度信息的字典
        """
        print(f"🔍 第二阶段：开始从 {csv_file_path} 获取用户详细资料...")

        # 读取第一阶段的用户列表
        usernames = await self._read_usernames_from_csv(csv_file_path)

        if not usernames:
            yield {
                'type': 'error',
                'message': 'No username list found'
            }
            return

        # 限制处理数量（如果指定了max_users）
        if max_users is not None:
            usernames = usernames[:max_users]
        total_users = len(usernames)

        yield {
            'type': 'progress',
            'message': f'Will process {total_users} users',
            'progress': 0,
            'total_count': total_users,
            'processed_count': 0
        }

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        # 设置用户代理
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        enriched_users = []
        processed_count = 0

        try:
            # 分批处理用户
            for i in range(0, len(usernames), batch_size):
                batch = usernames[i:i + batch_size]
                batch_num = i // batch_size + 1

                yield {
                    'type': 'progress',
                    'message': f'Processing batch {batch_num}: {len(batch)} users',
                    'progress': (processed_count / total_users) * 100,
                    'total_count': total_users,
                    'processed_count': processed_count
                }

                for username_data in batch:
                    username = username_data['username']
                    try:
                        yield {
                            'type': 'progress',
                            'message': f'Getting user profile: {username}',
                            'progress': (processed_count / total_users) * 100,
                            'current_user': username,
                            'total_count': total_users,
                            'processed_count': processed_count
                        }

                        user_details = await self._get_user_details(username, page, username_data)
                        if user_details:
                            enriched_users.append(user_details)
                            processed_count += 1

                            yield {
                                'type': 'user_completed',
                                'message': f'✅ Successfully retrieved {username} profile',
                                'progress': (processed_count / total_users) * 100,
                                'current_user': username,
                                'total_count': total_users,
                                'processed_count': processed_count,
                                'user_data': user_details
                            }
                        else:
                            processed_count += 1
                            yield {
                                'type': 'user_failed',
                                'message': f'❌ Failed to retrieve {username} profile',
                                'progress': (processed_count / total_users) * 100,
                                'current_user': username,
                                'total_count': total_users,
                                'processed_count': processed_count
                            }
                    except Exception as e:
                        processed_count += 1
                        yield {
                            'type': 'user_error',
                            'message': f'Error retrieving {username} profile: {e}',
                            'progress': (processed_count / total_users) * 100,
                            'current_user': username,
                            'total_count': total_users,
                            'processed_count': processed_count
                        }
                        continue

                # 批次间暂停
                if i + batch_size < len(usernames):
                    yield {
                        'type': 'progress',
                        'message': 'Pausing between batches...',
                        'progress': (processed_count / total_users) * 100,
                        'total_count': total_users,
                        'processed_count': processed_count
                    }
                    await asyncio.sleep(2)

            # 保存详细资料到新的CSV文件
            yield {
                'type': 'progress',
                'message': f'Saving detailed profiles for {len(enriched_users)} users...',
                'progress': 95,
                'total_count': total_users,
                'processed_count': processed_count
            }

            output_file = await self._save_enriched_csv(enriched_users, csv_file_path)

            yield {
                'type': 'complete',
                'message': f'✅ Stage 2 complete! Retrieved detailed info for {len(enriched_users)} users',
                'progress': 100,
                'total_count': total_users,
                'processed_count': processed_count,
                'output_file': output_file
            }

        except Exception as e:
            yield {
                'type': 'error',
                'message': f'Error during Stage 2 processing: {e}'
            }
        finally:
            await browser.close()
            await playwright.stop()

    async def scrape_profiles_from_csv(self, csv_file_path: str, max_users: Optional[int] = None, batch_size: int = 5) -> str:
        """
        从CSV文件读取用户列表，获取每个用户的详细资料

        Args:
            csv_file_path: 第一阶段生成的CSV文件路径
            max_users: 最大处理用户数
            batch_size: 批次大小

        Returns:
            包含详细资料的CSV文件路径
        """
        print(f"🔍 Stage 2: Starting to get user details from {csv_file_path}...")

        # 读取第一阶段的用户列表
        usernames = await self._read_usernames_from_csv(csv_file_path)

        if not usernames:
            print("没有找到用户名列表")
            return ""

        # 限制处理数量（如果指定了max_users）
        if max_users is not None:
            usernames = usernames[:max_users]
        print(f"将处理 {len(usernames)} 个用户")

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        page = await browser.new_page()

        # 设置用户代理
        await page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

        enriched_users = []

        try:
            # 分批处理用户
            for i in range(0, len(usernames), batch_size):
                batch = usernames[i:i + batch_size]
                print(f"处理批次 {i//batch_size + 1}: {len(batch)} 个用户")

                for username_data in batch:
                    username = username_data['username']
                    try:
                        print(f"正在获取用户资料: {username}")
                        user_details = await self._get_user_details(username, page, username_data)
                        if user_details:
                            enriched_users.append(user_details)
                            print(f"✅ 成功获取 {username} 的资料")
                        else:
                            print(f"❌ 获取 {username} 的资料失败")
                    except Exception as e:
                        print(f"获取 {username} 资料时出错: {e}")
                        continue

                # 批次间暂停
                if i + batch_size < len(usernames):
                    print("批次间暂停...")
                    await asyncio.sleep(2)

            # 保存详细资料到新的CSV文件
            output_file = await self._save_enriched_csv(enriched_users, csv_file_path)
            print(f"✅ 第二阶段完成！获取了 {len(enriched_users)} 个用户的详细资料")

            return output_file

        except Exception as e:
            print(f"第二阶段处理过程中出错: {e}")
            return ""
        finally:
            await browser.close()
            await playwright.stop()

    async def _read_usernames_from_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """从CSV文件读取用户名列表"""
        usernames = []

        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('username'):
                        usernames.append({
                            'username': row['username'],
                            'type': row.get('type', 'user'),
                            'source_user': row.get('source_user', ''),
                            'source_repo': row.get('source_repo', ''),
                            'page_number': row.get('page_number', ''),
                            'scraped_at': row.get('scraped_at', '')
                        })

            print(f"从CSV文件读取到 {len(usernames)} 个用户名")
            return usernames

        except Exception as e:
            print(f"读取CSV文件时出错: {e}")
            return []

    async def _get_user_details(self, username: str, page_obj, original_data: Dict) -> Optional[Dict]:
        """获取用户详细信息"""
        try:
            # 访问用户主页
            user_url = f"https://github.com/{username}"
            await page_obj.goto(user_url, wait_until='networkidle', timeout=15000)

            # 等待页面加载
            await asyncio.sleep(1)

            # 初始化用户信息，保留第一阶段的数据
            user_info = {
                'username': username,
                'display_name': username,
                'bio': '',
                'avatar_url': f"https://github.com/{username}.png",
                'profile_url': user_url,
                'platform': 'github',
                'type': original_data.get('type', 'user'),
                'source_user': original_data.get('source_user', ''),
                'source_repo': original_data.get('source_repo', ''),
                'page_number': original_data.get('page_number', ''),
                'follower_count': 0,
                'following_count': 0,
                'company': '',
                'location': '',
                'website': '',
                'twitter': '',
                'email': '',
                'public_repos': 0,
                'scraped_at': original_data.get('scraped_at', ''),
                'profile_scraped_at': datetime.now().isoformat()
            }

            # 获取显示名
            try:
                name_selectors = [
                    'h1.vcard-names .p-name',
                    '.vcard-fullname',
                    '[data-testid="profile-name"]',
                    '.js-profile-editable-names .p-name'
                ]

                for selector in name_selectors:
                    name_element = await page_obj.query_selector(selector)
                    if name_element:
                        display_name = await name_element.text_content()
                        if display_name and display_name.strip():
                            user_info['display_name'] = display_name.strip()
                            break
            except Exception as e:
                print(f"获取显示名时出错: {e}")

            # 获取bio
            try:
                bio_selectors = [
                    '.p-note .user-profile-bio',
                    '[data-bio-text]',
                    '.js-user-profile-bio',
                    '.user-profile-bio'
                ]

                for selector in bio_selectors:
                    bio_element = await page_obj.query_selector(selector)
                    if bio_element:
                        bio = await bio_element.text_content()
                        if bio and bio.strip():
                            user_info['bio'] = bio.strip()
                            break
            except Exception as e:
                print(f"获取bio时出错: {e}")

            # 获取头像URL
            try:
                avatar_selectors = [
                    '.avatar-user',
                    '.avatar img',
                    '[data-testid="profile-avatar"] img'
                ]

                for selector in avatar_selectors:
                    avatar_element = await page_obj.query_selector(selector)
                    if avatar_element:
                        avatar_url = await avatar_element.get_attribute('src')
                        if avatar_url:
                            user_info['avatar_url'] = avatar_url
                            break
            except Exception as e:
                print(f"获取头像时出错: {e}")

            # 获取follower和following数量
            try:
                # 查找包含followers的链接
                links = await page_obj.query_selector_all('a')
                for link in links:
                    href = await link.get_attribute('href')
                    text = await link.text_content()

                    if href and text:
                        text = text.strip()
                        if f'/{username}?tab=followers' in href or f'/{username}/followers' in href:
                            # 提取数字
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                count_str = numbers[0].replace(',', '')
                                try:
                                    user_info['follower_count'] = int(count_str)
                                except:
                                    pass
                        elif f'/{username}?tab=following' in href or f'/{username}/following' in href:
                            # 提取数字
                            numbers = re.findall(r'[\d,]+', text)
                            if numbers:
                                count_str = numbers[0].replace(',', '')
                                try:
                                    user_info['following_count'] = int(count_str)
                                except:
                                    pass
            except Exception as e:
                print(f"获取关注数据时出错: {e}")

            # 获取公共仓库数量
            try:
                repo_links = await page_obj.query_selector_all('a')
                for link in repo_links:
                    href = await link.get_attribute('href')
                    text = await link.text_content()

                    if href and text and '?tab=repositories' in href:
                        numbers = re.findall(r'[\d,]+', text)
                        if numbers:
                            count_str = numbers[0].replace(',', '')
                            try:
                                user_info['public_repos'] = int(count_str)
                                break
                            except:
                                pass
            except Exception as e:
                print(f"获取仓库数量时出错: {e}")

            # 获取其他资料信息
            try:
                # 公司、位置、网站等信息通常在vcard-details中
                detail_items = await page_obj.query_selector_all('.vcard-details li, .vcard-detail')

                for item in detail_items:
                    text = await item.text_content()
                    if text:
                        text = text.strip()
                        # 检查是否包含位置信息
                        if any(keyword in text.lower() for keyword in ['location', '位置', 'based in']):
                            user_info['location'] = text
                        # 检查是否包含公司信息
                        elif any(keyword in text.lower() for keyword in ['company', '公司', 'work', 'org']):
                            user_info['company'] = text
                        # 检查是否包含网站链接
                        elif 'http' in text.lower():
                            user_info['website'] = text
            except Exception as e:
                print(f"获取详细资料时出错: {e}")

            return user_info

        except Exception as e:
            print(f"获取用户 {username} 详细信息时出错: {e}")
            return None

    async def _save_enriched_csv(self, users: List[Dict[str, Any]], original_csv_path: str) -> str:
        """保存增强后的用户数据到CSV文件"""
        if not users:
            return ""

        # 生成输出文件名
        base_name = os.path.basename(original_csv_path)
        name_parts = base_name.split('_raw.csv')
        if len(name_parts) == 2:
            output_filename = f"{name_parts[0]}_enriched.csv"
        else:
            output_filename = f"enriched_{base_name}"

        output_path = os.path.join(self.data_dir, output_filename)

        # 定义CSV字段
        fieldnames = [
            'username', 'display_name', 'bio', 'avatar_url', 'profile_url',
            'platform', 'type', 'source_user', 'source_repo', 'page_number',
            'follower_count', 'following_count', 'public_repos',
            'company', 'location', 'website', 'twitter', 'email',
            'scraped_at', 'profile_scraped_at'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for user in users:
                # 确保所有字段都存在
                row = {field: user.get(field, '') for field in fieldnames}
                writer.writerow(row)

        print(f"详细资料已保存到: {output_path}")
        return output_path

# 测试函数
async def main():
    scraper = GitHubProfileScraper()

    # 假设已有第一阶段的CSV文件
    csv_file = "/path/to/connor4312_followers_raw.csv"
    if os.path.exists(csv_file):
        result_file = await scraper.scrape_profiles_from_csv(csv_file, max_users=10)
        print(f"结果文件: {result_file}")
    else:
        print("请先运行第一阶段获取用户列表")

if __name__ == "__main__":
    asyncio.run(main())