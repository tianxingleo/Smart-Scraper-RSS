"""任务队列 - 生产者-消费者模式处理抓取任务"""
import queue
import threading
import logging
from typing import Callable, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class TaskQueue:
    """任务队列管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaskQueue, cls).__new__(cls)
            cls._instance.queue = queue.Queue()
            cls._instance.workers = []
            cls._instance.running = False
        return cls._instance
    
    def start(self, num_workers: int = 2):
        """
        启动工作线程
        
        Args:
            num_workers: 工作线程数量
        """
        if self.running:
            logger.warning("任务队列已在运行")
            return
        
        self.running = True
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"Worker-{i+1}")
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"任务队列已启动，工作线程数: {num_workers}")
    
    def _worker(self):
        """工作线程 - 从队列中取任务并执行"""
        while self.running:
            try:
                # 从队列获取任务，超时1秒
                task_func, args, kwargs = self.queue.get(timeout=1)
                
                logger.info(f"[{threading.current_thread().name}] 开始执行任务")
                
                try:
                    # 执行任务
                    task_func(*args, **kwargs)
                    logger.info(f"[{threading.current_thread().name}] 任务执行成功")
                except Exception as e:
                    logger.error(f"[{threading.current_thread().name}] 任务执行失败: {e}")
                finally:
                    self.queue.task_done()
                    
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"工作线程错误: {e}")
    
    def add_task(self, func: Callable, *args, **kwargs):
        """
        添加任务到队列
        
        Args:
            func: 要执行的函数
            *args: 位置参数
            **kwargs: 关键字参数
        """
        self.queue.put((func, args, kwargs))
        logger.info(f"任务已加入队列，当前队列长度: {self.queue.qsize()}")
    
    def get_queue_size(self):
        """获取队列长度"""
        return self.queue.qsize()
    
    def stop(self):
        """停止任务队列"""
        self.running = False
        # 等待所有任务完成
        self.queue.join()
        logger.info("任务队列已停止")

# 全局任务队列实例
task_queue = TaskQueue()
