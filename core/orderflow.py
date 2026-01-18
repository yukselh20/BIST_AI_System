import numpy as np

def calculate_imbalance(bids, asks, depth=5):
    """
    Calculates the Order Book Imbalance.
    
    Args:
        bids (list): List of [price, qty] pairs for buy orders.
        asks (list): List of [price, qty] pairs for sell orders.
        depth (int): Number of levels to consider (Standard L2 is 5 or 10).
        
    Returns:
        float: Imbalance Score [-1.0 (Sell Pressure) to 1.0 (Buy Pressure)]
    """
    # Defensive check for empty data
    if not bids or not asks:
        return 0.0
        
    # Take top N levels
    bids = bids[:depth]
    asks = asks[:depth]
    
    total_bid_qty = sum([qty for price, qty in bids])
    total_ask_qty = sum([qty for price, qty in asks])
    
    total_volume = total_bid_qty + total_ask_qty
    
    if total_volume == 0:
        return 0.0
        
    # Formula: (Bid - Ask) / (Bid + Ask)
    imbalance = (total_bid_qty - total_ask_qty) / total_volume
    
    return imbalance

def calculate_weighted_imbalance(bids, asks, depth=5):
    """
    Calculates Imbalance but weights closer levels higher.
    Level 1 (Best Bid/Ask) has more impact than Level 5.
    """
    if not bids or not asks:
        return 0.0
        
    bids = bids[:depth]
    asks = asks[:depth]
    
    weighted_bid_sum = 0
    weighted_ask_sum = 0
    total_weight = 0
    
    # Weights: 1.0, 0.8, 0.6, 0.4, 0.2 ...
    decay = 1.0 / depth
    
    for i in range(min(len(bids), depth)):
        weight = 1.0 - (i * decay)
        weighted_bid_sum += bids[i][1] * weight
        total_weight += weight
        
    for i in range(min(len(asks), depth)):
        weight = 1.0 - (i * decay)
        weighted_ask_sum += asks[i][1] * weight
        
    if (weighted_bid_sum + weighted_ask_sum) == 0:
        return 0.0
        
    imbalance = (weighted_bid_sum - weighted_ask_sum) / (weighted_bid_sum + weighted_ask_sum)
    
    return imbalance
