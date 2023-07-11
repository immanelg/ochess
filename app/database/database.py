from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app import environment

engine = create_async_engine(url=environment.DATABASE_URL)
get_session = async_sessionmaker(bind=engine, expire_on_commit=False)
