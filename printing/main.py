import requests
import webbrowser
import sys
import os

# Configuration
GITHUB_REPO = "harrisonhowford123/prodigially"
CURRENT_VERSION = "0.1.0"  # Update this with each release
APP_PREFIX = "printing"  # Tag prefix for this app

def check_for_updates():
    """Check GitHub for new releases for this specific app"""
    try:
        # Get all releases (not just latest)
        response = requests.get(
            f"https://api.github.com/repos/{GITHUB_REPO}/releases",
            timeout=5
        )
        
        if response.status_code != 200:
            return None
        
        releases = response.json()
        
        # Find the latest release for THIS app
        for release in releases:
            tag = release['tag_name']
            
            # Check if this release is for our app (printing-vX.X.X)
            if tag.startswith(f"{APP_PREFIX}-v"):
                # Extract version number (remove "printing-v")
                latest_version = tag.replace(f"{APP_PREFIX}-v", "")
                
                # Compare versions
                if latest_version > CURRENT_VERSION:
                    # Find the correct download asset
                    download_url = None
                    for asset in release['assets']:
                        # Match by app prefix in filename or just .dmg/.zip
                        if asset['name'].endswith('.dmg') or asset['name'].endswith('.zip'):
                            download_url = asset['browser_download_url']
                            break
                    
                    if download_url:
                        return {
                            'available': True,
                            'version': latest_version,
                            'url': download_url,
                            'notes': release.get('body', 'New version available')
                        }
                # Only check the most recent release for this app
                break
                
    except Exception as e:
        print(f"Update check failed: {e}")
    
    return None

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    import sys
    import os
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def show_update_notification(update_info):
    """Show custom branded update notification window"""
    import tkinter as tk
    from tkinter import font as tkfont
    from PIL import Image, ImageTk
    
    # Create custom window
    window = tk.Tk()
    window.title("Update Available")
    window.geometry("500x400")
    window.resizable(False, False)
    window.configure(bg="#F5F5F5")
    
    # Center the window on screen
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    # Variable to store user's choice
    user_choice = {'download': False}
    
    # Load and display logo
    try:
        # Use resource_path to find logo
        logo_path = resource_path(os.path.join("images", "prodigiAlly.png"))
        
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((200, 60), Image.Resampling.LANCZOS)
        logo_photo = ImageTk.PhotoImage(logo_img)
        
        logo_label = tk.Label(window, image=logo_photo, bg="#F5F5F5")
        logo_label.image = logo_photo  # Keep a reference
        logo_label.pack(pady=(20, 10))
    except Exception as e:
        print(f"Could not load logo: {e}")
        # Fallback text header
        header = tk.Label(window, text="prodigiAlly", 
                         font=("Arial", 24, "bold"), 
                         bg="#F5F5F5", fg="#7C3AED")
        header.pack(pady=(20, 10))
    
    # Update title
    title_font = tkfont.Font(family="Arial", size=18, weight="bold")
    title = tk.Label(window, 
                     text=f"Version {update_info['version']} Available!", 
                     font=title_font,
                     bg="#F5F5F5",
                     fg="#1F2937")
    title.pack(pady=(10, 5))
    
    # Current version
    current_font = tkfont.Font(family="Arial", size=11)
    current = tk.Label(window, 
                      text=f"Current version: {CURRENT_VERSION}",
                      font=current_font,
                      bg="#F5F5F5",
                      fg="#6B7280")
    current.pack(pady=(0, 15))
    
    # Release notes frame with scrollbar
    notes_frame = tk.Frame(window, bg="white", relief=tk.SOLID, borderwidth=1)
    notes_frame.pack(padx=40, pady=(0, 20), fill=tk.BOTH, expand=True)
    
    notes_text = tk.Text(notes_frame, 
                        wrap=tk.WORD, 
                        font=("Arial", 10),
                        bg="white",
                        fg="#374151",
                        relief=tk.FLAT,
                        padx=10,
                        pady=10,
                        height=6)
    notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    scrollbar = tk.Scrollbar(notes_frame, command=notes_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    notes_text.config(yscrollcommand=scrollbar.set)
    
    # Insert release notes
    notes_content = update_info['notes'] if update_info['notes'] else "New version available"
    notes_text.insert(1.0, notes_content)
    notes_text.config(state=tk.DISABLED)
    
    # Button frame
    button_frame = tk.Frame(window, bg="#F5F5F5")
    button_frame.pack(pady=(0, 20))
    
    def on_yes():
        user_choice['download'] = True
        window.destroy()
    
    def on_no():
        user_choice['download'] = False
        window.destroy()
    
    # Yes button (purple to match brand)
    yes_btn = tk.Button(button_frame,
                       text="Download Update",
                       command=on_yes,
                       font=("Arial", 12, "bold"),
                       bg="#7C3AED",
                       fg="white",
                       activebackground="#6D28D9",
                       activeforeground="white",
                       relief=tk.FLAT,
                       padx=30,
                       pady=10,
                       cursor="hand2")
    yes_btn.pack(side=tk.LEFT, padx=10)
    
    # No button
    no_btn = tk.Button(button_frame,
                      text="Not Now",
                      command=on_no,
                      font=("Arial", 12),
                      bg="#E5E7EB",
                      fg="#374151",
                      activebackground="#D1D5DB",
                      activeforeground="#374151",
                      relief=tk.FLAT,
                      padx=30,
                      pady=10,
                      cursor="hand2")
    no_btn.pack(side=tk.LEFT, padx=10)
    
    # Make window modal
    window.grab_set()
    window.focus_force()
    
    # Wait for window to close
    window.mainloop()
    
    # Handle user's choice
    if user_choice['download']:
        webbrowser.open(update_info['url'])
        # Show download instructions
        show_download_instructions()
    else:
        print(f"User declined update to version {update_info['version']}")

def show_download_instructions():
    """Show simple instructions after download starts"""
    import tkinter as tk
    from tkinter import font as tkfont
    
    inst_window = tk.Tk()
    inst_window.title("Download Started")
    inst_window.geometry("400x200")
    inst_window.resizable(False, False)
    inst_window.configure(bg="#F5F5F5")
    
    # Center window
    inst_window.update_idletasks()
    width = inst_window.winfo_width()
    height = inst_window.winfo_height()
    x = (inst_window.winfo_screenwidth() // 2) - (width // 2)
    y = (inst_window.winfo_screenheight() // 2) - (height // 2)
    inst_window.geometry(f'{width}x{height}+{x}+{y}')
    
    title_font = tkfont.Font(family="Arial", size=14, weight="bold")
    title = tk.Label(inst_window,
                    text="Download Started",
                    font=title_font,
                    bg="#F5F5F5",
                    fg="#1F2937")
    title.pack(pady=(20, 10))
    
    instructions = """The update will download in your browser.

To install:
1. Quit this application
2. Install the downloaded file
3. Restart the application"""
    
    inst_label = tk.Label(inst_window,
                         text=instructions,
                         font=("Arial", 11),
                         bg="#F5F5F5",
                         fg="#374151",
                         justify=tk.LEFT)
    inst_label.pack(pady=10)
    
    ok_btn = tk.Button(inst_window,
                      text="Got it!",
                      command=inst_window.destroy,
                      font=("Arial", 11, "bold"),
                      bg="#7C3AED",
                      fg="white",
                      activebackground="#6D28D9",
                      activeforeground="white",
                      relief=tk.FLAT,
                      padx=40,
                      pady=8,
                      cursor="hand2")
    ok_btn.pack(pady=20)
    
    inst_window.mainloop()

from loginPage import create_main_menu
from printingAlly import create_printing_menu
from clientCalls import loggedOut

if __name__ == "__main__":
    # Check for updates before showing login (runs on main thread)
    print("[UPDATE] Checking for updates...")
    update_info = check_for_updates()
    if update_info and update_info['available']:
        print(f"[UPDATE] Update found: version {update_info['version']}")
        show_update_notification(update_info)
    else:
        print("[UPDATE] No updates available")
    
    active = True
    while active:
        loggedEmployee = create_main_menu()
        if loggedEmployee is None:
            active = False
        else:
            # Assume create_printing_menu returns True if user wants to continue, False to exit
            continue_running = create_printing_menu(loggedEmployee)
            if continue_running is False:
                active = False  # Stop the loop if the user closes the printing menu
            else:
                try:
                    response = loggedOut(
                        loggedEmployee.employeeName,
                        server_ip="192.168.111.230",
                        port=8080
                    )
                    if response.get("status") != "success":
                        show_custom_popup(
                            "Logout Error",
                            message=response.get("message", "Failed to log out")
                        )
                except Exception as e:
                    show_custom_popup("Connection Error", message=str(e))
