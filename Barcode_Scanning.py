# Barcode_Scanning.py - Robust version for compiled apps
import sys
import time
import threading
import platform
from multiprocessing import Queue

def start_listener(queue: Queue):
    """
    Start the barcode listener - works in compiled executables
    """
    print(f"Barcode listener process started on {platform.system()}")
    
    # Import pynput inside the function to avoid import issues
    try:
        from pynput import keyboard
    except ImportError as e:
        print(f"ERROR: Could not import pynput: {e}")
        # Keep process alive but non-functional
        while True:
            time.sleep(1)
            
    # Platform-specific messages
    if platform.system() == "Darwin":
        print("Note: macOS requires Accessibility permissions for keyboard monitoring")
    elif platform.system() == "Windows":
        print("Note: Windows may require administrator privileges for global keyboard capture")
    
    # Buffer for accumulating barcode characters
    buffer = []
    last_char_time = 0
    CHAR_TIMEOUT = 0.15  # 150ms between characters max
    
    def on_press(key):
        nonlocal buffer, last_char_time
        
        try:
            current_time = time.time()
            
            # Get the character if it's a regular key
            char = None
            if hasattr(key, 'char'):
                char = key.char
            elif hasattr(key, 'vk'):  # Windows virtual key
                # Handle numpad numbers
                if 96 <= key.vk <= 105:  # Numpad 0-9
                    char = str(key.vk - 96)
            
            if char and char.isprintable():
                # Reset buffer if too much time passed
                if current_time - last_char_time > CHAR_TIMEOUT:
                    buffer = []
                
                buffer.append(char)
                last_char_time = current_time
                
                # Send character to main process
                try:
                    queue.put(("CHAR", char))
                except:
                    pass  # Queue might be closed
                
            elif key in [keyboard.Key.enter, keyboard.Key.tab]:
                # End of barcode scan
                if buffer and (current_time - last_char_time <= CHAR_TIMEOUT):
                    try:
                        queue.put(("END", None))
                    except:
                        pass  # Queue might be closed
                        
                # Reset buffer
                buffer = []
                last_char_time = 0
                
        except Exception as e:
            print(f"Listener error: {e}")
    
    # Create and start the listener
    try:
        listener = keyboard.Listener(
            on_press=on_press,
            suppress=False  # Don't suppress the actual keystrokes
        )
        
        # Start the listener
        listener.start()
        print("Keyboard listener started successfully")
        
        # Keep the process alive
        listener.join()
            
    except Exception as e:
        print(f"Failed to start keyboard listener: {e}")
        print("Keeping process alive...")
        # Keep process alive even if listener fails
        while True:
            time.sleep(1)
