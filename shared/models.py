from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Contract(Base):
    __tablename__ = 'contracts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    regnum = Column(String(50), unique=True, nullable=False)
    customer_inn = Column(String(12))
    supplier_inn = Column(String(12))
    price = Column(Float)
    sign_date = Column(DateTime)
    okpd2 = Column(String(20))
    description = Column(Text)
    file_path = Column(Text)
    ei_link = Column(String(500))
    status = Column(String(50), default='new')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    insights = relationship("AIInsight", back_populates="contract")


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(500), unique=True, nullable=False)
    source = Column(String(100))
    title = Column(String(500))
    date = Column(DateTime)
    link = Column(String(500))
    content = Column(Text)
    status = Column(String(50), default='new')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    insights = relationship("AIInsight", back_populates="news")


class Hackathon(Base):
    __tablename__ = 'hackathons'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_url = Column(String(500), unique=True, nullable=False)
    title = Column(String(500))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    organizer = Column(String(500))
    topics = Column(Text)
    description = Column(Text)
    status = Column(String(50), default='new')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    insights = relationship("AIInsight", back_populates="hackathon")


class AIInsight(Base):
    __tablename__ = 'ai_insights'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=True)
    news_id = Column(Integer, ForeignKey('news.id'), nullable=True)
    hackathon_id = Column(Integer, ForeignKey('hackathons.id'), nullable=True)
    title = Column(Text)
    description = Column(Text)
    potential_ai_solution = Column(Text)
    detected_keywords = Column(Text)
    confidence_score = Column(Float)
    model_version = Column(String(50))
    source_url = Column(String(500))
    dataset_suggestion = Column(Text)
    status = Column(String(50), default='new')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contract = relationship("Contract", back_populates="insights")
    news = relationship("News", back_populates="insights")
    hackathon = relationship("Hackathon", back_populates="insights")


class AnalyticsLog(Base):
    __tablename__ = 'analytics_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(50), nullable=False)
    source_id = Column(Integer, nullable=False)
    model_used = Column(String(100))
    prompt = Column(Text)
    raw_response = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)