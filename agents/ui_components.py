import streamlit as st

def render_agent_card(role_name, icon, vote, reasoning, container):
    """
    Renders a single agent's card in the UI.
    """
    color_map = {
        "BUY": "green",
        "STRONG BUY": "green",
        "SELL": "red",
        "REJECT": "red",
        "NEUTRAL": "gray",
        "HOLD": "orange",
        "APPROVED": "blue"
    }
    vote_color = color_map.get(vote, "gray")
    
    with container:
        st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 15px; margin-bottom: 10px;">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px;">
                <span style="font-size: 1.2rem; font-weight: bold; color: white;">{icon} {role_name}</span>
                <span style="background-color: {vote_color}; padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8rem; color: white;">{vote}</span>
            </div>
            <div style="font-size: 0.9rem; color: #ddd; font-style: italic; min-height: 80px;">
                "{reasoning}"
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_committee_decision(result):
    """
    Displays the full committee result.
    result: Output from run_committee_simulation (AgentState dict)
    """
    st.markdown("### 🏛️ Yatırım Komitesi Karar Toplantısı")
    st.markdown("---")
    
    votes = result.get('votes', {})
    reasoning = result.get('reasoning', {})
    final = result.get('final_decision', 'N/A')
    
    # 1. Analysts Row
    c1, c2, c3 = st.columns(3)
    
    render_agent_card("Teknik Analist", "📈", votes.get('technical', 'N/A'), reasoning.get('technical', ''), c1)
    render_agent_card("Temel Analist", "📰", votes.get('fundamental', 'N/A'), reasoning.get('fundamental', ''), c2)
    render_agent_card("Risk Müdürü", "🛡️", votes.get('risk', 'N/A'), reasoning.get('risk', ''), c3)
    
    # 2. Connector / Visual Flow
    st.markdown("""
    <div style="text-align: center; font-size: 2rem; color: #555; margin: 10px 0;">
        ⬇️ ⬇️ ⬇️
    </div>
    """, unsafe_allow_html=True)
    
    # 3. Head Trader Decision
    final_color = "#4CAF50" if "BUY" in final else "#F44336" if "SELL" in final or "REJECT" in final else "#FF9800"
    
    st.markdown(f"""
    <div style="background-color: {final_color}22; border: 2px solid {final_color}; border-radius: 15px; padding: 20px; text-align: center; max-width: 600px; margin: 0 auto;">
        <div style="font-size: 1rem; color: #aaa; margin-bottom: 5px;">HERKESİ DİNLEDİKTEN SONRA...</div>
        <div style="font-size: 2.5rem; font-weight: 800; color: {final_color}; letter-spacing: 1px;">
            {final}
        </div>
        <div style="font-size: 0.9rem; color: #ccc; margin-top: 10px;">
            Head Trader Kararı Kesindir.
        </div>
    </div>
    """, unsafe_allow_html=True)
