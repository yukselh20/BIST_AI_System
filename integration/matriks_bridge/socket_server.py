import socket
import json
import sys
import os
import threading
from datetime import datetime

# Resolve project root absolute path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.append(project_root)

from core.database import SessionLocal, TickData

HOST = '127.0.0.1'
PORT = 5555

def save_to_db(data_dict):
    """
    Saves the parsed market data to the database.
    """
    try:
        session = SessionLocal()
        
        # Parse timestamp from ISO format or use current time if missing
        ts_str = data_dict.get('timestamp')
        if ts_str:
            try:
                # Handle ISO format variations if necessary
                ts = datetime.fromisoformat(ts_str)
            except ValueError:
                ts = datetime.utcnow()
        else:
            ts = datetime.utcnow()

        tick = TickData(
            symbol=data_dict.get('symbol'),
            price=float(data_dict.get('price', 0.0)),
            volume=float(data_dict.get('volume', 0.0)),
            timestamp=ts,
            received_at=datetime.utcnow()
        )
        
        session.add(tick)
        session.commit()
        session.close()
    except Exception as e:
        print(f"[!] Database Error: {e}")
        # Make sure session is closed on error if created
        if 'session' in locals():
            session.close()

def start_server():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"[*] Server listening on {HOST}:{PORT}")
    except Exception as e:
        print(f"[!] Failed to bind server: {e}")
        return

    while True:
        try:
            client_socket, addr = server_socket.accept()
            print(f"[+] Accepted connection from {addr}")
            
            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.daemon = True
            client_handler.start()
            
        except KeyboardInterrupt:
            print("\n[*] Server stopping...")
            break
        except Exception as e:
            print(f"[!] Error accepting connection: {e}")

    server_socket.close()

def handle_client(client_socket):
    buffer = ""
    try:
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            
            try:
                decoded_data = data.decode('utf-8')
                buffer += decoded_data
                
                while "\n" in buffer:
                    message, buffer = buffer.split("\n", 1)
                    if message.strip():
                        process_message(message)
            except UnicodeDecodeError:
                print("[!] Decoding error, skipping chunk")
                continue
                
    except ConnectionResetError:
        print("[-] Connection reset by client")
    except Exception as e:
        print(f"[!] Error handling client: {e}")
    finally:
        client_socket.close()
        print("[-] Connection closed")

def process_message(message_str):
    try:
        data = json.loads(message_str)
        print(f"CANLI VERI ALINDI: {data}")
        
        # --- NEW: Order Book Analysis ---
        # Check if this message contains specific Depth Data (Matriks sends this differently usually)
        if 'bids' in data and 'asks' in data:
            try:
                from core.orderflow import calculate_imbalance
                imbalance = calculate_imbalance(data['bids'], data['asks'])
                # Add to data dict to save to DB (needs DB schema update later) or just log for now
                data['imbalance'] = imbalance
                print(f"[*] Order Book Imbalance: {imbalance:.2f}")
            except ImportError:
                pass # core.orderflow might not be ready in some envs
        # --------------------------------
        
        # Save to DB - simplistic 'fire and forget' in main thread for now (or separate thread if blocking is an issue)
        # For high frequency, a queue + worker thread is better, but per instructions we keep it simple.
        save_to_db(data)
        
    except json.JSONDecodeError:
        print(f"[!] Invalid JSON received: {message_str}")
    except Exception as e:
        print(f"[!] Error processing message: {e}")

if __name__ == "__main__":
    start_server()
