import os
import sys
import re
from tkinter import Tk, Canvas, Frame, Listbox, Toplevel, IntVar, Label
from tkinter import ttk
from tkinter.ttk import Style, Button as TtkButton
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageFilter
from PDF_analysis import extract_pdf_info
from clientCalls import send_tracking_data, fetch_next_container_id, fetch_employee_start_time, log_employee_time, loggedOut, loggedIn
from datetime import datetime, timedelta

# ---------------- Resource Path ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# ---------------- PDF Object ----------------
class PDFFile:
    def __init__(self, path):
        self.path = path
        self.filename = os.path.basename(path)
        self.text = None
        self.orders = []
        self.barcodes = []

IS_WINDOWS = sys.platform.startswith("win")

def open_and_subtle_sharpen_image(path, size):
    img = Image.open(resource_path(path))
    img = img.resize(size, Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=1, percent=80, threshold=1))
    return img

# ---------------- Batch Moved Popup ----------------
def show_batch_moved_popup(root):
    popup = Toplevel(root)
    popup.title("Batch Moved")
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
        img = open_and_subtle_sharpen_image("images/batchMoved.png", (popup_width, popup_height))
        photo = ImageTk.PhotoImage(img)
        img_label = Label(popup, image=photo)
        img_label.image = photo
        img_label.place(x=0, y=0, width=popup_width, height=popup_height)
    except Exception as e:
        print(f"[Popup] Failed to load batchMoved image: {e}")
        popup.configure(bg="#E6E1D6")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Popup.TButton", background="#6D05FF", foreground="white",
                    font=("Arial", 10, "bold"), padding=5)
    style.map("Popup.TButton", background=[('active', '#8B1CFF')],
              foreground=[('disabled', 'gray')])

    ttk.Button(popup, text="OK", command=popup.destroy, style="Popup.TButton").place(
        relx=0.5, rely=0.85, anchor="center"
    )

    if IS_WINDOWS:
        popup.update()
    popup.wait_window()

# ---------------- Mode Selector ----------------
# ---------------- Mode Selector (Fixed + Taller + Width matches drop box) ----------------
class ModeSelector(Frame):
    def __init__(self, master, pdf_files, file_listbox, update_confirm_state, loggedEmployee, drop_frame, **kwargs):
        super().__init__(master, bg="#E6E1D6", bd=1, relief="solid", **kwargs)
        self.pdf_files = pdf_files
        self.file_listbox = file_listbox
        self.update_confirm_state = update_confirm_state
        self.loggedEmployee = loggedEmployee
        self.drop_frame = drop_frame  # reference to drop box frame

        # Use tk.Label for reliable background color
        self.text_label = Label(
            self,
            text=f"{self.loggedEmployee.employeeName}'s File Dropbox",
            anchor="center",
            bg="#E6E1D6",
            fg="black",
            font=("Arial", 12, "bold")
        )
        self.text_label.pack(fill="both", expand=True)

        # Initial sizing
        self.update_size(master.winfo_width(), master.winfo_height())

        # Bind to window resize
        master.bind("<Configure>", self._on_master_resize)

    def _on_master_resize(self, event):
        # Resize frame and font relative to window size
        self.update_size(event.width, event.height)

    def update_size(self, window_width, window_height):
        # Height is 1.3× default
        frame_height = max(30, int(window_height * 0.05 * 1.3))
        # Width matches drop_frame width
        frame_width = self.drop_frame.winfo_width() or int(window_width * 0.8)

        self.config(width=frame_width, height=frame_height)

        # Resize font relative to frame height
        font_size = max(8, int(frame_height * 0.45))
        self.text_label.config(font=("Arial", font_size, "bold"))


# ---------------- Time Selector ----------------
class TimeSelector:
    def __init__(self, master, x, y, width, height, label_text="Start", default_hour=9, default_minute=0):
        self.master = master
        self.x, self.y, self.width, self.height = x, y, width, height
        self.label_text = label_text
        self.hour_var = IntVar(value=default_hour)
        self.minute_var = IntVar(value=default_minute)

        padding = int(self.height * 0.05)
        label_height = int(self.height * 0.25)
        arrow_size = int(self.height * 0.25)
        time_width = self.width - 2 * (arrow_size + padding)
        font_size_label = max(8, int(label_height * 0.6))
        font_size_time = max(8, int(arrow_size * 0.6))

        self.label = Label(self.master, text=self.label_text, fg="black", bg="#E6E1D6",
                           font=("Arial", font_size_label, "bold"))
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

# ---------------- Time Popup ----------------
def show_time_popup(root, employee_name):
    popup = Toplevel(root)
    popup.transient(root)
    popup.grab_set()
    if not IS_WINDOWS:
        popup.overrideredirect(True)
    else:
        popup.title("Set Work Time")

    root.update_idletasks()
    main_width = root.winfo_width() or 800
    main_height = root.winfo_height() or 450
    aspect_ratio = 1920 / 1080
    popup_width = max(1, main_width)
    popup_height = max(1, int(popup_width / aspect_ratio))
    x = root.winfo_x() + (main_width - popup_width)//2
    y = root.winfo_y() + (main_height - popup_height)//2
    popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    if IS_WINDOWS:
        popup.deiconify()
        popup.lift()
        popup.focus_force()
        popup.update_idletasks()

    try:
        bg_image = Image.open(resource_path("images/setWorkTime.png")).resize((popup_width, popup_height), Image.LANCZOS)
        bg_photo = ImageTk.PhotoImage(bg_image)
        Label(popup, image=bg_photo).place(x=0, y=0, width=popup_width, height=popup_height)
    except Exception as e:
        print(f"[Popup] Failed to load background image: {e}")
        popup.configure(bg="#E6E1D6")

    y_pos = int(popup_height * 0.4)
    padding_x = int(0.05 * popup_width)
    time_width = int((popup_width - 3 * padding_x)//2 * 0.8)
    time_height = int(100 * 0.8)
    start_x = (popup_width - (2*time_width + padding_x))//2

    start_selector = TimeSelector(popup, x=start_x, y=y_pos, width=time_width, height=time_height, label_text="Start", default_hour=9, default_minute=0)
    end_selector   = TimeSelector(popup, x=start_x+time_width+padding_x, y=y_pos, width=time_width, height=time_height, label_text="End", default_hour=17, default_minute=0)


    def on_submit():
        today = datetime.now().date()
        start_time = datetime.combine(today, datetime.min.time()).replace(hour=start_selector.hour_var.get(), minute=start_selector.minute_var.get())
        end_time = datetime.combine(today, datetime.min.time()).replace(hour=end_selector.hour_var.get(), minute=end_selector.minute_var.get())
        if end_time < start_time:
            end_time += timedelta(days=1)
        try:
            response = log_employee_time(employee_name, start_time, end_time, server_ip="192.168.111.230", port=8080)
            if response.get("status") != "success":
                print(f"Failed to log time: {response.get('message','')}")
        except Exception as e:
            print("Connection Error:", e)
        popup.destroy()

    style = Style()
    style.theme_use('clam')
    style.configure("Popup.TButton", background="#6D05FF", foreground="white", font=("Arial", 10, "bold"), padding=5)
    style.map("Popup.TButton", background=[('active', '#8B1CFF')], foreground=[('disabled','gray')])
    TtkButton(popup, text="Submit", style="Popup.TButton", command=on_submit).place(relx=0.5, rely=0.85, anchor="center")
    if IS_WINDOWS: popup.update()
    popup.wait_window()

# ---------------- Batch Processing ----------------
def process_for_database(pdf_files, file_listbox, loggedEmployee, update_confirm_state, root):
    # --- PDFs (standard PDFFile objects) ---
    for file_obj in pdf_files:
        if isinstance(file_obj, PDFFile):
            orders, leads, isos = extract_pdf_info(file_obj.path)
            for i in range(len(orders)):
                for iso in isos[i]:
                    send_tracking_data(
                        None,
                        orders[i],
                        leads[i],
                        iso,
                        "Printer Station: Oneflow Order Forms Printed",
                        loggedEmployee.employeeName
                    )

    # --- JPEG/PNG and PDFs treated like images ---
    jpg_files = [f for f in pdf_files if isinstance(f, list)]
    if jpg_files:
        containerNum = fetch_next_container_id()
        for f in jpg_files:
            try:
                itemNum = f[2] if len(f) > 2 else None
                prodType = f[0]
                orderNumber = f[1]
                workstation_msg = f"Printer Station: Sent {orderNumber} To Printer"

                # 🔍 DEBUG PRINT
                print(f"[DEBUG] Sending tracking data → "
                      f"containerID={containerNum}, "
                      f"orderNumber={orderNumber}, "
                      f"itemNum={itemNum}, "
                      f"prodType={prodType}, "
                      f"employee={loggedEmployee.employeeName}, "
                      f"workstation='{workstation_msg}'")

                send_tracking_data(
                    containerNum,
                    orderNumber,
                    None,
                    None,
                    workstation_msg,
                    loggedEmployee.employeeName,
                    itemNum=itemNum,
                    prodType=prodType
                )
            except Exception as e:
                print(f"[ERROR] Failed to send {f[1]}: {e}")

    # --- Clear lists & GUI ---
    pdf_files.clear()
    file_listbox.delete(0,'end')
    update_confirm_state()
    show_batch_moved_popup(root)

# ---------------- Main Printing Menu ----------------
def create_printing_menu(loggedEmployee):
    root = TkinterDnD.Tk()
    root.title("Prodigi Ally")

    try:
        loggedIn(loggedEmployee.employeeName)
    except: pass

    screen_width, screen_height = root.winfo_screenwidth(), root.winfo_screenheight()
    window_size = int(min(screen_width, screen_height)*0.75)
    x_pos, y_pos = (screen_width-window_size)//2, (screen_height-window_size)//2
    root.geometry(f"{window_size}x{window_size}+{x_pos}+{y_pos}")
    root.resizable(True, True)

    canvas = Canvas(root, width=window_size, height=window_size, highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    bg_image_path = resource_path("images/printingMenu.png")
    bg_image = Image.open(bg_image_path).resize((window_size, window_size))
    canvas.bg_photo = ImageTk.PhotoImage(bg_image)
    canvas.create_image(0,0,anchor="nw",image=canvas.bg_photo)

    pdf_files = []
    drop_frame = Frame(root, bg="#E6E1D6", highlightbackground="black", highlightthickness=2)
    drop_frame.place(relx=0.49, rely=0.54, anchor="center", relwidth=0.8, relheight=0.6)

    style = Style()
    style.theme_use('clam')
    style.configure("Custom.Vertical.TScrollbar", background="#E6E1D6", troughcolor="#E6E1D6", arrowcolor="black")
    file_scrollbar = ttk.Scrollbar(drop_frame, orient="vertical", style="Custom.Vertical.TScrollbar")
    file_listbox = Listbox(drop_frame, bg="#E6E1D6", fg="black", bd=0, highlightthickness=0, relief="flat", yscrollcommand=file_scrollbar.set, selectbackground="#6D05FF", selectforeground="white")
    file_scrollbar.config(command=file_listbox.yview)
    file_listbox.pack(side="left", fill="both", expand=True, padx=(2,0), pady=2)
    file_scrollbar.pack(side="right", fill="y", padx=(0,2), pady=2)

    # ---------------- Drop Handler ----------------
    def update_confirm_state():
        confirm_button.state(['!disabled'] if pdf_files else ['disabled'])

    def drop(event):
        files = root.splitlist(event.data)
        for f in files:
            filename = os.path.basename(f).lower()

            # --- PDF handling ---
            if filename.endswith(".pdf") and all(not (isinstance(p, PDFFile) and p.path == f) for p in pdf_files):
                # PDFs treated like images (based on filename pattern)
                match = re.search(r"po00(\d+)_li(\d+)_?", filename)
                if match:
                    order_number = match.group(1)
                    item_number = int(match.group(2).lstrip("0") or "0")  # extract trailing _li00001_ → 1
                    prefix = filename.split("_")[0]
                    pdf_as_image_entry = [prefix, order_number, item_number]
                    pdf_files.append(pdf_as_image_entry)
                    file_listbox.insert("end", f"{order_number} : {prefix} : Item {item_number}")
                else:
                    # Standard PDF order sheets (no image-like pattern)
                    pdf_obj = PDFFile(f)
                    pdf_files.append(pdf_obj)
                    file_listbox.insert("end", os.path.basename(f))

            # --- JPEG/PNG handling ---
            elif filename.endswith((".jpg", ".png")):
                match = re.search(r"po00(\d+)_li(\d+)_?", filename)
                if match:
                    order_number = match.group(1)
                    item_number = int(match.group(2).lstrip("0") or "0")
                    prefix = filename.split("_")[0]
                    image_entry = [prefix, order_number, item_number]
                    pdf_files.append(image_entry)
                    file_listbox.insert("end", f"{order_number} : {prefix} : Item {item_number}")


        update_confirm_state()


    drop_frame.drop_target_register(DND_FILES)
    drop_frame.dnd_bind("<<Drop>>", drop)

    # ---------------- Buttons ----------------
    # ---------------- Buttons ----------------
    mode_selector = ModeSelector(root, pdf_files, file_listbox, update_confirm_state, loggedEmployee, drop_frame)
    mode_selector.place(relx=0.5, rely=0.19, anchor="center")

    
    style.configure("Green.TButton", background="#28A745", foreground="white")
    style.map("Green.TButton", background=[('active','#34D058')], foreground=[('disabled','gray')])

    style.configure("Red.TButton", background="#FF3B3B", foreground="white")
    style.map("Red.TButton", background=[('active','#FF6B6B')], foreground=[('disabled','gray')])

    style.configure("Purple.TButton", background="#6D05FF", foreground="white")
    style.map("Purple.TButton", background=[('active','#8B1CFF')], foreground=[('disabled','gray')])

    confirm_button = ttk.Button(root, text="Submit", style="Green.TButton",
                                command=lambda: process_for_database(pdf_files, file_listbox, loggedEmployee, update_confirm_state, root))
    confirm_button.place(relx=0.82, rely=0.88, anchor="center", relwidth=0.15, relheight=0.04)
    confirm_button.state(['disabled'])

    empty_button = ttk.Button(root, text="Empty", style="Red.TButton",
                              command=lambda: [pdf_files.clear(), file_listbox.delete(0,'end'), update_confirm_state()])
    empty_button.place(relx=0.65, rely=0.88, anchor="center", relwidth=0.15, relheight=0.04)

    logout_button = ttk.Button(root, text="Logout", style="Purple.TButton",
                               command=lambda: [loggedOut(loggedEmployee.employeeName, server_ip="192.168.111.230", port=8080), root.destroy()])
    logout_button.place(relx=0.48, rely=0.88, anchor="center", relwidth=0.15, relheight=0.04)

    # ---------------- Settings Cog Button ----------------
    try:
        cog_img_path = resource_path("images/settingsCog.png")
        cog_img = Image.open(cog_img_path)

        # Fixed size for the cog button
        cog_btn_size = int(window_size * 0.05)  # adjust as needed
        cog_img_size = int(cog_btn_size * 0.75)
        cog_img = cog_img.resize((cog_img_size, cog_img_size), Image.Resampling.LANCZOS)
        cog_photo = ImageTk.PhotoImage(cog_img)

        style = ttk.Style()
        style.theme_use('clam')
        # Cream-colored button style
        style.configure(
            "Cream.TButton",
            background="#E6E1D6",  # same as ModeSelector
            foreground="black",
            font=("Arial", 10, "bold"),
            padding=5
        )
        style.map(
            "Cream.TButton",
            background=[('active', '#DCD6C5')],  # slightly darker on hover
            foreground=[('disabled', 'gray')]
        )

        settings_btn = ttk.Button(
            root,
            image=cog_photo,
            style="Cream.TButton",
            command=lambda: show_time_popup(root, loggedEmployee.employeeName)
        )
        settings_btn.image = cog_photo  # keep reference

        # Absolute placement — put it wherever you want
        settings_btn.place(
            x=int(window_size * 0.82),  # adjust horizontal position
            y=int(window_size * 0.165),  # adjust vertical position
            width=cog_btn_size,
            height=cog_btn_size
        )

    except Exception as e:
        print("Error loading settings cog:", e)


    # ---------------- Dynamic Button Font Resizing ----------------
    import tkinter.font as tkFont

    def resize_buttons(event=None):
        w, h = root.winfo_width(), root.winfo_height()
        buttons = [
            (confirm_button, "Green.TButton"),
            (empty_button, "Red.TButton"),
            (logout_button, "Purple.TButton")
        ]
        for btn, style_name in buttons:
            btn_height = int(h * 0.04)
            font_size = max(8, int(btn_height * 0.45))
            style.configure(style_name, font=("Arial", font_size, "bold"), padding=int(font_size*0.4))

    root.bind("<Configure>", resize_buttons)
    root.after(100, resize_buttons)


    # ---------------- Check Time ----------------
    try:
        start_time = fetch_employee_start_time(loggedEmployee.employeeName)
        today = datetime.now().date()
        if not start_time or datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S").date() != today:
            root.after(0, lambda: show_time_popup(root, loggedEmployee.employeeName))
    except: pass

    root.mainloop()
