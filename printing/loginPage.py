import os
import sys
import threading
from tkinter import Tk, Canvas, StringVar, Toplevel, Label
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter
import tkinter.font as tkFont
from clientCalls import fetch_all_employees, get_employee_login_state

# ---------------- Platform Detection ----------------
IS_WINDOWS = sys.platform.startswith("win")

# ---------------- Resource Path ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ---------------- Image Loader ----------------
def open_and_subtle_sharpen_image(path, size):
    img = Image.open(resource_path(path))
    img = img.resize(size, Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=80, threshold=1))
    return img

def show_already_logged_in_popup(root, employee, continue_login_callback):
    popup = Toplevel(root)
    popup.title("Already Logged In")
    popup.transient(root)
    popup.grab_set()

    if not IS_WINDOWS:
        popup.overrideredirect(True)

    main_width = root.winfo_width() or 800
    main_height = root.winfo_height() or 450
    aspect_ratio = 1920 / 1080
    popup_width = max(1, main_width)
    popup_height = max(1, int(popup_width / aspect_ratio))

    x = root.winfo_x() + (main_width - popup_width) // 2
    y = root.winfo_y() + (main_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    if IS_WINDOWS:
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        popup.update_idletasks()

    # Load and display warning image
    try:
        img = open_and_subtle_sharpen_image("images/loggingWarning.png", (popup_width, popup_height))
        photo = ImageTk.PhotoImage(img)
        img_label = Label(popup, image=photo)
        img_label.image = photo
        img_label.place(x=0, y=0, width=popup_width, height=popup_height)
    except Exception as e:
        print(f"[Popup] Failed to load logging warning image: {e}")
        popup.configure(bg="#E6E1D6")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Popup.TButton", background="#6D05FF", foreground="white",
                    font=("Arial", 10, "bold"), padding=5)
    style.map("Popup.TButton", background=[('active', '#8B1CFF')],
              foreground=[('disabled', 'gray')])

    style.configure("Printer.TButton", background="#FF4C4C", foreground="white",
                    font=("Arial", 10, "bold"), padding=5)
    style.map("Printer.TButton", background=[('active', '#FF1C1C')], foreground=[('disabled', 'gray')])

    def printer_override():
        popup.destroy()
        continue_login_callback(employee)

    ttk.Button(popup, text="Printer Override", command=printer_override, style="Printer.TButton").place(
        relx=0.3, rely=0.85, anchor="center"
    )
    ttk.Button(popup, text="OK", command=popup.destroy, style="Popup.TButton").place(
        relx=0.7, rely=0.85, anchor="center"
    )

    if IS_WINDOWS:
        popup.update()

    popup.wait_window()

# ---------------- Connection Error Popup ----------------
def show_connection_error_popup(root):
    popup = Toplevel(root)
    popup.title("Connection Error")
    popup.transient(root)
    popup.grab_set()
    
    if not IS_WINDOWS:
        popup.overrideredirect(True)
    
    main_width = root.winfo_width() or 800
    main_height = root.winfo_height() or 450
    aspect_ratio = 1920 / 1080
    popup_width = max(1, main_width)
    popup_height = max(1, int(popup_width / aspect_ratio))
    
    x = root.winfo_x() + (main_width - popup_width) // 2
    y = root.winfo_y() + (main_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    if IS_WINDOWS:
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        popup.update_idletasks()
    
    # Load and display image
    try:
        img = open_and_subtle_sharpen_image("images/errorConnection.png", (popup_width, popup_height))
        photo = ImageTk.PhotoImage(img)
        img_label = Label(popup, image=photo)
        img_label.image = photo
        img_label.place(x=0, y=0, width=popup_width, height=popup_height)
    except Exception as e:
        print(f"[Popup] Failed to load image: {e}")
        popup.configure(bg="#E6E1D6")
    
    # OK button styling
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Popup.TButton", background="#6D05FF", foreground="white",
                    font=("Arial", 10, "bold"), padding=5)
    style.map("Popup.TButton", background=[('active', '#8B1CFF')], foreground=[('disabled', 'gray')])
    
    def close_popup():
        popup.destroy()
    
    ttk.Button(popup, text="OK", command=close_popup, style="Popup.TButton").place(
        relx=0.5, rely=0.85, anchor="center"
    )
    
    if IS_WINDOWS:
        popup.update()
    
    popup.wait_window()

# ---------------- Main Menu ----------------
def create_main_menu():
    global root
    selected_employee = [None]
    root = Tk()
    root.title("Employee Login")
    root.resizable(False, False)

    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # ---------------- Window Setup ----------------
    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    phone_ratio = 9 / 16
    window_height = int(screen_height * 0.85)
    window_width = int(window_height * phone_ratio)
    x_pos = (screen_width - window_width) // 2
    y_pos = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

    # ---------------- Background ----------------
    canvas = Canvas(root, width=window_width, height=window_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    try:
        bg_image = open_and_subtle_sharpen_image("images/mainMenu.png", (window_width, window_height))
        bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    except Exception:
        show_connection_error_popup(root)

    # ---------------- Styles ----------------
    style = ttk.Style()
    style.theme_use('clam')

    style.configure('Custom.TCombobox', fieldbackground='#E6E1D6', background='#E6E1D6',
                    foreground='black', padding=0)
    style.map('Custom.TCombobox',
              arrowcolor=[('!disabled', 'white')],
              fieldbackground=[('readonly', '#E6E1D6'), ('!readonly', '#E6E1D6')],
              background=[('readonly', '#E6E1D6'), ('!readonly', '#E6E1D6')],
              selectbackground=[('readonly', '#E6E1D6'), ('!readonly', '#E6E1D6')],
              selectforeground=[('readonly', 'black'), ('!readonly', 'black')])

    style.configure('Custom.TEntry', fieldbackground='#E6E1D6', foreground='black', padding=0)

    style.configure("Purple.TButton", background="#6D05FF", foreground="white",
                    font=("Arial", 6, "bold"), padding=2)
    style.map("Purple.TButton", background=[('active', '#8B1CFF')],
              foreground=[('disabled', 'gray')])

    root.option_add('*TCombobox*Listbox*Background', '#E6E1D6')
    root.option_add('*TCombobox*Listbox*Foreground', 'black')
    root.option_add('*TCombobox*Listbox*Font', ('Arial', 10))

    # ---------------- Combobox & Entry ----------------
    all_employee_names = []  # Store full list for filtering
    
    combo1 = ttk.Combobox(root, values=[], style='Custom.TCombobox',
                          height=8, state='normal')  # Changed to 'normal' to allow typing
    combo1.place(relx=0.42, rely=0.45, anchor="center", relwidth=0.35, relheight=0.03)
    
    def filter_combobox(event=None):
        typed = combo1.get().lower()
        if typed == '':
            filtered = all_employee_names
        else:
            filtered = [name for name in all_employee_names if typed in name.lower()]
        combo1['values'] = filtered
        combo1['height'] = min(8, max(1, len(filtered)))
    
    def combo_enter_pressed(event):
        # Open dropdown when pressing Enter in combobox
        combo1.event_generate('<Down>')
    
    combo1.bind('<KeyRelease>', filter_combobox)
    combo1.bind("<<ComboboxSelected>>", lambda e: combo1.selection_clear())
    combo1.bind("<Return>", combo_enter_pressed)

    entry1 = ttk.Entry(root, style='Custom.TEntry')
    entry1.place(relx=0.42, rely=0.54, anchor="center", relwidth=0.35, relheight=0.03)
    entry1.bind("<Return>", lambda e: confirm_password())

    # ---------------- Fetch Employees Thread ----------------
    employees = []

    def fetch_employees_thread():
        nonlocal employees
        try:
            fetched_employees = fetch_all_employees()
            if not fetched_employees:  # Empty list = network fetch failed
                raise Exception("No employees fetched")
            employees = fetched_employees
            employee_names = sorted(emp.employeeName for emp in employees)
        except Exception:
            employees = []
            employee_names = []

            # --- DELAYED NETWORK ERROR POPUP ---
            def delayed_error():
                show_connection_error_popup(root)
            root.after(200, delayed_error)  # ensure UI is ready

        def update_combo():
            nonlocal all_employee_names
            all_employee_names = employee_names
            combo1['values'] = employee_names
            combo1['height'] = min(8, len(employee_names))

        root.after(0, update_combo)

    threading.Thread(target=fetch_employees_thread, daemon=True).start()

    # ---------------- Login Button ----------------
    def confirm_password():
        selected_name = combo1.get()
        entered_password = entry1.get()
        try:
            employee = next((emp for emp in employees if emp.employeeName == selected_name), None)
        except Exception:
            show_connection_error_popup(root)
            return

        if not employee:
            show_connection_error_popup(root)
            return

        if entered_password != employee.password:
            print("Incorrect password")
            return

        # --- Check if already logged in ---
        state_response = get_employee_login_state(selected_name)

        def proceed_to_login(emp):
            selected_employee[0] = emp
            root.destroy()

        if state_response.get("status") == "success" and state_response.get("loggedIn") is True:
            # Already logged in – reset UI and show warning
            entry1.delete(0, "end")
            combo1.set("")
            show_already_logged_in_popup(root, employee, continue_login_callback=proceed_to_login)
            return
        elif state_response.get("status") != "success":
            # Network or server problem – fallback to connection error popup
            show_connection_error_popup(root)
            return

        # --- Proceed to login if not logged in ---
        proceed_to_login(employee)

    confirm_button = ttk.Button(root, text="Login", style="Purple.TButton", command=confirm_password)
    confirm_button.place(relx=0.325, rely=0.61, anchor="center", relwidth=0.16, relheight=0.035)

    # ---------------- Descent-Aware Font Scaling ----------------
    def get_font_size_for_widget(widget_height, font_family="Arial", bold=False, max_size=100):
        for size in range(1, max_size+1):
            f = tkFont.Font(family=font_family, size=size, weight="bold" if bold else "normal")
            total_height = f.metrics("ascent") + f.metrics("descent")
            if total_height > widget_height:
                return max(1, size-1)
        return max_size

    def resize_ui(event=None):
        widgets = [('Custom.TCombobox', combo1, True), ('Custom.TEntry', entry1, False)]
        for style_name, w, bold in widgets:
            width_px = w.winfo_width()
            height_px = w.winfo_height()
            if width_px <= 1 or height_px <= 1:
                root.after(10, resize_ui)
                return
            font_size = get_font_size_for_widget(height_px, "Arial", bold)
            f = tkFont.Font(family="Arial", size=font_size, weight="bold" if bold else "normal")
            style.configure(style_name, font=f, padding=0)
        combo_list_font = tkFont.Font(family="Arial", size=font_size)
        root.option_add('*TCombobox*Listbox*Font', combo_list_font)

    root.bind("<Configure>", resize_ui)
    root.after(100, resize_ui)

    def resize_buttons(event=None):
        buttons = [('Purple.TButton', confirm_button)]
        for style_name, btn in buttons:
            w = btn.winfo_width()
            h = btn.winfo_height()
            if w <= 1 or h <= 1:
                root.after(10, resize_buttons)
                return
            font_size = get_font_size_for_widget(h, "Arial", bold=True)
            f = tkFont.Font(family="Arial", size=font_size, weight="bold")
            style.configure(style_name, font=f, padding=0)

    root.bind("<Configure>", resize_buttons)
    root.after(100, resize_buttons)

    root.mainloop()
    return selected_employee[0]
