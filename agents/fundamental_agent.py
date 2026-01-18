from agents.state import AgentState

def fundamental_analyst_node(state: AgentState):
    """
    Fundamental Analyst Agent.
    Responsibility: Analyze news sentiment and macro conditions.
    """
    symbol = state['symbol']
    sentiment = state.get('news_sentiment', 0.0)
    inflation = state['macro_data'].get('inflation_cpi', 0)
    
    print(f"  [Fundamental] Analiz ediliyor: {symbol} (Sentiment: {sentiment:.2f})...")
    
    votes = state.get('votes', {})
    reasoning = state.get('reasoning', {})
    
    signal = "NEUTRAL"
    reason = ""
    
    if sentiment > 0.5:
        signal = "BUY"
        reason = f"Haber akışı oldukça pozitif (Skor: {sentiment:.2f}). Şirket büyüme odaklı haberlerle öne çıkıyor."
    elif sentiment < -0.5:
        signal = "SELL"
        reason = f"Negatif haber baskısı var (Skor: {sentiment:.2f})."
    else:
        signal = "NEUTRAL"
        reason = "Haber akışı durağan veya karmaşık."
    
    # Macro Filter
    if inflation > 50 and signal == "BUY":
        reason += " Ancak yüksek enflasyon ortamı reel getiriyi baskılayabilir."
        
    print(f"  [Fundamental] Oy: {signal} | Sebep: {reason}")
    
    votes['fundamental'] = signal
    reasoning['fundamental'] = reason
    
    return {"votes": votes, "reasoning": reasoning}
