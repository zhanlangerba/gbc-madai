import requests
import time
import json
from typing import List, Dict
from app.core.config import settings

class SearchTool:
    def __init__(self):
        self.search_service = settings.SEARCH_SERVICE

        if self.search_service == "bocha_ai":
            # 初始化博查AI搜索
            self.api_key = settings.BOCHA_AI_API_KEY
            if not self.api_key:
                raise ValueError("未设置BOCHA_AI_API_KEY环境变量")
            self.base_url = settings.BOCHA_AI_BASE_URL

        elif self.search_service == "baidu_ai":
            # 初始化百度AI搜索
            self.api_key = settings.BAIDU_AI_SEARCH_API_KEY
            if not self.api_key:
                raise ValueError("未设置BAIDU_AI_SEARCH_API_KEY环境变量")

            self.client = OpenAI(
                api_key=self.api_key,
                base_url=settings.BAIDU_AI_SEARCH_BASE_URL
            )
            self.model = settings.BAIDU_AI_SEARCH_MODEL

        elif self.search_service == "serpapi":
            # 初始化SerpAPI
            self.api_key = settings.SERPAPI_KEY
            if not self.api_key:
                raise ValueError("未设置SERPAPI_KEY环境变量")
        else:
            raise ValueError(f"不支持的搜索服务: {self.search_service}")

    def search(self, query: str, num_results: int = 3) -> List[Dict]:
        """执行搜索并返回结构化结果"""
        # 使用配置中的结果数量，如果没有则使用传入的数量
        num_results = settings.SEARCH_RESULT_COUNT or num_results

        if self.search_service == "bocha_ai":
            return self._search_with_bocha_ai(query, num_results)
        elif self.search_service == "baidu_ai":
            return self._search_with_baidu_ai(query, num_results)
        elif self.search_service == "serpapi":
            return self._search_with_serpapi(query, num_results)
        else:
            return []

    def _search_with_bocha_ai(self, query: str, num_results: int) -> List[Dict]:
        """使用博查AI搜索"""
        print(f"使用博查AI搜索: {query}")

        url = f"{self.base_url}/web-search"

        payload = {
            "query": query,
            "freshness": "noLimit",  # 时间范围：oneDay, oneWeek, oneMonth, oneYear, noLimit
            "summary": True,  # 是否显示文本摘要
            "count": min(num_results, 50)  # 返回结果数量，最大50
        }

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=(10, 30)
                )
                response.raise_for_status()

                result = response.json()
                print(f"博查AI搜索成功")

                return self._parse_bocha_ai_results(result, num_results)

            except Exception as e:
                print(f"博查AI搜索失败 (第 {attempt + 1}/{max_retries} 次): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("所有博查AI搜索重试都失败了，返回备用结果")
                    return self._get_fallback_results(query)

        return []

    def _parse_bocha_ai_results(self, data: dict, num_results: int) -> List[Dict]:
        """解析博查AI搜索结果"""
        results = []

        # 检查响应状态
        if data.get('code') != 200:
            print(f"博查AI搜索API错误: {data.get('message', '未知错误')}")
            return []

        # 获取搜索结果
        search_data = data.get('data', {})
        web_pages = search_data.get('webPages', {})
        page_results = web_pages.get('value', [])

        for item in page_results[:num_results]:
            result = {
                'title': item.get('name', ''),
                'url': item.get('url', ''),
                'snippet': item.get('summary', '') or item.get('snippet', '')
            }

            # 确保所有字段都有值
            if not result['title']:
                result['title'] = f"搜索结果 {len(results) + 1}"
            if not result['snippet']:
                result['snippet'] = "暂无摘要信息"

            results.append(result)

        return results

    def _search_with_baidu_ai(self, query: str, num_results: int) -> List[Dict]:
        """使用百度AI搜索"""
        print(f"使用百度AI搜索: {query}")

        max_retries = 3
        for attempt in range(max_retries):
            try:
                # 调用百度AI搜索API - 使用正确的参数格式
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": query}
                    ],
                    stream=False,
                    # 百度AI搜索特有参数 - 使用extra_body传递
                    extra_body={
                        "search_source": "baidu_search_v2",  # 使用V2版本
                        "resource_type_filter": [
                            {"type": "web", "top_k": min(num_results, 20)}  # V2版本最大支持20个结果
                        ],
                        "enable_deep_search": False,  # 不开启深度搜索以节省调用次数
                        "enable_corner_markers": True,  # 开启角标
                        "enable_followup_queries": False,  # 不需要追问
                        "search_mode": "required"  # 强制执行搜索
                    },
                    temperature=0.1  # 低温度保证结果稳定性
                )

                print(f"百度AI搜索API调用完成")

                # 检查是否有错误信息
                if hasattr(response, 'model_extra') and response.model_extra:
                    error_code = response.model_extra.get('code')
                    error_message = response.model_extra.get('message')
                    if error_code:
                        print(f"百度AI搜索API错误: {error_code} - {error_message}")
                        if error_code == 'rpm_rate_limit_exceeded':
                            print("API调用频率超限，等待更长时间后重试...")
                            if attempt < max_retries - 1:
                                wait_time = 10 * (2 ** attempt)  # 更长的等待时间
                                print(f"等待 {wait_time} 秒后重试...")
                                time.sleep(wait_time)
                                continue
                        raise Exception(f"百度AI搜索API错误: {error_code} - {error_message}")

                # 解析响应
                if response.choices and len(response.choices) > 0:
                    choice = response.choices[0]

                    # 尝试多种方式获取搜索结果引用
                    references = []

                    # 方式1: 直接从response获取references
                    if hasattr(response, 'references') and response.references:
                        references = response.references
                        print(f"找到references: {len(references)}个")

                    # 方式2: 从choice中获取references
                    elif hasattr(choice, 'references') and choice.references:
                        references = choice.references
                        print(f"从choice找到references: {len(references)}个")

                    # 方式3: 从message中获取references
                    elif hasattr(choice.message, 'references') and choice.message.references:
                        references = choice.message.references
                        print(f"从message找到references: {len(references)}个")

                    if references:
                        return self._parse_baidu_ai_results(references, num_results)
                    else:
                        # 如果没有references，创建一个基于回答内容的结果
                        content = choice.message.content if choice.message else ""
                        print(f"没有找到references，使用回答内容: {content[:100]}...")

                        if content and len(content.strip()) > 0:
                            return [{
                                'title': f'关于"{query}"的搜索结果',
                                'url': 'https://www.baidu.com/s?wd=' + query.replace(' ', '+'),
                                'snippet': content[:200] + '...' if len(content) > 200 else content
                            }]
                        else:
                            print("回答内容也为空")
                            return []
                else:
                    print("百度AI搜索返回空结果")
                    return []

            except Exception as e:
                print(f"百度AI搜索失败 (第 {attempt + 1}/{max_retries} 次): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    print(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    print("所有百度AI搜索重试都失败了，返回备用结果")
                    return self._get_fallback_results(query)

        return []

    def _parse_baidu_ai_results(self, references: List, num_results: int) -> List[Dict]:
        """解析百度AI搜索的引用结果"""
        results = []

        for ref in references[:num_results]:
            result = {
                'title': ref.get('title', ''),
                'url': ref.get('url', ''),
                'snippet': ref.get('content', '')
            }

            # 确保所有字段都有值
            if not result['title']:
                result['title'] = f"搜索结果 {len(results) + 1}"
            if not result['snippet']:
                result['snippet'] = "暂无摘要信息"

            results.append(result)

        return results

    def _search_with_serpapi(self, query: str, num_results: int) -> List[Dict]:
        """使用SerpAPI搜索（备用方案）"""
        print(f"使用SerpAPI搜索: {query}")

        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": num_results,
            "hl": "zh-CN",
            "gl": "cn"
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                session = requests.Session()
                session.headers.update({
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })

                response = session.get(
                    "https://serpapi.com/search",
                    params=params,
                    timeout=(10, 30),
                    verify=False
                )
                response.raise_for_status()

                return self._parse_serpapi_results(response.json())

            except Exception as e:
                print(f"SerpAPI搜索失败 (第 {attempt + 1}/{max_retries} 次): {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return self._get_fallback_results(query)

        return []

    def _parse_serpapi_results(self, data: dict) -> List[Dict]:
        """解析SerpAPI结果"""
        results = []

        if "organic_results" in data:
            for item in data["organic_results"]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                })

        return results[:settings.SEARCH_RESULT_COUNT]

    def _get_fallback_results(self, query: str) -> List[Dict]:
        """当所有搜索都失败时返回备用结果"""
        print("返回备用搜索结果...")
        return [
            {
                'title': f'关于"{query}"的搜索',
                'url': 'https://www.baidu.com/s?wd=' + query.replace(' ', '+'),
                'snippet': f'由于网络连接问题，无法获取"{query}"的实时搜索结果。建议：1) 检查网络连接 2) 稍后重试 3) 直接访问搜索引擎'
            },
            {
                'title': '搜索服务说明',
                'url': 'https://open.bochaai.com/',
                'snippet': f'当前使用的搜索服务: {self.search_service}。如果遇到问题，请检查API密钥配置或网络连接。'
            },
            {
                'title': '解决方案建议',
                'url': 'https://example.com/help',
                'snippet': '如果问题持续存在，可以尝试：1) 切换搜索服务 2) 检查API配额 3) 联系技术支持'
            }
        ]