import uasyncio as asyncio
import network
import json
import draw

try:
    import config
except ImportError:
    print("Create a config.py file with your wifi credentials")
    import sys
    sys.exit()

wlan = network.WLAN(network.STA_IF)
async def connect_wifi():
    """Connect to the WiFi network."""
    global wlan
    wlan.active(True)
    wlan.config(pm = 0xa11140)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)

    # Wait for connection with a timeout
    max_wait = 120
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        draw.image.ip = "Connecting..."
        await asyncio.sleep(1)

    if wlan.status() != 3:
        print('network connection failed')
        # Handle connection failure
        draw.image.ip = "WiFi failure."
        return None # Indicate failure
    else:
        status = wlan.ifconfig()
        print('connected. IP = ' + status[0])
        draw.image.ip = status[0]
        return wlan # Return the WLAN object

async def handle_http_request(reader, writer):
    """Handle an incoming HTTP client request."""
    addr = writer.get_extra_info('peername')
    print(f"Client connected from {addr}")

    request_line = await reader.readline()
    if not request_line:
        print("No request line")
        await writer.aclose()
        return

    request_line = request_line.decode().strip()
    print(f"Request: {request_line}")

    # Parse request line
    method, path, version = request_line.split(' ')

    # Read headers
    headers = {}
    while True:
        header_line = await reader.readline()
        if header_line == b'' or header_line == b'\r\n':
            break # End of headers
        header_line = header_line.decode().strip()
        if ':' in header_line:
            name, value = header_line.split(':', 1)
            headers[name.strip()] = value.strip()
            print(f"Header: {name.strip()}: {value.strip()}")

    content_length = int(headers.get('Content-Length', 0))
    content_type = headers.get('Content-Type', '').lower()
    
    json_data = None

    draw.image.init_balls()
    
    # --- Handle POST Request with JSON ---
    if method == 'POST':
        print(f"Received POST request with Content-Length: {content_length}, Content-Type: {content_type}")
        if content_length > 0:
            if 'application/json' in content_type:
                try:
                    # Read the exact number of bytes specified by Content-Length
                    body = await reader.readexactly(content_length)
                    body_str = body.decode()
                    print(f"Received body:\n{body_str}")

                    # Attempt to parse JSON
                    json_data = json.loads(body_str)
                    print("Parsed JSON data:", json_data)

                    # --- Process the JSON data here ---
                    if 'text' in json_data:
                        draw.image.text = json_data['text']

                    if 'text_color' in json_data:
                        draw.image.set_text_color(json_data['text_color'][0],json_data['text_color'][1],json_data['text_color'][2])

                    if 'bar_color' in json_data:
                        draw.image.set_bar_color(json_data['bar_color'][0],json_data['bar_color'][1],json_data['bar_color'][2])

                    if 'bg_color' in json_data:
                        draw.image.set_bg_color(json_data['bg_color'][0],json_data['bg_color'][1],json_data['bg_color'][2])

                    # Send a success response
                    response_status = '200 OK'
                    response_body = json.dumps({"status": "success", "received_data": json_data}) # Echo back received data or a confirmation
                    response_headers = {
                        'Content-Type': 'application/json',
                        'Content-Length': len(response_body)
                    }

                except ValueError as e:
                    print(f"JSON parsing error: {e}")
                    response_status = '400 Bad Request'
                    response_body = json.dumps({"status": "error", "message": "Invalid JSON"})
                    response_headers = {
                         'Content-Type': 'application/json',
                         'Content-Length': len(response_body)
                    }
                except Exception as e:
                    print(f"Error reading body: {e}")
                    response_status = '500 Internal Server Error'
                    response_body = json.dumps({"status": "error", "message": "Server error reading body"})
                    response_headers = {
                         'Content-Type': 'application/json',
                         'Content-Length': len(response_body)
                    }
            else:
                 print("Unsupported Media Type for POST")
                 response_status = '415 Unsupported Media Type'
                 response_body = json.dumps({"status": "error", "message": "Please send JSON (Content-Type: application/json)"})
                 response_headers = {
                      'Content-Type': 'application/json',
                      'Content-Length': len(response_body)
                 }
        else:
            print("POST request with no body (Content-Length was 0 or missing)")
            response_status = '400 Bad Request'
            response_body = json.dumps({"status": "error", "message": "POST request body expected (missing Content-Length or body)"})
            response_headers = {
                 'Content-Type': 'application/json',
                 'Content-Length': len(response_body)
            }
            
    # --- Handle GET or other methods ---
    elif method == 'GET':
        # --- Basic GET response based on path ---
        print(f"Received GET request for path: {path}")
        if path == '/':
            response_status = '200 OK'
            response_body = """<!DOCTYPE html>
<html>
<head><title>Pico W Async</title></head>
<body><h1>Pico W Status</h1><p>Async server and screen running.</p><p>Send a POST request with JSON to /data endpoint.</p></body>
</html>"""
            response_headers = {
                'Content-Type': 'text/html',
                'Content-Length': len(response_body)
            }
        # You could add other GET paths here
        # elif path == '/status':
        #     status_data = {"wifi": True, "animation": True} # Example status
        #     response_body = json.dumps(status_data)
        #     response_status = '200 OK'
        #     response_headers = {
        #         'Content-Type': 'application/json',
        #         'Content-Length': len(response_body)
        #     }
        # else:
        #     response_status = '404 Not Found'
        #     response_body = """<!DOCTYPE html><html><body><h1>404 Not Found</h1></body></html>"""
        #     response_headers = {
        #         'Content-Type': 'text/html',
        #         'Content-Length': len(response_body)
        #     }
        else:
             response_status = '404 Not Found'
             response_body = b'Not Found'
             response_headers = {
                'Content-Type': 'text/plain',
                'Content-Length': len(response_body)
             }

    else:
        # --- Handle unsupported methods ---
        print(f"Unsupported method: {method}")
        response_status = '405 Method Not Allowed'
        response_body = b'Method Not Allowed'
        response_headers = {
            'Content-Type': 'text/plain',
            'Content-Length': len(response_body)
        }


    # --- Send the response ---
    await writer.awrite(f'HTTP/1.0 {response_status}\r\n'.encode())
    for header_name, header_value in response_headers.items():
        await writer.awrite(f'{header_name}: {header_value}\r\n'.encode())
    await writer.awrite(b'\r\n') # End of headers
    
    if isinstance(response_body, str):
         await writer.awrite(response_body.encode())
    elif isinstance(response_body, bytes):
         await writer.awrite(response_body)
         
    await writer.drain() # Ensure data is sent
    await writer.wait_closed() # Wait for the client to close the connection or timeout
    print(f"Client {addr} disconnected")

async def start_http_server():
    """Start the asynchronous HTTP server."""
    # This creates and starts the server task managed by asyncio
    # Listen on all interfaces ('0.0.0.0') on port 80
    server = await asyncio.start_server(handle_http_request, '0.0.0.0', 80)
    print('HTTP server listening on 0.0.0.0:80')
    # The server runs in the background. wait_closed keeps this task alive.
    await server.wait_closed()
