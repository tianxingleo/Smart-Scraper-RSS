"""定时任务调度器 - 使用 APScheduler 实现自动抓取"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SchedulerManager:
    """调度器管理器 - 单例模式"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SchedulerManager, cls).__new__(cls)
            cls._instance.scheduler = BackgroundScheduler()
            cls._instance.scheduler.start()
            logger.info("调度器已启动")
        return cls._instance
    
    def add_job(self, job_id: str, func, minutes: int, **kwargs):
        """
        添加定时任务
        
        Args:
            job_id: 任务唯一标识
            func: 要执行的函数
            minutes: 执行间隔（分钟）
            **kwargs: 传递给函数的参数
        """
        try:
            # 如果任务已存在，先移除
            if self.scheduler.get_job(job_id):
                self.remove_job(job_id)
            
            # 添加新任务
            self.scheduler.add_job(
                func=func,
                trigger=IntervalTrigger(minutes=minutes),
                id=job_id,
                kwargs=kwargs,
                replace_existing=True
            )
            logger.info(f"添加定时任务: {job_id}, 间隔: {minutes}分钟")
            return True
        except Exception as e:
            logger.error(f"添加任务失败: {job_id}, 错误: {e}")
            return False
    
    def remove_job(self, job_id: str):
        """移除定时任务"""
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"移除定时任务: {job_id}")
            return True
        except Exception as e:
            logger.error(f"移除任务失败: {job_id}, 错误: {e}")
            return False
    
    def get_jobs(self):
        """获取所有任务"""
        return self.scheduler.get_jobs()
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("调度器已关闭")

# 全局调度器实例
scheduler_manager = SchedulerManager()
