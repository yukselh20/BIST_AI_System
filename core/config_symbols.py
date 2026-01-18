# Master list of BIST stocks used in the project
# This file ensures consistency between Data Feeder, Bot, and Dashboard.

ALL_SYMBOLS = [
    # Bank & Insurance
    'GARAN', 'ISCTR', 'AKBNK', 'YKBNK', 'VAKBN', 'HALKB', 'TSKB',
    
    # Industry & Holding
    'KCHOL', 'SAHOL', 'TKFEN', 'ALARK', 'SISE', 'ENKAI',
    
    # Energy
    'TUPRS', 'PETKM', 'ODAS', 'ASTOR', 'SASA', 'EUPWR', 'KONTR', 'ENJSA',
    
    # Transport
    'THYAO', 'PGSUS', 'TAVHL', 
    
    # Tech & Defense
    'ASELS', 'KAREL', 'TCELL', 'TTKOM', 'VESTL',
    
    # Metal & Auto
    'EREGL', 'KRDMD', 'FROTO', 'TOASO', 'CIMSA', 'OTKAR',
    
    # Retail & Food
    'BIMAS', 'MGROS', 'SOKM', 'HEKTS', 'KOZAL', 'EKGYO'
]

# Sort alphabetically for better UI presentation
ALL_SYMBOLS.sort()
