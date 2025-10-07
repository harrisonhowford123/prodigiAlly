# standardAlly.py - DEBUG VERSION WITH PRINTS
import os
import sys
import threading
import time
from multiprocessing import Process, Queue
from tkinter import Tk, Canvas, StringVar, Toplevel, Label, IntVar, Button
from tkinter.ttk import Combobox, Entry, Style, Button as TtkButton
from PIL import Image, ImageTk, ImageFilter
from clientCalls import fetch_facility_workstations, send_tracking_data, move_container, fetch_employee_start_time, log_employee_time, loggedOut
import Barcode_Scanning as barcode_listener
import tkinter.font as tkFont
from datetime import datetime, timedelta
import platform

# Platform detection for popup fixes
IS_WINDOWS = platform.system() == "Windows"

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

# ---------------- Time Popup ----------------
def show_time_popup(employee_name):
    print(f"[STANDARD] Opening time popup for {employee_name}")
    hour_start = IntVar(value=9)
    minute_start = IntVar(value=0)
    hour_end = IntVar(value=17)
    minute_end = IntVar(value=0)

    popup = Toplevel(root)
    popup.transient(root)
    popup.grab_set()
    
    if not IS_WINDOWS:
        popup.overrideredirect(True)
    else:
        popup.title("Set Work Time")
    
    root.update_idletasks()
    main_width = root.winfo_width()
    main_height = root.winfo_height()
    if main_width <= 1:
        main_width = 800
    if main_height <= 1:
        main_height = 450

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
        bg_image = Image.open(resource_path("images/setWorkTime.png"))
        bg_image = bg_image.resize((popup_width, popup_height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        bg_label = Label(popup, image=bg_photo)
        bg_label.image = bg_photo
        bg_label.place(x=0, y=0, width=popup_width, height=popup_height)
    except Exception as e:
        print(f"[STANDARD] Failed to load time popup background: {e}")
        popup.configure(bg="#E6E1D6")

    y_pos = int(popup_height * 0.4)
    padding_x = int(0.05 * popup_width)
    time_width = int((popup_width - 3 * padding_x) // 2 * 0.8)
    time_height = int(100 * 0.8)
    start_x = (popup_width - (2 * time_width + padding_x)) // 2

    start_selector = TimeSelector(
        popup, hour_start, minute_start,
        x=start_x, y=y_pos, width=time_width, height=time_height, label_text="Start"
    )
    end_selector = TimeSelector(
        popup, hour_end, minute_end,
        x=start_x + time_width + padding_x, y=y_pos, width=time_width, height=time_height, label_text="End"
    )

    def on_submit():
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time()).replace(
            hour=hour_start.get(), minute=minute_start.get(), second=0
        )
        end_time = datetime.combine(today, datetime.min.time()).replace(
            hour=hour_end.get(), minute=minute_end.get(), second=0
        )

        if end_time < start_time:
            end_time += timedelta(days=1)

        try:
            response = log_employee_time(
                employee_name=employee_name,
                start_time=start_time,
                end_time=end_time,
                server_ip="192.168.111.230",
                port=8080
            )
            if response.get("status") != "success":
                show_custom_popup("Error", message=response.get("message", "Failed to log time"))
        except Exception as e:
            show_custom_popup("Connection Error", message=str(e))

        print(f"[STANDARD] Time popup closed")
        popup.destroy()

    style = Style()
    style.theme_use('clam')
    style.configure("Popup.TButton", background="#6D05FF", foreground="white",
                    font=("Arial", 10, "bold"), padding=5)
    style.map("Popup.TButton", background=[('active', '#8B1CFF')], foreground=[('disabled', 'gray')])

    submit_btn = TtkButton(popup, text="Submit", style="Popup.TButton", command=on_submit)
    submit_btn.place(relx=0.5, rely=0.85, anchor="center")
    
    if IS_WINDOWS:
        popup.update()

    popup.wait_window()

# ---------------- Custom Popup ----------------
def show_custom_popup(title, message=None, confirm=False, image_path=None, errorConnection=False):
    print(f"[STANDARD] Showing popup: {title}")
    popup = Toplevel(root)
    popup.title(title)
    popup.transient(root)
    popup.grab_set()
    
    if not IS_WINDOWS:
        popup.overrideredirect(True)

    main_width = root.winfo_width() or 800
    aspect_ratio = 1920 / 1080
    popup_width = main_width
    popup_height = int(popup_width / aspect_ratio)

    x = root.winfo_x() + (root.winfo_width() - popup_width) // 2
    y = root.winfo_y() + (root.winfo_height() - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
    
    if IS_WINDOWS:
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        popup.update_idletasks()

    if image_path:
        try:
            img = open_and_subtle_sharpen_image(image_path, (popup_width, popup_height))
            photo = ImageTk.PhotoImage(img)
            img_label = Label(popup, image=photo)
            img_label.image = photo
            img_label.place(x=0, y=0, width=popup_width, height=popup_height)
        except Exception as e:
            print(f"[STANDARD] Failed to load popup image: {e}")
            msg_label = Label(popup, text=title, bg="#E6E1D6",
                            fg="black", font=("Arial", 14, "bold"),
                            wraplength=popup_width-20, justify="center")
            msg_label.pack(expand=True, fill="both", pady=10, padx=10)
    elif message:
        msg_label = Label(popup, text=message, bg="#E6E1D6",
                          fg="black", font=("Arial", 12, "bold"),
                          wraplength=popup_width-20, justify="center")
        msg_label.pack(expand=True, fill="both", pady=10, padx=10)
    else:
        popup.configure(bg="#E6E1D6")

    popup_style = Style()
    popup_style.theme_use('clam')
    popup_style.configure(
        "Popup.TButton",
        background="#6D05FF",
        foreground="white",
        font=("Arial", 10, "bold"),
        padding=max(1, int(root.winfo_height() * 0.01))
    )
    popup_style.map(
        "Popup.TButton",
        background=[('active', '#8B1CFF')],
        foreground=[('disabled', 'gray')]
    )

    if confirm:
        result = {"value": False}
        def yes_action():
            result["value"] = True
            popup.destroy()
        def no_action():
            popup.destroy()
        TtkButton(popup, text="Yes", command=yes_action, style="Popup.TButton").place(relx=0.38, rely=0.85, anchor="center")
        TtkButton(popup, text="No", command=no_action, style="Popup.TButton").place(relx=0.62, rely=0.85, anchor="center")
        
        if IS_WINDOWS:
            popup.update()
            
        popup.wait_window()
        return result["value"]
    else:
        popup.update_idletasks()
        if errorConnection:
            button_y = int(popup.winfo_height() * 0.8)
            TtkButton(popup, text="OK", command=popup.destroy, style="Popup.TButton").place(
                x=popup.winfo_width()//2, y=button_y, anchor="center")
        else:
            TtkButton(popup, text="OK", command=popup.destroy, style="Popup.TButton").place(relx=0.65, rely=0.631, anchor="center")
        
        if IS_WINDOWS:
            popup.update()
            
        popup.wait_window()
        return None

# ---------------- Time Selector ----------------
class TimeSelector:
    def __init__(self, master, hour_var, minute_var, x, y, width, height, label_text="Time"):
        self.master = master
        self.hour_var = hour_var
        self.minute_var = minute_var
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.label_text = label_text
        self.create_widgets()

    def create_widgets(self):
        padding = int(self.height * 0.05)
        label_height = int(self.height * 0.25)
        arrow_size = int(self.height * 0.25)
        time_width = self.width - 2 * (arrow_size + padding)
        font_size_label = max(8, int(label_height * 0.6))
        font_size_time = max(8, int(arrow_size * 0.6))

        self.label = Label(self.master, text=self.label_text, fg="black", bg="#E6E1D6", font=("Arial", font_size_label, "bold"))
        self.label.place(x=self.x + self.width//2, y=self.y + padding, anchor="n")

        self.left_arrow = Canvas(self.master, width=arrow_size, height=arrow_size, bg="black", highlightthickness=0)
        self.left_arrow.place(x=self.x + padding, y=self.y + label_height + padding)
        self.draw_left_arrow()
        self.left_arrow.bind("<Button-1>", lambda e: self.change_time(-15))
        self.left_arrow.bind("<Enter>", lambda e: self.left_arrow.config(cursor="hand2"))

        self.time_label = Label(self.master, text=self.get_time(), fg="white", bg="black",
                                font=("Arial", font_size_time, "bold"))
        self.time_label.place(x=self.x + arrow_size + 2*padding, y=self.y + label_height + padding,
                              width=time_width, height=arrow_size)

        self.right_arrow = Canvas(self.master, width=arrow_size, height=arrow_size, bg="black", highlightthickness=0)
        self.right_arrow.place(x=self.x + arrow_size + 3*padding + time_width, y=self.y + label_height + padding)
        self.draw_right_arrow()
        self.right_arrow.bind("<Button-1>", lambda e: self.change_time(15))
        self.right_arrow.bind("<Enter>", lambda e: self.right_arrow.config(cursor="hand2"))

    def draw_left_arrow(self):
        w, h = self.left_arrow.winfo_reqwidth(), self.left_arrow.winfo_reqheight()
        self.left_arrow.delete("all")
        self.left_arrow.create_polygon([w*0.7, h*0.2, w*0.3, h*0.5, w*0.7, h*0.8], fill="white")

    def draw_right_arrow(self):
        w, h = self.right_arrow.winfo_reqwidth(), self.right_arrow.winfo_reqheight()
        self.right_arrow.delete("all")
        self.right_arrow.create_polygon([w*0.3, h*0.2, w*0.7, h*0.5, w*0.3, h*0.8], fill="white")

    def change_time(self, delta_minutes):
        total_minutes = self.hour_var.get()*60 + self.minute_var.get() + delta_minutes
        total_minutes %= 24*60
        self.hour_var.set(total_minutes // 60)
        self.minute_var.set(total_minutes % 60)
        self.time_label.config(text=self.get_time())

    def get_time(self):
        return f"{self.hour_var.get():02d}:{self.minute_var.get():02d}"

# ---------------- Main Window ----------------
def create_standard_window(employee):
    print(f"[STANDARD] Creating standard window for employee: {employee.employeeName}")
    global root, p
    window_result = False
    root = Tk()
    root.title("Prodigi Ally")
    root.resizable(False, False)
    
    # ---------------- Log Employee as Logged In ----------------
    try:
        from clientCalls import loggedIn
        print(f"[STANDARD] Attempting to log in employee '{employee.employeeName}' to server...")
        response = loggedIn(employee.employeeName)
        print(f"[STANDARD] LoggedIn response: {response}")

        if response.get("status") == "success":
            print(f"[STANDARD] Employee '{employee.employeeName}' successfully logged in on server.")
        else:
            print(f"[STANDARD] Failed to log in employee '{employee.employeeName}': {response.get('message')}")
    except Exception as e:
        print(f"[STANDARD] Exception during loggedIn call for '{employee.employeeName}': {e}")

    # ---------------- Proper Close Handling ----------------
    def on_close():
        print("[STANDARD] Window close button clicked")
        nonlocal window_result
        window_result = False  # Exit application completely
        try:
            if 'p' in globals() and p.is_alive():
                print("[STANDARD] Terminating barcode process...")
                p.terminate()
        except Exception as e:
            print(f"[STANDARD] Error terminating process: {e}")
        print("[STANDARD] Destroying window...")
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

    bg_image = open_and_subtle_sharpen_image("images/standardAlly.png", (window_width, window_height))
    bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.bg_photo = bg_photo
    canvas.create_image(0, 0, anchor="nw", image=bg_photo)

    # ---------------- Styles ----------------
    style = Style()
    style.theme_use('clam')

    style.configure('Custom.TCombobox', fieldbackground='#E6E1D6', background='#E6E1D6', foreground='black', arrowcolor='white', padding=0)
    style.map('Custom.TCombobox',
              arrowcolor=[('!disabled', 'white')],
              fieldbackground=[('readonly', '#E6E1D6')],
              background=[('readonly', '#E6E1D6')],
              selectbackground=[('readonly', '#E6E1D6')],
              selectforeground=[('readonly', 'black')])
    style.configure('Custom.TEntry', fieldbackground='#E6E1D6', foreground='black', padding=0)

    style.configure("Red.TButton", background="#FF0000", foreground="white", font=("Arial", 6, "bold"), padding=2)
    style.configure("Purple.TButton", background="#6D05FF", foreground="white", font=("Arial", 6, "bold"), padding=2)
    style.configure("Green.TButton", background="#28A745", foreground="white", font=("Arial", 6, "bold"), padding=2)

    root.option_add('*TCombobox*Listbox*Background', '#E6E1D6')
    root.option_add('*TCombobox*Listbox*Foreground', 'black')
    root.option_add('*TCombobox*Listbox*Font', ('Arial', 10))

    # ---------------- Widgets ----------------
    selected_option = StringVar()
    combo1 = Combobox(root, textvariable=selected_option, values=[], style='Custom.TCombobox', state='readonly', height=5)
    combo1.place(relx=0.18, rely=0.158, relwidth=0.7, relheight=0.03)
    employee_name_var = StringVar(value=employee.employeeName)
    entry1 = Entry(root, style='Custom.TEntry', textvariable=employee_name_var, state='readonly')
    entry1.place(relx=0.18, rely=0.103, relwidth=0.7, relheight=0.03)
    barcode_var = StringVar(value="")
    entry2 = Entry(root, style='Custom.TEntry', textvariable=barcode_var, state='readonly')
    entry2.place(relx=0.18, rely=0.213, relwidth=0.7, relheight=0.03)

    # ---------------- Button Commands ----------------
    def reprint_action():
        print("[STANDARD] Reprint button clicked")
        barcode_value = barcode_var.get().strip()
        workstation = combo1.get()
        employeeName = employee_name_var.get()

        if not workstation or not barcode_value:
            show_custom_popup("Warning", image_path="images/warning_emptyField.png")
            return

        if len(barcode_value) == 10:
            leadBarcode = barcode_value
            isoBarcode = None
            confirm_msg = "images/warning_wholeFileReprint.png"
        elif len(barcode_value) == 11:
            leadBarcode = None
            isoBarcode = barcode_value
            confirm_msg = "images/confirm.png"
        else:
            show_custom_popup("Warning", image_path="images/warning_emptyField.png")
            return

        confirm = show_custom_popup("Reprint", confirm=True, image_path=confirm_msg)
        if not confirm:
            return

        try:
            containerID = None
            orderNumber = None
            response = send_tracking_data(containerID, orderNumber, leadBarcode, isoBarcode, "REPRINT", employeeName)
            if response.get("status") == "error":
                show_custom_popup("Connection Error", image_path="images/errorConnection.png", errorConnection=True)
        except Exception:
            show_custom_popup("Connection Error", image_path="images/errorConnection.png", errorConnection=True)

    def complete_batch_action():
        print("[STANDARD] Complete Batch button clicked")
        confirm = show_custom_popup("Complete Batch", confirm=True, image_path="images/confirm.png")
        if not confirm:
            return

        def task():
            try:
                barcode_value = barcode_var.get().strip()
                workstation = combo1.get().strip()
                employeeName = employee_name_var.get()
                if not barcode_value or not workstation:
                    show_custom_popup("Warning", image_path="images/warning_emptyField.png")
                    return

                if len(barcode_value) == 10:
                    leadBarcode = barcode_value
                    isoBarcode = None
                elif len(barcode_value) == 11:
                    leadBarcode = None
                    isoBarcode = barcode_value
                else:
                    show_custom_popup("Warning", image_path="images/warning_emptyField.png")
                    return

                response = move_container(
                    leadBarcode=leadBarcode,
                    isoBarcode=isoBarcode,
                    workstation=workstation,
                    employeeName=employeeName,
                    server_ip="192.168.111.230",
                    port=8080
                )
                if response.get("status") != "success":
                    show_custom_popup("Connection Error", image_path="images/errorConnection.png", errorConnection=True)
                else:
                    show_custom_popup("Success", image_path="images/batchMoved.png", errorConnection=True)

            except Exception:
                show_custom_popup("Connection Error", image_path="images/errorConnection.png", errorConnection=True)

        threading.Thread(target=task, daemon=True).start()

    def exit_action():
        print("[STANDARD] Logout button clicked")
        nonlocal window_result
        employeeName = employee_name_var.get()
        try:
            response = loggedOut(employeeName, server_ip="192.168.111.230", port=8080)
            if response.get("status") != "success":
                show_custom_popup("Logout Error", message=response.get("message", "Failed to log out"))
        except Exception as e:
            show_custom_popup("Connection Error", message=str(e))
        finally:
            window_result = True  # Return to login screen
            print("[STANDARD] Setting window_result to True (return to login)")
            root.destroy()

    # ---------------- Buttons ----------------
    reprint_btn = TtkButton(root, text="Reprint", style="Red.TButton", command=reprint_action)
    reprint_btn.place(relx=0.18, rely=0.27, relwidth=0.16, relheight=0.033)
    complete_batch_btn = TtkButton(root, text="Complete Batch", style="Green.TButton", command=complete_batch_action)
    complete_batch_btn.place(relx=0.36, rely=0.27, relwidth=0.35, relheight=0.033)
    exit_btn = TtkButton(root, text="Logout", style="Purple.TButton", command=exit_action)
    exit_btn.place(relx=0.18, rely=0.31, relwidth=0.16, relheight=0.033)

    # ---------------- Settings Cog Button ----------------
    try:
        cog_img_path = resource_path("images/settingsCog.png")
        cog_img = Image.open(cog_img_path)
        cog_btn_size = int(window_width * 0.075)
        cog_img_size = int(cog_btn_size * 0.75)
        cog_img = cog_img.resize((cog_img_size, cog_img_size), Image.Resampling.LANCZOS)
        cog_photo = ImageTk.PhotoImage(cog_img)

        settings_btn = Button(
            root,
            image=cog_photo,
            bd=0,
            highlightthickness=0,
            relief="flat",
            command=lambda: show_time_popup(employee.employeeName)
        )

        settings_btn.image = cog_photo
        settings_btn.place(
            relx=0.875,
            rely=0.04,
            anchor="ne",
            width=cog_btn_size,
            height=cog_btn_size
        )
    except Exception as e:
        print(f"[STANDARD] Error loading settings cog: {e}")

    # ---------------- Font size calculation ----------------
    def get_font_size_for_widget(widget_height, font_family="Arial", bold=False, max_size=100):
        for size in range(1, max_size+1):
            f = tkFont.Font(family=font_family, size=size, weight="bold" if bold else "normal")
            total_height = f.metrics("ascent") + f.metrics("descent")
            if total_height > widget_height:
                return max(1, size-1)
        return max_size

    # ---------------- Resize Entries / Combobox ----------------
    def resize_ui(event=None):
        widgets = [
            ('Custom.TCombobox', combo1, True),
            ('Custom.TEntry', entry1, False),
            ('Custom.TEntry', entry2, False)
        ]
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

    # ---------------- Resize Buttons ----------------
    def resize_buttons(event=None):
        buttons = [
            ('Red.TButton', reprint_btn),
            ('Green.TButton', complete_batch_btn),
            ('Purple.TButton', exit_btn)
        ]
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

    # ---------------- Fetch Workstations ----------------
    def fetch_workstations_thread():
        print("[STANDARD] Fetching workstations...")
        try:
            workstations, _, _ = fetch_facility_workstations()
        except Exception as e:
            print(f"[STANDARD] Error fetching workstations: {e}")
            workstations = []

        def update_combo_and_show_popup():
            combo1['values'] = sorted(workstations, key=str.lower) if workstations else []
            combo1['height'] = len(workstations)

            if not workstations:
                show_custom_popup(
                    "Connection Error",
                    image_path="images/errorConnection.png",
                    errorConnection=True
                )

            # Check Employee Start Time
            from clientCalls import fetch_employee_start_time
            start_time = fetch_employee_start_time(employee.employeeName)
            today = datetime.now().date()

            if not start_time:
                root.after(0, lambda: show_time_popup(employee.employeeName))
            else:
                try:
                    parsed_start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    if parsed_start_time.date() != today:
                        root.after(0, lambda: show_time_popup(employee.employeeName))
                    else:
                        print(f"[STANDARD] Employee {employee.employeeName} already has start time for today: {parsed_start_time}")
                except ValueError:
                    root.after(0, lambda: show_time_popup(employee.employeeName))

        root.after(0, update_combo_and_show_popup)

    threading.Thread(target=fetch_workstations_thread, daemon=True).start()

    # ---------------- Barcode Listener ----------------
    print("[STANDARD] Starting barcode listener process...")
    queue = Queue()
    p = Process(target=barcode_listener.start_listener, args=(queue,))
    p.daemon = True
    p.start()
    print(f"[STANDARD] Barcode process started with PID: {p.pid}")

    scanning = {"completed": True, "last_char_time": 0}
    BARCODE_TIMEOUT = 0.1
    HUMAN_TYPING_THRESHOLD = 0.3
    FAST_PULSE_THRESHOLD = 0.05
    barcode_buffer = []
    MIN_BARCODE_LENGTH = 6

    def poll_queue():
        while not queue.empty():
            msg_type, value = queue.get()
            now = time.time()

            if msg_type == "CHAR":
                print(f"[STANDARD] Barcode char received: {value}")
                if scanning["completed"] or (now - scanning["last_char_time"] > HUMAN_TYPING_THRESHOLD):
                    barcode_buffer.clear()
                    scanning["completed"] = False

                barcode_buffer.append(value)
                scanning["last_char_time"] = now

            elif msg_type == "END":
                print(f"[STANDARD] Barcode END signal received. Buffer: {''.join(barcode_buffer)}")
                if barcode_buffer and (now - scanning["last_char_time"] > BARCODE_TIMEOUT):
                    barcode_buffer.clear()

                if len(barcode_buffer) >= MIN_BARCODE_LENGTH:
                    full_barcode = "".join(barcode_buffer)
                    print(f"[STANDARD] Processing barcode: {full_barcode}")
                    barcode_var.set(full_barcode)
                    combo1.focus_set()

                    try:
                        if not combo1.get().strip():
                            show_custom_popup("Warning", image_path="images/warning_emptyField.png")
                        else:
                            if len(full_barcode) == 10:
                                leadBarcode = full_barcode
                                isoBarcode = None
                            elif len(full_barcode) == 11:
                                leadBarcode = None
                                isoBarcode = full_barcode
                            containerID = None
                            orderNumber = None

                            send_tracking_data(
                                containerID, orderNumber, leadBarcode, isoBarcode,
                                combo1.get(), employee_name_var.get(),
                                server_ip="192.168.111.230", port=8080
                            )
                    except Exception as e:
                        print(f"[STANDARD] Error processing barcode: {e}")
                        show_custom_popup("Connection Error", image_path="images/errorConnection.png")

                barcode_buffer.clear()
                scanning["completed"] = True

        root.after(50, poll_queue)

    root.after(50, poll_queue)

    # ---------------- Main Loop ----------------
    print("[STANDARD] Starting mainloop...")
    root.mainloop()
    
    # This code only runs after window is destroyed
    print("[STANDARD] Mainloop ended, cleaning up...")
    if 'p' in locals():
        try:
            p.terminate()
            print("[STANDARD] Barcode process terminated")
        except:
            pass
    
    print(f"[STANDARD] Returning window_result: {window_result}")
    return window_result
