from agents.state import AgentState

def head_trader_node(state: AgentState):
    """
    Head Trader (Orchestrator).
    Responsibility: Synthesizes votes and executes the final decision.
    """
    print(f"  [HeadTrader] Komite kararları değerlendiriliyor...")
    
    votes = state.get('votes', {})
    
    tech = votes.get('technical')
    fund = votes.get('fundamental')
    risk = votes.get('risk')
    
    final_decision = "HOLD"
    
    # Decision Logic
    if risk == "REJECT":
        final_decision = "HOLD (Risk Reddedildi)"
    else:
        # If Risk Approved
        if tech == "BUY" and fund == "BUY":
            final_decision = "STRONG BUY"
        elif tech == "BUY" and fund == "NEUTRAL":
            final_decision = "BUY"
        elif tech == "SELL":
            final_decision = "SELL"
        else:
            final_decision = "HOLD"
            
    print(f"  [HeadTrader] NİHAİ KARAR: {final_decision}")
    
    return {"final_decision": final_decision}
