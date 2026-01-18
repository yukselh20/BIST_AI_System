import socket
import json
import time
import random
from datetime import datetime

HOST = '127.0.0.1'
PORT = 5555

SYMBOLS = ['THYAO', 'ASELS', 'GARAN', 'AKBNK', 'EREGL']

def generate_mock_data():
    """
    Generates a random market data packet.
    """
    symbol = random.choice(SYMBOLS)
    price = round(random.uniform(10.0, 500.0), 2)
    volume = random.randint(1, 1000)
    
    return {
        "symbol": symbol,
        "price": price,
        "volume": volume,
        "timestamp": datetime.now().isoformat()
    }

def run_feeder():
    """
    Connects to the server and sends data continuously.
    """
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"[*] Connecting to {HOST}:{PORT}...")
            client_socket.connect((HOST, PORT))
            print("[+] Connected to server!")

            while True:
                data = generate_mock_data()
                json_data = json.dumps(data) + "\n" # Add newline as delimiter
                
                client_socket.sendall(json_data.encode('utf-8'))
                # print(f"Sent: {data}") # Optional debug print
                
                time.sleep(0.1) # 100ms interval
                
        except ConnectionRefusedError:
            print("[!] Connection refused. Retrying in 2 seconds...")
            time.sleep(2)
        except ConnectionResetError:
            print("[!] Connection lost. Reconnecting...")
            client_socket.close()
            time.sleep(1)
        except Exception as e:
            print(f"[!] Unexpected error: {e}")
            time.sleep(1)
        finally:
             if 'client_socket' in locals():
                client_socket.close()

if __name__ == "__main__":
    run_feeder()
