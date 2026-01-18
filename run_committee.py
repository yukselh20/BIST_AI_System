import sys
import os
from langgraph.graph import StateGraph, END

# Resolve project imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from agents.state import AgentState
from agents.technical_agent import technical_analyst_node
from agents.fundamental_agent import fundamental_analyst_node
from agents.risk_agent import risk_manager_node
from agents.head_trader import head_trader_node

def run_committee_simulation(symbol="THYAO"):
    print(f"\n🏛️ YATIRIM KOMİTESİ TOPLANIYOR (LangGraph Simulation) - {symbol}...")
    print("="*60)
    
    # 1. Build the Graph
    workflow = StateGraph(AgentState)
    
    # 2. Add Nodes (Agents)
    workflow.add_node("technical", technical_analyst_node)
    workflow.add_node("fundamental", fundamental_analyst_node)
    workflow.add_node("risk", risk_manager_node)
    workflow.add_node("head_trader", head_trader_node)
    
    # 3. Define Edges (Flow)
    # Start -> Technical & Fundamental (Parallel usually, but sequential here for simplicity)
    workflow.set_entry_point("technical")
    workflow.add_edge("technical", "fundamental")
    workflow.add_edge("fundamental", "risk")
    workflow.add_edge("risk", "head_trader")
    workflow.add_edge("head_trader", END)
    
    # 4. Compile
    committee = workflow.compile()
    
    # 5. Run with Initial State
    # Scenario: THYAO with Good News but High Volatility? Or Good News and Good Tech?
    initial_state = {
        "symbol": symbol,
        "market_data": {}, # Mocked inside agents
        "macro_data": {"inflation_cpi": 65},
        "news_sentiment": 0.85, # Strong Positive News
        "votes": {},
        "reasoning": {}
    }
    
    # Execute the graph
    result = committee.invoke(initial_state)
    
    return result

if __name__ == "__main__":
    result = run_committee_simulation("THYAO")
    print("="*60)
    print(f"🏁 KOMİTE SONUCU: {result.get('final_decision')}")
    print("="*60)
    print("Detaylı Rapor:")
    for role, reason in result['reasoning'].items():
        print(f"- {role.upper()}: {reason}")
