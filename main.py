##from src import balls_demo
import server
import draw
import uasyncio as asyncio

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
    else:
        res = server.start_http_server()
        if res == None:
            raise Exception("Failed to connect to WiFi. Server will not start.")
        else:
            # Start the HTTP server as a background task ONLY if WiFi connected
            asyncio.create_task(res)

    # Start the screen animation as another background task
    asyncio.create_task(draw.image.update_loop())

    # Keep the main loop running so the tasks continue
    while True:
        await asyncio.sleep(5) # Sleep for a longer period

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