"""
Database Manager
Handles database connection, session management, and initialization
"""
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import config


class DatabaseManager:
    """Singleton database manager for the application"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is None:
            self._initialize_engine()
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine and session factory"""
        # Use StaticPool for SQLite to handle threading better
        self._engine = create_engine(
            config.DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Set to True for SQL debugging
        )
        
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False
        )
    
    def create_tables(self):
        """Create all database tables"""
        from .models import Base
        Base.metadata.create_all(self._engine)
        print("✓ Database tables created successfully")
    
    def get_session(self) -> Session:
        """Get a new database session"""
        return self._session_factory()
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        Usage:
            with db_manager.session_scope() as session:
                session.add(obj)
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def close(self):
        """Close database engine"""
        if self._engine:
            self._engine.dispose()


# Global instance
_db_manager = DatabaseManager()


def get_session() -> Session:
    """
    Convenience function to get a database session
    Usage:
        session = get_session()
        try:
            # do work
            session.commit()
        except:
            session.rollback()
        finally:
            session.close()
    """
    return _db_manager.get_session()


def initialize_database():
    """Initialize database - create tables if they don't exist"""
    _db_manager.create_tables()


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    return _db_manager
