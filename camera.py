import pyautogui
import time

print("Move your mouse around to see the live coordinates. Press Ctrl+C to stop.")

try:
    while True:
        # Get the current mouse position
        x, y = pyautogui.position()
        
        # Print the coordinates (overwrite the same line for better readability)
        print(f"X: {x}, Y: {y}", end='\r', flush=True)
        
        # Sleep for a short time to avoid overwhelming the console
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nProgram stopped.")
