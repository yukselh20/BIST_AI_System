from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import os
from datetime import datetime

# Define database file path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'data', 'database', 'market_data.db')
DB_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class TickData(Base):
    __tablename__ = 'tick_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    volume = Column(Float, nullable=True)
    timestamp = Column(DateTime)
    received_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Tick(stock='{self.symbol}', price={self.price}, time='{self.timestamp}')>"

class MacroData(Base):
    """
    Stores macroeconomic indicators (Inflation, Interest Rate, USDTRY, etc.)
    frequency: 'M' (Monthly), 'W' (Weekly), 'D' (Daily)
    """
    __tablename__ = 'macro_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    indicator_name = Column(String, index=True) # e.g. 'inflation_cpi', 'policy_rate'
    value = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow) # When the data belongs to (e.g. 2023-11-01)
    frequency = Column(String) 
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Macro('{self.indicator_name}', value={self.value}, date='{self.timestamp}')>"

class FundFlow(Base):
    """
    Stores Institutional Fund data (TEFAS).
    """
    __tablename__ = 'fund_flow'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fund_code = Column(String, index=True) # e.g. 'MAC'
    stock_allocation_pct = Column(Float) # 45.5 -> 45.5%
    total_value = Column(Float) # Total AUM
    date = Column(DateTime) # Data Release Date
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Fund('{self.fund_code}', stock%={self.stock_allocation_pct}, date='{self.date}')>"

def init_db():
    """Initializes the database by creating tables."""
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    Base.metadata.create_all(engine)

# Auto-initialize when imported, or can be called explicitly
init_db()
