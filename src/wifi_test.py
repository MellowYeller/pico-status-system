import network
import socket
import time
from machine import Pin

try:
    import config
except ImportError:
    print("Create a config.py file with your credentials")
    # Provide some default or fallback behavior, or halt execution
    import sys
    sys.exit()

# Set up onboard LED
led = Pin("LED", Pin.OUT)

# Connect to WiFi
def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    # Set power mode to improve connection reliability
    wlan.config(pm = 0xa11140)
    
    print(f"Connecting to {config.WIFI_SSID}")
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    
    # Wait for connection with timeout
    max_wait = 10
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print("Waiting for connection...")
        time.sleep(1)
    
    # Handle connection result
    if wlan.status() != 3:
        print("Network connection failed")
        return None
    else:
        print("Connected")
        status = wlan.ifconfig()
        print(f"IP address: {status[0]}")
        return status[0]

# Define available commands and their functions
def execute_command(command):
    if command == "led_on":
        led.value(1)
        return "LED turned ON"
    elif command == "led_off":
        led.value(0)
        return "LED turned OFF"
    elif command == "led_blink":
        for _ in range(5):
            led.toggle()
            time.sleep(0.5)
        return "LED blinked 5 times"
    elif command.startswith("echo="):
        return f"Echo: {command.split('=')[1]}"
    else:
        return f"Unknown command: {command}"

# Set up web server
def start_server(ip):
    # Open socket
    addr = (ip, 80)
    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    
    print(f"Listening on {ip}:80")
    
    # Listen for connections
    while True:
        try:
            client, addr = s.accept()
            print(f"Client connected from {addr}")
            
            # Get request
            request = client.recv(1024)
            request = request.decode('utf-8')
            print(f"Request: {request}")
            
            # Parse request
            command = None
            if "GET /cmd/" in request:
                command = request.split("/cmd/")[1].split(" ")[0]
            
            # Process command
            if command:
                result = execute_command(command)
                response = f"HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n<html><body><h1>Pico W2 Command Server</h1><p>{result}</p></body></html>"
            else:
                response = """HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n
                <html>
                <body>
                <h1>Pico W2 Command Server</h1>
                <p>Send commands via /cmd/COMMAND</p>
                <p>Available commands:</p>
                <ul>
                <li><a href="/cmd/led_on">LED On</a></li>
                <li><a href="/cmd/led_off">LED Off</a></li>
                <li><a href="/cmd/led_blink">LED Blink</a></li>
                <li><a href="/cmd/echo=hello">Echo</a></li>
                </ul>
                </body>
                </html>
                """
            
            # Send response
            client.send(response)
            client.close()
            
        except Exception as e:
            print(f"Error: {e}")
            client.close()

# Main program
def main():
    ip = connect_to_wifi()
    if ip:
        start_server(ip)

if __name__ == "__main__":
    main()
