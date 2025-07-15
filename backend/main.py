from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import asyncio
from urllib.parse import urlparse
import tempfile
import uuid
from typing import Optional, List, Dict, AsyncGenerator
from datetime import datetime
import json

from scrapers.github_two_stage import GitHubTwoStageScraper as GitHubScraper

app = FastAPI(title="FollowNet API", version="1.0.0")

# 启用CORS以允许前端访问
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://localhost:3003",
    "http://localhost:3004",
    "http://localhost:3005",
    "https://follownet.online"
]

# 添加生产环境URL
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)
    # 同时添加不带www的版本
    if frontend_url.startswith("https://www."):
        allowed_origins.append(frontend_url.replace("https://www.", "https://"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ScrapeRequest(BaseModel):
    url: str
    max_users: Optional[int] = 0  # 0 means use default limit
    unlimited: Optional[bool] = False  # Enable unlimited scraping
    page: Optional[int] = 1  # 添加页码参数

class ScrapeResponse(BaseModel):
    success: bool
    message: str
    platform: Optional[str] = None
    total_extracted: Optional[int] = None
    data: Optional[List[Dict]] = None
    download_url: Optional[str] = None
    current_page: Optional[int] = None  # 当前页码
    has_next_page: Optional[bool] = None  # 是否有下一页
    cache_id: Optional[str] = None  # 缓存ID，用于后续分页请求
    total_followers: Optional[int] = None  # 总followers数量
    total_pages: Optional[int] = None  # 总页数

# 存储爬取结果的内存缓存
scrape_cache = {}

def detect_platform_name(url: str) -> str:
    """检测平台名称用于错误消息"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    
    if 'github.com' in domain:
        return 'GitHub'
    elif 'twitter.com' in domain or 'x.com' in domain:
        return 'Twitter/X'
    elif 'youtube.com' in domain or 'youtu.be' in domain:
        return 'YouTube'
    elif 'instagram.com' in domain:
        return 'Instagram'
    elif 'linkedin.com' in domain:
        return 'LinkedIn'
    elif 'reddit.com' in domain:
        return 'Reddit'
    elif 'tiktok.com' in domain:
        return 'TikTok'
    elif 'facebook.com' in domain:
        return 'Facebook'
    elif 'producthunt.com' in domain:
        return 'Product Hunt'
    elif 'weibo.com' in domain:
        return 'Weibo'
    elif 'news.ycombinator.com' in domain:
        return 'Hacker News'
    elif 'medium.com' in domain:
        return 'Medium'
    elif 'bilibili.com' in domain:
        return 'Bilibili'
    else:
        return domain  # 返回域名作为平台名称

def detect_platform(url: str) -> str:
    """根据URL检测平台类型"""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    if 'github.com' in domain:
        return 'github'
    else:
        platform_name = detect_platform_name(url)
        error_msg = f"Oops! We don't support {platform_name} yet.\n\nI'm an individual developer, and currently only GitHub user scraping is available. This is an open-source project — contributions are welcome on GitHub! Thank you for your understanding and support."
        raise ValueError(error_msg)

@app.get("/")
async def root():
    return {"message": "FollowNet API 正在运行"}

@app.get("/test-github-direct")
async def test_github_direct():
    """直接测试GitHub爬取器"""
    try:
        print("=== 直接测试GitHub爬取器 ===")

        scraper = GitHubScraper()
        url = "https://github.com/connor4312?tab=followers"

        print(f"测试URL: {url}")

        result = await scraper.scrape(url)

        print(f"爬取结果数量: {len(result) if result else 0}")

        if result:
            print(f"前3条结果:")
            for i, item in enumerate(result[:3], 1):
                print(f"  {i}. {item.get('username', 'N/A')} - {item.get('display_name', 'N/A')}")

        return {
            "success": True,
            "total": len(result) if result else 0,
            "sample_data": result[:3] if result else []
        }

    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }



@app.post("/api/scrape", response_model=ScrapeResponse)
async def scrape_followers(request: ScrapeRequest):
    """分页爬取接口"""
    try:
        print(f"开始处理请求: {request.url}, 页码: {request.page}")

        # 检测平台
        platform = detect_platform(request.url)
        print(f"检测到平台: {platform}")

        # 选择对应的爬取器
        if platform == 'github':
            scraper = GitHubScraper()
            print("🐌 使用标准爬虫模式")
        else:
            platform_name = detect_platform_name(request.url)
            error_msg = f"Oops! We don't support {platform_name} yet.\n\nI'm an individual developer, and currently only GitHub user scraping is available. This is an open-source project — contributions are welcome on GitHub! Thank you for your understanding and support."
            raise HTTPException(status_code=400, detail=error_msg)

        print(f"开始执行第{request.page}页爬取，爬取当前页所有用户...")

        # 设置默认值
        page = request.page or 1
        
        # 标准模式 - 使用GitHubScraper
        github_scraper = scraper
        # 检查是否支持分页爬取
        if hasattr(github_scraper, 'scrape_page'):
            # 使用分页爬取
            result = await github_scraper.scrape_page(request.url, page)
            has_next = result.get('has_next_page', False)
            data = result.get('data', [])
        else:
            # 兼容旧版本，只支持第一页
            if page > 1:
                return ScrapeResponse(
                    success=False,
                    message="Oops! This platform doesn't support pagination yet",
                    platform=platform,
                    current_page=page
                )
            # 对于GitHub，使用默认参数
            if platform == 'github' and hasattr(github_scraper, 'scrape'):
                result = await github_scraper.scrape(request.url)
            else:
                result = await github_scraper.scrape(request.url)
            data = result if result else []
            has_next = False

        print(f"第{request.page}页爬取完成，结果数量: {len(data)}")

        if not data or len(data) == 0:
            print("返回失败响应：未找到数据")
            return ScrapeResponse(
                success=False,
                message="Oops! No data found or scraping failed",
                platform=platform,
                current_page=request.page
            )

        # 生成缓存ID
        cache_key = f"{request.url}_{request.page}"
        cache_id = str(uuid.uuid4())
        scrape_cache[cache_id] = {
            'data': data,
            'platform': platform,
            'url': request.url,
            'page': request.page,
            'scraped_at': datetime.now().isoformat()
        }

        print(f"数据已缓存，ID: {cache_id}")

        return ScrapeResponse(
            success=True,
            message=f"成功爬取第{request.page}页 {len(data)} 条数据",
            platform=platform,
            total_extracted=len(data),
            data=data,
            download_url=f"/api/export-csv/{cache_id}",
            current_page=request.page,
            has_next_page=has_next,
            cache_id=cache_id
        )

    except ValueError as e:
        print(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Oops! Scraping failed: {str(e)}")

@app.post("/api/scrape-stream")
async def scrape_stream(request: ScrapeRequest):
    """流式爬取接口 - 边爬边返回数据"""

    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # 发送开始消息
            yield f"data: {json.dumps({'type': 'start', 'message': 'Starting scrape...', 'url': request.url})}\n\n"

            # 检测平台
            try:
                platform = detect_platform(request.url)
                yield f"data: {json.dumps({'type': 'platform', 'platform': platform})}\n\n"
            except ValueError as e:
                # 平台不支持的错误，直接返回原始错误消息
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
                return

            # 创建爬取器 - 目前只支持GitHub
            if platform == 'github':
                scraper = GitHubScraper()
            else:
                platform_name = detect_platform_name(request.url)
                error_msg = f"Oops! We don't support {platform_name} yet.\n\nI'm an individual developer, and currently only GitHub user scraping is available. This is an open-source project — contributions are welcome on GitHub! Thank you for your understanding and support."
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                return

            # 设置默认值
            page = request.page or 1

            # GitHub支持流式爬取（支持无限制爬取）
            if hasattr(scraper, 'scrape_with_progress'):
                # Determine scraping parameters
                max_users = request.max_users or 0
                unlimited = request.unlimited or False
                max_pages = 5 if not unlimited and max_users <= 250 else min(max_users // 50, 100) if max_users > 0 else 5
                
                async for progress_data in scraper.scrape_with_progress(
                    request.url, 
                    max_pages=max_pages,
                    max_users=max_users,
                    unlimited=unlimited
                ):
                    yield f"data: {json.dumps(progress_data)}\n\n"
                    await asyncio.sleep(0.1)  # 小延迟避免前端处理不过来
            else:
                # 普通爬取
                yield f"data: {json.dumps({'type': 'progress', 'message': f'Scraping GitHub data...'})}\n\n"

                if hasattr(scraper, 'scrape_page'):
                    result = await scraper.scrape_page(request.url, page)
                    data = result.get('data', [])
                    has_next = result.get('has_next_page', False)
                else:
                    result = await scraper.scrape(request.url)
                    data = result if result else []
                    has_next = False

                # 发送最终结果
                complete_data = {
                    'type': 'complete',
                    'data': data,
                    'total': len(data),
                    'has_next_page': has_next,
                    'current_page': page,
                    'platform': platform
                }
                yield f"data: {json.dumps(complete_data)}\n\n"

        except Exception as e:
            error_msg = f"Oops! Something went wrong during scraping: {str(e)}"
            yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.post("/api/scrape-and-download")
async def scrape_and_download(request: ScrapeRequest):
    """爬取数据并直接下载CSV文件"""
    try:
        print(f"开始爬取并下载: {request.url}, 页码: {request.page}")

        # 检测平台
        platform = detect_platform(request.url)
        print(f"检测到平台: {platform}")

        # 选择对应的爬取器 - 目前只支持GitHub
        if platform == 'github':
            scraper = GitHubScraper()
        else:
            platform_name = detect_platform_name(request.url)
            error_msg = f"Oops! We don't support {platform_name} yet.\n\nI'm an individual developer, and currently only GitHub user scraping is available. This is an open-source project — contributions are welcome on GitHub! Thank you for your understanding and support."
            raise HTTPException(status_code=400, detail=error_msg)

        # 设置默认值
        page = request.page or 1
        
        print(f"开始执行第{page}页爬取，爬取当前页所有用户...")

        # 检查是否支持分页爬取
        if hasattr(scraper, 'scrape_page'):
            # 使用分页爬取
            result = await scraper.scrape_page(request.url, page)
            has_next = result.get('has_next_page', False)
            data = result.get('data', [])
        else:
            # 兼容旧版本，只支持第一页
            if page > 1:
                raise HTTPException(status_code=400, detail="Oops! This platform doesn't support pagination yet")
            # 对于GitHub，使用默认参数
            result = await scraper.scrape(request.url)
            data = result if result else []
            has_next = False

        print(f"第{page}页爬取完成，结果数量: {len(data)}")

        if not data or len(data) == 0:
            raise HTTPException(status_code=404, detail="Oops! No data found or scraping failed")

        # 直接生成并返回CSV文件
        from urllib.parse import urlparse, quote
        parsed_url = urlparse(request.url)
        url_parts = parsed_url.path.strip('/').split('/')

        if len(url_parts) >= 1:
            identifier = url_parts[0] if url_parts[0] else "unknown"
        else:
            identifier = "unknown"

        csv_filename = f"follownet_{platform}_{identifier}_page{page}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = os.path.join(tempfile.gettempdir(), csv_filename)

        # 保存数据到CSV
        await scraper.save_to_csv(data, csv_path)
        print(f"CSV文件已生成: {csv_path}")

        return FileResponse(
            path=csv_path,
            filename=csv_filename,
            media_type='text/csv',
            headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
        )

    except ValueError as e:
        print(f"ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Oops! Scraping failed: {str(e)}")

@app.get("/api/export-csv/{cache_id}")
async def export_csv(cache_id: str):
    """导出CSV文件"""
    if cache_id not in scrape_cache:
        raise HTTPException(status_code=404, detail="Oops! Data not found or expired")

    cached_data = scrape_cache[cache_id]
    result = cached_data['data']
    platform = cached_data['platform']
    page = cached_data.get('page', 1)

    # 生成CSV文件
    csv_filename = f"follownet_{platform}_page{page}_data_{cache_id}.csv"
    csv_path = os.path.join(tempfile.gettempdir(), csv_filename)

    # 根据平台选择对应的爬取器来保存CSV - 目前只支持GitHub
    if platform == 'github':
        scraper = GitHubScraper()
    else:
        # 对于导出CSV，不需要URL，所以使用通用错误消息
        error_msg = f"Oops! We don't support {platform} yet.\n\nI'm an individual developer, and currently only GitHub user scraping is available. This is an open-source project — contributions are welcome on GitHub! Thank you for your understanding and support."
        raise HTTPException(status_code=400, detail=error_msg)

    # 保存数据到CSV
    await scraper.save_to_csv(result, csv_path)
    print(f"CSV文件已生成: {csv_path}")

    return FileResponse(
        path=csv_path,
        filename=csv_filename,
        media_type='text/csv',
        headers={"Content-Disposition": f"attachment; filename={csv_filename}"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)