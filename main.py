##from src import balls_demo
import server
import draw
import uasyncio as asyncio
from machine import Pin

async def main():
    print("Starting...")

    # Initialize display hardware (if needed before starting tasks)
    # display.init() # Placeholder

    # Connect to WiFi first
    wlan_status = await server.connect_wifi()
    if wlan_status is None:
        raise Exception("Failed to connect to WiFi. Server will not start.")
        # You might choose to exit or enter an offline mode here
        # For this example, we'll still start animation if WiFi fails

    http_server = await asyncio.start_server(server.handle_http_request, '0.0.0.0', 80)
    # res = server.start_http_server()
    # if res == None:
    server_task = asyncio.create_task(http_server.wait_closed())
    # print(dir(server_task))
    # if not http_server.is_serving():
    #     raise Exception("Failed to start server.")
    print('HTTP server listening on 0.0.0.0:80')

    # Start the screen animation as another background task
    asyncio.create_task(draw.image.update_loop())


    button_a = Pin(12, Pin.IN, Pin.PULL_UP)
    button_b = Pin(13, Pin.IN, Pin.PULL_UP)
    button_x = Pin(14, Pin.IN, Pin.PULL_UP)
    button_y = Pin(15, Pin.IN, Pin.PULL_UP)
    # Keep the main loop running so the tasks continue
    while True:
        wifi_status = server.wlan.ifconfig()
        draw.image.ip = wifi_status[0]

        if not server.wlan.isconnected() or wifi_status == '0.0.0.0':
            draw.image.server_status = "Connection lost. Reconnecting..."
            server.wlan.disconnect()
            await asyncio.sleep(1)
            success = await server.connect_wifi()
            if success is None:
                draw.image.server_status = "Error! Failed to reconnect."
            else:
                draw.image.server_status = "Listening..."


        if not http_server.state:
            draw.image.server_status = "Listening..."
        else:
            draw.image.server_status = "Error!"

        if button_a.value() == 0:
            print("A Button pressed. Showing IP.")
            draw.image.show_ip = True
        if button_b.value() == 0:
            print("B Button pressed. Hiding IP.")
            draw.image.show_ip = False
        if button_x.value() == 0:
            print("X Button pressed. Showing server status.")
            draw.image.show_server_status = True
        if button_y.value() == 0:
            print("Y Button pressed. Hiding server status.")
            draw.image.show_server_status = False
        await asyncio.sleep(0.01) # Sleep for a longer period

# --- Run the Event Loop ---
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program interrupted by user")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    print("Cleaning up...")
    # Clean up resources if necessary (e.g., close display)
    # if hasattr(draw.display, 'deinit'):
    #    draw.display.deinit() # Placeholder
    # draw.display.clear()
    # draw.display.update()

    # This helps reset the asyncio state for subsequent runs in an IDE
    asyncio.new_event_loop()
    print("Cleanup complete")