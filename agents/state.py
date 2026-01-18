from typing import TypedDict, Annotated, List, Dict, Any
import operator

class AgentState(TypedDict):
    """
    The shared state of the Investment Committee.
    All agents read from and write to this state.
    """
    # 1. Context: What differents agents have to work with
    symbol: str
    market_data: Dict[str, Any] # OHLCV, Indicators
    macro_data: Dict[str, Any]  # Inflation, Rates, USD
    news_sentiment: float       # -1.0 to 1.0 (from ABSA/RAG)
    
    # 2. Dialogue: Agents talking to each other (Optional for now)
    messages: List[str]
    
    # 3. Votes/Signals: Each agent puts their vote here
    # Keys: 'technical', 'fundamental', 'risk'
    # Values: 'BUY', 'SELL', 'NEUTRAL', 'REJECT' (for Risk)
    votes: Dict[str, str]
    
    # 4. Reasonings: Explanations for votes
    reasoning: Dict[str, str]
    
    # 5. Final Decision (Made by Head Trader)
    final_decision: str
    final_confidence: float
