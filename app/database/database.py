from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.environment import settings

engine = create_async_engine(url=str(settings.DATABASE_URL))
get_session = async_sessionmaker(bind=engine, expire_on_commit=False)
