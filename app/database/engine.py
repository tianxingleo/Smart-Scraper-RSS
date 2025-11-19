from sqlmodel import SQLModel, create_engine, Session
from app.database.models import Source, ScrapedItem

sqlite_file_name = "data/database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(engine)

def rebuild_database():
    """重建数据库（删除所有表并重新创建）"""
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        yield session
