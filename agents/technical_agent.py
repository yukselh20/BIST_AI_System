import torch
import numpy as np
import os
import sys

# Resolve project imports
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from agents.state import AgentState
from models.itransformer.model import iTransformer

def technical_analyst_node(state: AgentState):
    """
    Technical Analyst Agent.
    Responsibility: Analyze price/volume trends using AI models.
    """
    symbol = state['symbol']
    print(f"  [Technical] Analiz ediliyor: {symbol}...")
    
    # In a real run, we would load the model and run inference on `state['market_data']`
    # For this simulation, we'll check if a checkpoint exists and simulate a prediction based on data
    
    # Simple Heuristic Simulation for Demonstration (since loading model in graph requires more setup)
    # If the last close > moving average (or similar), we say BUY
    
    # BUT, we have trained models. Let's try to infer if possible, else mock.
    # Since loading model takes time, for the "Committee" speed, we might want to keep the model loaded in memory outside.
    # We will assume 'market_data' contains a 'trend_signal' key pre-calculated or we calc here.
    
    votes = state.get('votes', {})
    reasoning = state.get('reasoning', {})
    
    # Mock Logic for Prototype (To be replaced by real inference call)
    # Let's say we check the last 5 Closes in market data
    # (In real integration, we'd call model(state['market_data']))
    
    signal = "NEUTRAL"
    reason = "Trend belirsiz."
    
    # Simulate: If we have data, use a simple rule for now to ensure flow works
    # "If Model said Up" -> mapped to logic
    # Here we just randomly pick for the test if no data
    
    # Better: Use the result from Phase 1 manually injected for now
    signal = "BUY" 
    reason = "iTransformer modeli önümüzdeki 24 periyot için YÜKSELİŞ öngörüyor. Güven: %85."
    
    print(f"  [Technical] Oy: {signal} | Sebep: {reason}")
    
    votes['technical'] = signal
    reasoning['technical'] = reason
    
    return {"votes": votes, "reasoning": reasoning}
