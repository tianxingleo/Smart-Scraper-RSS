"""全局配置管理"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "Smart Scraper RSS"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///data/database.db"
    
    # AI API 配置
    DEEPSEEK_API_KEY: Optional[str] = None
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 爬虫配置
    BROWSER_HEADLESS: bool = False
    BROWSER_USER_DATA_PATH: str = "./data/browser_profile"
    DEFAULT_SCRAPE_FREQUENCY: int = 60  # 分钟
    PROXY_SERVER: Optional[str] = None  # 代理服务器地址，例如 "http://127.0.0.1:7890"
    
    # UI 配置
    UI_PORT: int = 8080
    UI_NATIVE_MODE: bool = False  # Web 模式，避免需要 pywebview
    UI_WINDOW_SIZE: tuple = (1200, 800)
    
    # RSS 配置
    RSS_FEED_TITLE: str = "Smart Scraper RSS Feed"
    RSS_FEED_LINK: str = "http://localhost:8080"
    RSS_FEED_DESCRIPTION: str = "智能内容聚合 RSS"
    RSS_MAX_ITEMS: int = 50
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 全局配置实例
settings = Settings()
