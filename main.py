import multiprocessing
import sys

# CRITICAL: This MUST be at the very top before other imports
if __name__ == '__main__':
    multiprocessing.freeze_support()

from loginPage import create_main_menu
from standardAlly import create_standard_window
from clientCalls import loggedOut
import time
import platform

# Permission checking for compiled apps
def check_permissions():
    """Basic permission check - expand as needed"""
    system = platform.system()
    if system == "Darwin":
        print("Note: This app requires Accessibility permissions on macOS")
        print("Go to System Preferences > Security & Privacy > Privacy > Accessibility")
    elif system == "Windows":
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("Warning: Running without administrator privileges")
                print("Barcode scanning may not work properly")
        except:
            pass

if __name__ == "__main__":
    print("[MAIN] Starting ProdigiAlly application...")
    
    # Check permissions on startup
    check_permissions()
    
    active = True
    loop_count = 0
    
    while active:
        loop_count += 1
        print(f"\n[MAIN] Main loop iteration #{loop_count}")
        print("[MAIN] Creating login window...")
        
        # Create login window and get employee
        loggedEmployee = create_main_menu()
        
        if loggedEmployee != None:
            print(f"[MAIN] Employee logged in: {loggedEmployee.employeeName}")
            print("[MAIN] Login window should be destroyed now")
            
            # Add small delay to ensure login window is fully destroyed
            time.sleep(0.3)
            print("[MAIN] Creating standard window...")
            
            # Create standard window - this should block until window closes
            logoff = create_standard_window(loggedEmployee)
            
            print(f"[MAIN] Standard window closed. Logoff value: {logoff}")
            
            # Handle logout
            try:
                response = loggedOut(loggedEmployee.employeeName, server_ip="192.168.111.230", port=8080)
                if response.get("status") != "success":
                    print(f"[MAIN] Logout Error: {response.get('message', 'Failed to log out')}")
                else:
                    print(f"[MAIN] Employee {loggedEmployee.employeeName} logged out successfully")
            except Exception as e:
                print(f"[MAIN] Connection Error during logout: {e}")
            
            # Check if user wants to return to login (logoff=True) or exit completely
            if logoff == True:
                print("[MAIN] User clicked Logout - returning to login screen")
                # Continue the loop to show login again
            else:
                print("[MAIN] Exiting application")
                active = False
                break
                
        else:  # No employee selected (user closed login window)
            print("[MAIN] No employee selected - exiting application")
            active = False
            break
    
    print("[MAIN] Application closing...")
    sys.exit(0)
