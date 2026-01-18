from agents.state import AgentState

def risk_manager_node(state: AgentState):
    """
    Risk Manager Agent.
    Responsibility: The Gatekeeper. Validates if the trade is safe.
    """
    print(f"  [Risk] Risk kontrolleri yapılıyor...")
    
    votes = state.get('votes', {})
    reasoning = state.get('reasoning', {})
    
    # 1. Advanced Risk Check (VaR)
    try:
        from core.portfolio_optimizer import PortfolioOptimizer
        import pandas as pd
        import numpy as np
        
        # Mocking Portfolio Data for Simulation
        # In real system, this comes from `state` or database
        mock_prices = pd.DataFrame(np.random.normal(10, 0.1, size=(50, 1)), columns=['Price'])
        mock_weights = {'Price': 1.0}
        
        opt = PortfolioOptimizer()
        # Calculate VaR for 1M TL capital
        var_amount, var_pct = opt.calculate_var(1_000_000, mock_weights, mock_prices)
        
        print(f"  [Risk] VaR Hesaplanıyor... (Beklenen Kayıp: %{var_pct*100:.2f})")
        
        # Limit: Do not accept if daily VaR > 2%
        if abs(var_pct) > 0.02:
            decision = "REJECT" 
            reason = f"Portföy riski (VaR: %{var_pct*100:.2f}) kabul edilebilir sınırın (%2) üzerinde."
            
    except Exception as e:
        print(f"  [Risk] VaR Hatası: {e}")
        # Default safety
        decision = "REJECT"
        reason = "Risk motoru hatası."
        
    print(f"  [Risk] Karar: {decision} | Sebep: {reason}")
    
    votes['risk'] = decision
    reasoning['risk'] = reason
    
    return {"votes": votes, "reasoning": reasoning}
