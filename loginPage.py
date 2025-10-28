import os
import sys
import threading
from tkinter import Tk, Canvas, StringVar, Toplevel, Label
from tkinter import ttk
from PIL import Image, ImageTk, ImageFilter
import tkinter.font as tkFont
from clientCalls import fetch_all_employees, get_employee_login_state

IS_WINDOWS = sys.platform.startswith("win")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def open_and_subtle_sharpen_image(path, size):
    img = Image.open(resource_path(path))
    img = img.resize(size, Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=80, threshold=1))
    return img

def show_image_popup(root, title, image_path):
    popup = Toplevel(root)
    popup.title(title)
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

    try:
        img = open_and_subtle_sharpen_image(image_path, (popup_width, popup_height))
        photo = ImageTk.PhotoImage(img)
        img_label = Label(popup, image=photo)
        img_label.image = photo
        img_label.place(x=0, y=0, width=popup_width, height=popup_height)
    except Exception as e:
        print(f"[Popup] Failed to load image: {e}")
        popup.configure(bg="#E6E1D6")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Popup.TButton", background="#6D05FF", foreground="white", font=("Arial", 10, "bold"), padding=5)
    style.map("Popup.TButton", background=[('active', '#8B1CFF')], foreground=[('disabled', 'gray')])

    ttk.Button(popup, text="OK", command=popup.destroy, style="Popup.TButton").place(relx=0.5, rely=0.85, anchor="center")

    if IS_WINDOWS:
        popup.update()

    popup.wait_window()

def show_already_logged_in_popup(root):
    show_image_popup(root, "Already Logged In", "images/loggingWarning.png")

def show_connection_error_popup(root):
    show_image_popup(root, "Connection Error", "images/errorConnection.png")

def show_incorrect_password_popup(root):
    show_image_popup(root, "Incorrect Password", "images/incorrectPassword.png")

def create_main_menu():
    global root
    selected_employee = [None]
    root = Tk()
    root.title("Employee Login")
    root.resizable(False, False)

    def on_close():
        try:
            if 'p' in globals() and getattr(p, 'is_alive', lambda: False)():
                p.terminate()
        except Exception:
            pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    phone_ratio = 9 / 16
    window_height = int(screen_height * 0.85)
    window_width = int(window_height * phone_ratio)
    x_pos = (screen_width - window_width) // 2
    y_pos = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_pos}+{y_pos}")

    canvas = Canvas(root, width=window_width, height=window_height, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    try:
        bg_image = open_and_subtle_sharpen_image("images/mainMenu.png", (window_width, window_height))
        bg_photo = ImageTk.PhotoImage(bg_image)
        canvas.bg_photo = bg_photo
        canvas.create_image(0, 0, anchor="nw", image=bg_photo)
    except Exception:
        show_connection_error_popup(root)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Custom.TCombobox', fieldbackground='#E6E1D6', background='#E6E1D6', foreground='black', padding=0)
    style.map('Custom.TCombobox', arrowcolor=[('!disabled', 'white')])

    root.option_add('*TCombobox*Listbox*Background', '#E6E1D6')
    root.option_add('*TCombobox*Listbox*Foreground', 'black')
    root.option_add('*TCombobox*Listbox*selectBackground', 'black')
    root.option_add('*TCombobox*Listbox*selectForeground', 'white')

    style.configure('Custom.TEntry', fieldbackground='#E6E1D6', foreground='black', padding=0)
    style.configure("Purple.TButton", background="#6D05FF", foreground="white", font=("Arial", 6, "bold"), padding=2)

    employees = []
    employee_names_master = []

    combo1_var = StringVar()
    combo1 = ttk.Combobox(root, textvariable=combo1_var, values=[], style='Custom.TCombobox', height=8)
    combo1.place(relx=0.42, rely=0.45, anchor="center", relwidth=0.35, relheight=0.03)

    entry1 = ttk.Entry(root, style='Custom.TEntry', show='•')
    entry1.place(relx=0.42, rely=0.54, anchor="center", relwidth=0.35, relheight=0.03)

    def fetch_employees_thread():
        nonlocal employees, employee_names_master
        try:
            fetched_employees = fetch_all_employees()
            if not fetched_employees:
                raise Exception("No employees fetched")
            employees = fetched_employees
            employee_names_master = sorted(emp.employeeName for emp in employees)
        except Exception:
            employees = []
            employee_names_master = []
            root.after(200, lambda: show_connection_error_popup(root))

        root.after(0, lambda: combo1.configure(values=employee_names_master))

    threading.Thread(target=fetch_employees_thread, daemon=True).start()

    def filter_usernames(event=None):
        combo1.event_generate('<Escape>')
        query = combo1_var.get().strip().lower()
        if not employee_names_master:
            return
        if not query:
            filtered = employee_names_master
        else:
            filtered = [n for n in employee_names_master if query in n.lower()]
        combo1['values'] = filtered
        combo1['height'] = min(8, len(filtered))

    combo1.bind('<KeyRelease>', filter_usernames)

    def clear_combo_selection(event=None):
        try:
            combo1.selection_clear()
            combo1.icursor('end')
        except Exception:
            pass

    combo1.bind('<FocusOut>', clear_combo_selection)

    def on_combo_selected(event=None):
        clear_combo_selection()
        text = combo1_var.get().strip()
        values = list(combo1['values'])
        if any(text.lower() == v.lower() for v in values) and text:
            entry1.focus_set()
    combo1.bind('<<ComboboxSelected>>', on_combo_selected)

    def on_combo_return(event=None):
        text = combo1_var.get().strip()
        values = list(combo1['values'])
        if any(text.lower() == v.lower() for v in values) and text:
            entry1.focus_set()
        else:
            combo1.event_generate('<Down>')
        return 'break'
    combo1.bind('<Return>', on_combo_return)

    def confirm_password():
        selected_name = combo1_var.get().strip()
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
            show_incorrect_password_popup(root)
            return

        state_response = get_employee_login_state(selected_name)
        if state_response.get("status") == "success" and state_response.get("loggedIn") is True:
            entry1.delete(0, "end")
            combo1.set("")
            show_already_logged_in_popup(root)
            return
        elif state_response.get("status") != "success":
            show_connection_error_popup(root)
            return

        selected_employee[0] = employee
        root.destroy()

    confirm_button = ttk.Button(root, text="Login", style="Purple.TButton", command=confirm_password)
    confirm_button.place(relx=0.325, rely=0.61, anchor="center", relwidth=0.16, relheight=0.035)

    def on_password_return(event=None):
        confirm_password()
        return 'break'
    entry1.bind('<Return>', on_password_return)

    root.mainloop()
    return selected_employee[0]
