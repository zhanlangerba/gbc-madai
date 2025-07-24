import aiohttp
import asyncio
import time
from pathlib import Path
from loguru import logger
import random
from tqdm import tqdm
import json
from datetime import datetime
import psutil
import GPUtil

# 配置日志
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
logger.add(
    "logs/benchmark.log",
    rotation="100 MB",
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {message}"
)

"""
关键指标:
1. 吞吐量 (Throughput)：
吞吐量是指单位时间内系统能够处理的请求数量或数据量。通常以请求/秒 (requests per second) 或 tokens/秒 (tokens per second) 来衡量。
吞吐量反映了系统的处理能力，越高的吞吐量意味着系统在给定时间内能够处理更多的请求。

对于大模型服务来说，每秒生成的 Token 数量就可以被视为系统的吞吐量。


2. 并发 (Concurrency)
并发是指系统在同一时间内能够处理的请求数量。它表示系统的并行处理能力。
高并发意味着系统可以同时处理多个请求，这通常会提高吞吐量，但是会降低单个请求的生成时间。


1. 尽可能保证生成的token数量保持一致，通过num_predict参数来控制
2. 



1. 并发会导致单个请求的处理时间变长
2. 因为是并行处理，虽然单个请求时间变成，但是系统整体吞吐量会得到提升
"""

# 测试问题列表
questions = [
    # 科学解释类问题
    "为什么天空是蓝色的？", 
    "为什么我们会做梦？",
    "为什么海水是咸的？",
    "为什么树叶会变色？",
    "为什么鸟儿会唱歌？",
    
    # 编程相关问题
    "解释什么是Python中的装饰器？",
    "什么是面向对象编程？",
    "如何处理Python中的异常？",
    "解释什么是递归函数？",
    "什么是设计模式？",
    
    # 数学问题
    "解释什么是傅里叶变换？",
    "什么是微积分？",
    "解释什么是线性代数？",
    "什么是概率论？",
    "解释什么是统计学？",
    
    # AI/ML问题
    "什么是神经网络？",
    "解释什么是深度学习？",
    "什么是机器学习？",
    "解释什么是强化学习？",
    "什么是自然语言处理？",
    
    # 哲学问题
    "什么是意识？",
    "为什么我们存在？",
    "什么是自由意志？",
    "解释什么是道德？",
    "什么是知识？"
]

class OllamaBenchmark:
    def __init__(self, url: str, model: str):
        self.url = url
        self.model = model
        
    async def single_request(self, session: aiohttp.ClientSession) -> dict:
        """发送单个请求并计算性能指标"""
        try:
            # 随机选择一个问题
            prompt = random.choice(questions)
            
            # 调用 ollama 的 generate 接口
            async with session.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "keep_alive": "5m",  # 保持模型加载5分钟
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 300,  # 限制生成token数量
                    }
                }
            ) as response:
                result = await response.json()
                # 从响应中获取性能指标
                eval_count = result.get("eval_count", 0)  # 生成的token数
                eval_duration = result.get("eval_duration", 0)  # 生成时间(纳秒)
                total_duration = result.get("total_duration", 0)  # 总时间(纳秒)
                
                # 计算 tokens/second
                tokens_per_second = (eval_count / eval_duration * 1e9) if eval_duration > 0 else 0
                
                return {
                    "success": True,
                    "eval_count": eval_count,
                    "eval_duration_seconds": eval_duration / 1e9,
                    "total_duration_seconds": total_duration / 1e9,
                    "tokens_per_second": tokens_per_second
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def test_single_request(self, num_tests: int = 5):
        """测试单个请求的性能"""
        logger.info("开始测试单个请求性能...")
        
        async with aiohttp.ClientSession() as session:
            results = []
            for i in range(num_tests):
                logger.info(f"执行测试 {i+1}/{num_tests}")
                result = await self.single_request(session)
                if result["success"]:
                    results.append(result)
                    logger.info(
                        f"测试 {i+1} 结果:\n"
                        f"- 生成的token数: {result['eval_count']}\n"
                        f"- 生成时间: {result['eval_duration_seconds']:.2f}秒\n"
                        f"- 总时间: {result['total_duration_seconds']:.2f}秒\n"
                        f"- 每秒生成token数: {result['tokens_per_second']:.2f}"
                    )
                await asyncio.sleep(2)  # 冷却时间，短时间频繁请求可能导致过载
            
            if results:
                avg_tokens = sum(r["eval_count"] for r in results) / len(results)
                avg_gen_time = sum(r["eval_duration_seconds"] for r in results) / len(results)
                avg_total_time = sum(r["total_duration_seconds"] for r in results) / len(results)
                avg_tps = sum(r["tokens_per_second"] for r in results) / len(results)
                
                logger.info(f"\n{len(results)}次成功测试的平均性能:")
                logger.info(f"- 平均token数: {avg_tokens:.2f}")
                logger.info(f"- 平均生成时间: {avg_gen_time:.2f}秒")
                logger.info(f"- 平均总时间: {avg_total_time:.2f}秒")
                logger.info(f"- 平均每秒token数: {avg_tps:.2f}")
                
                return {
                    "avg_tokens": avg_tokens,
                    "avg_generation_time": avg_gen_time,
                    "avg_total_time": avg_total_time,
                    "avg_tokens_per_second": avg_tps,
                    "individual_results": results
                }

    async def test_concurrent_requests(self, concurrent_requests: int, total_requests: int):
        """使用信号量测试并发性能"""
        logger.info(f"开始测试 {concurrent_requests} 并发请求，共 {total_requests} 个请求...")
        
        # 控制并发的工具。它的作用是限制同时执行的协程数量，以防止系统过载。
        sem = asyncio.Semaphore(concurrent_requests)
        
        async def bounded_request(session):
            async with sem:
                result = await self.single_request(session)
                # 每个请求后等待一小段时间
                await asyncio.sleep(0.5)  # 500ms 间隔
                return result
        
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            
            # 创建所有任务
            tasks = []
            # 使用tqdm显示进度条
            with tqdm(total=total_requests, desc="处理请求") as pbar:
                # 创建任务
                for _ in range(total_requests):
                    # 异步创建任务
                    task = asyncio.create_task(bounded_request(session))
                    # 任务完成后更新进度条
                    task.add_done_callback(lambda _: pbar.update(1))
                    tasks.append(task)
                
                # 等待所有任务完成
                responses = await asyncio.gather(*tasks)
            
            end_time = time.time()
            
            # 计算统计信息
            successful = [r for r in responses if r["success"]]
            if successful:
                total_tokens = sum(r["eval_count"] for r in successful)
                avg_gen_time = sum(r["eval_duration_seconds"] for r in successful) / len(successful)
                avg_total_time = sum(r["total_duration_seconds"] for r in successful) / len(successful)
                avg_tps = sum(r["tokens_per_second"] for r in successful) / len(successful)
                actual_time = end_time - start_time
                
                results = {
                    "concurrent_requests": concurrent_requests,
                    "total_requests": total_requests,
                    "success_rate": len(successful) / total_requests,
                    "total_tokens": total_tokens,
                    "average_generation_time": avg_gen_time,
                    "average_total_time": avg_total_time,
                    "average_tokens_per_second": avg_tps,
                    "actual_total_time": actual_time,
                    "system_throughput": total_tokens / actual_time
                }
                
                logger.info("\n并发测试结果:")
                logger.info(f"- 成功率: {len(successful)}/{total_requests}")
                logger.info(f"- 总token数: {total_tokens}")
                logger.info(f"- 平均生成时间: {avg_gen_time:.2f}秒")
                logger.info(f"- 平均总时间: {avg_total_time:.2f}秒")
                logger.info(f"- 平均每秒token数: {avg_tps:.2f}")
                logger.info(f"- 实际总耗时: {actual_time:.2f}秒")
                logger.info(f"- 系统整体吞吐量: {results['system_throughput']:.2f} tokens/s")
                
                return results
            return None

    async def check_system_health(self) -> tuple[bool, dict]:
        """检查系统健康状态"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            metrics = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "gpu_info": []
            }
            
            # 检查 CPU 和内存
            is_healthy = (
                cpu_percent < 90 and    
                memory_percent < 90      
            )
            
            # 只在资源接近阈值时打印警告
            if cpu_percent > 85:
                logger.warning(f"CPU 使用率较高: {cpu_percent:.1f}%")
            if memory_percent > 85:
                logger.warning(f"内存使用率较高: {memory_percent:.1f}%")
            
            # GPU 检查
            try:
                import subprocess
                result = subprocess.run(
                    ['nvidia-smi', '--query-gpu=index,memory.used,memory.total,memory.free', '--format=csv,noheader,nounits'],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        index, used, total, free = map(float, line.split(','))
                        memory_percent = (used / total) * 100
                        
                        metrics["gpu_info"].append({
                            "id": int(index),
                            "memory_used": used,
                            "memory_total": total,
                            "memory_free": free,
                            "memory_percent": memory_percent
                        })
                        
                        # 只在 GPU 显存使用率高时打印警告
                        if memory_percent > 85:
                            logger.warning(f"GPU {int(index)} 显存使用率较高: {memory_percent:.1f}%")
                        
                        if memory_percent > 90:
                            is_healthy = False
                            
            except Exception as e:
                logger.error(f"获取GPU信息时出错: {e}")
            
            return is_healthy, metrics
            
        except Exception as e:
            logger.error(f"检查系统状态时出错: {e}")
            return False, {}

    async def find_max_concurrency(self, start_concurrent: int = 1, max_concurrent: int = 20, 
                                 requests_per_test: int = 5, success_rate_threshold: float = 0.8,
                                 latency_threshold: float = 10.0):
        """通过逐步增加并发数来寻找系统极限"""
        logger.info("\n=== 开始寻找最大并发数 ===")
        
        results = []
        optimal_concurrent = 0
        max_throughput = 0
        consecutive_failures = 0  # 连续失败计数
        
        for concurrent in range(start_concurrent, max_concurrent + 1):
            # 每轮测试前检查系统状态
            is_healthy, metrics = await self.check_system_health()
            if not is_healthy:
                logger.warning("\n系统负载过高，立即停止测试")
                # 等待系统恢复
                await asyncio.sleep(30)
                break
                
            # 如果 CPU 或内存使用率超过 90%，立即停止
            if metrics["cpu_percent"] > 90 or metrics["memory_percent"] > 90:
                logger.warning("\n系统资源接近极限，紧急停止")
                break
            
            logger.info(f"\n测试并发数: {concurrent}")
            
            # 运行并发测试
            result = await self.test_concurrent_requests(concurrent, requests_per_test)
            
            if not result:
                consecutive_failures += 1
                if consecutive_failures >= 2:  # 连续失败2次就停止
                    logger.warning("连续测试失败，停止测试")
                    break
                continue
            else:
                consecutive_failures = 0  # 重置失败计数
            
            results.append(result)
            
            # 检查是否达到系统极限
            success_rate = result["success_rate"]
            avg_latency = result["average_generation_time"]
            throughput = result["system_throughput"]
            
            logger.info(f"成功率: {success_rate:.2%}")
            logger.info(f"平均延迟: {avg_latency:.2f}秒")
            logger.info(f"系统吞吐量: {throughput:.2f} tokens/s")
            
            # 更新最优并发数
            if (success_rate >= success_rate_threshold and 
                avg_latency <= latency_threshold and 
                throughput > max_throughput):
                optimal_concurrent = concurrent
                max_throughput = throughput
            
            # 检查是否应该停止测试
            if (success_rate < success_rate_threshold or 
                avg_latency > latency_threshold):
                logger.info(f"\n检测到系统瓶颈:")
                logger.info(f"- 成功率低于 {success_rate_threshold:.0%}" if success_rate < success_rate_threshold else "")
                logger.info(f"- 延迟超过 {latency_threshold}秒" if avg_latency > latency_threshold else "")
                break
            
            # 每次测试后检查系统状态并等待恢复
            is_healthy, _ = await self.check_system_health()
            if not is_healthy:
                logger.warning("系统需要更多恢复时间")
                await asyncio.sleep(30)  # 系统压力大时多等待
            else:
                await asyncio.sleep(5)   # 正常等待
        
        logger.info("\n=== 并发测试结果总结 ===")
        logger.info(f"最优并发数: {optimal_concurrent}")
        logger.info(f"最大吞吐量: {max_throughput:.2f} tokens/s")
        
        return {
            "optimal_concurrent": optimal_concurrent,
            "max_throughput": max_throughput,
            "all_results": results
        }

    async def check_model_exists(self, session: aiohttp.ClientSession) -> bool:
        """检查模型是否已经存在"""
        try:
            # 修改为 GET 请求
            async with session.get(f"{self.url}/api/tags") as response:
                if response.status != 200:
                    logger.error(f"获取模型列表失败: {response.status}")
                    return False
                    
                data = await response.json()
                models = data.get("models", [])
                logger.info(f"已安装的模型: {[m['name'] for m in models]}")
                return any(m["name"] == self.model for m in models)
        except Exception as e:
            logger.error(f"检查模型时出错: {e}")
            return False

    async def pull_model(self, session: aiohttp.ClientSession) -> bool:
        """拉取模型"""
        try:
            logger.info(f"开始拉取模型: {self.model}")
            
            async with session.post(
                f"{self.url}/api/pull",
                json={
                    "name": self.model,
                    "stream": False
                }
            ) as response:
                if response.status != 200:
                    logger.error(f"拉取模型失败: {response.status}")
                    return False
                
                # 读取流式响应
                async for line in response.content:
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        status = data.get("status", "")
                        
                        if "downloading" in status:
                            # 显示下载进度
                            total = data.get("total", 0)
                            completed = data.get("completed", 0)
                            if total > 0:
                                progress = (completed / total) * 100
                                logger.info(f"下载进度: {progress:.1f}% ({completed}/{total} bytes)")
                        else:
                            logger.info(f"模型拉取状态: {status}")
                            
                        if status == "success":
                            logger.info(f"模型 {self.model} 拉取成功")
                            return True
                            
                    except json.JSONDecodeError:
                        continue
                        
                return False
                
        except Exception as e:
            logger.error(f"拉取模型时出错: {e}")
            return False

    async def ensure_model_available(self) -> bool:
        """确保模型可用"""
        async with aiohttp.ClientSession() as session:
            # 检查模型是否存在
            if await self.check_model_exists(session):
                logger.info(f"模型 {self.model} 已存在")
                return True
                
            # 拉取模型
            logger.info(f"模型 {self.model} 不存在，开始拉取")
            return await self.pull_model(session)

    async def unload_model(self, session: aiohttp.ClientSession) -> bool:
        """通过设置 keep_alive=0 来卸载模型"""
        try:
            logger.info(f"准备卸载模型: {self.model}")
            
            # 发送一个 keep_alive=0 的请求来卸载模型
            async with session.post(
                f"{self.url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": "",  # 可以直接发送空字符串
                    "stream": False,
                    "keep_alive": 0,  # 使用完立即卸载
                }
            ) as response:
                if response.status == 200:
                    logger.info(f"模型 {self.model} 已卸载")
                    return True
                else:
                    logger.error(f"卸载模型失败: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"卸载模型时出错: {e}")
            return False

async def main():
    benchmark = OllamaBenchmark(
        url="http://192.168.110.131:11434",  # 这里替换成实际的ollama endpoint
        model="deepseek-r1:1.5b"             # 这里替换成实际要进行测试的模型名称
    )
    
    try:
        # 确保模型可用
        if not await benchmark.ensure_model_available():
            logger.error("模型准备失败，退出测试")
            return
            
        # 先检查系统状态
        is_healthy, metrics = await benchmark.check_system_health()
        if not is_healthy:
            logger.error("系统资源不足，无法开始测试")
            return
        
        # 1. 测试单个请求的基准性能
        logger.info("\n=== 开始单请求性能测试 ===")
        single_results = await benchmark.test_single_request(num_tests=3)
        
        # 使用保守的并发测试参数
        concurrency_results = await benchmark.find_max_concurrency(
            start_concurrent=2,          # 从2开始
            max_concurrent=5,            # 最多只测到5个并发
            requests_per_test=10,         # 每轮只测10个请求
            success_rate_threshold=0.95,  # 成功率要求提高到95%
            latency_threshold=5.0        # 延迟阈值降低到5秒
        )
        
        
        # 保存结果
        results = {
            "test_info": {
                "timestamp": datetime.now().isoformat(),
                "model": benchmark.model,
                "server": benchmark.url
            },
            "single_request_performance": single_results,
            "concurrency_test": concurrency_results
        }
        
        filename = f"logs/benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n测试结果已保存到: {filename}")

    finally:

        
        # 测试完成后卸载模型
        async with aiohttp.ClientSession() as session:
            await benchmark.unload_model(session)

        # 测试完成后删除
        # async with aiohttp.ClientSession() as session:
        #     try:
        #         await session.delete(f"{benchmark.url}/api/delete", 
        #                            json={"name": benchmark.model})
        #         logger.info(f"已卸载模型: {benchmark.model}")
        #     except Exception as e:
        #         logger.error(f"卸载模型时出错: {e}"

if __name__ == "__main__":
    asyncio.run(main()) 