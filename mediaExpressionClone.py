import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import fitz  # PyMuPDF for PDF handling

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False

class DraggableImage:
    def __init__(self, canvas, image_path, x, y, size=150):
        self.canvas = canvas
        self.image_path = image_path
        self.is_pdf = image_path.lower().endswith('.pdf')
        # Remove file extension from filename
        self.filename = os.path.splitext(os.path.basename(image_path))[0]
        self.x = x
        self.y = y
        self.size = size
        self.drag_data = {"x": 0, "y": 0}
        self.resize_mode = False
        self.resize_start = {"x": 0, "y": 0, "size": 0}
        
        # Load and resize image
        if self.is_pdf:
            self.load_pdf_thumbnail()
        else:
            self.original_image = Image.open(image_path)
        
        self.update_thumbnail()
        
        # Create canvas image
        self.canvas_image = self.canvas.create_image(x, y, image=self.photo, anchor="nw")
        
        # Create border rectangle
        self.border = self.canvas.create_rectangle(
            x, y, x + self.actual_width, y + self.actual_height,
            outline="black", width=1
        )
        
        # Create selection highlight (initially hidden)
        self.selection_highlight = self.canvas.create_rectangle(
            x - 3, y - 3, x + self.actual_width + 3, y + self.actual_height + 3,
            outline="blue", width=3, state='hidden'
        )
        
        # Create filename text below image
        self.text = self.canvas.create_text(
            x + self.actual_width // 2, 
            y + self.actual_height + 10,
            text=self.filename,
            font=("Arial", 9),
            fill="black",
            width=self.actual_width + 20
        )
        
        # Create resize handle (small square in bottom-right corner)
        handle_size = 8
        self.resize_handle = self.canvas.create_rectangle(
            x + self.actual_width - handle_size,
            y + self.actual_height - handle_size,
            x + self.actual_width,
            y + self.actual_height,
            fill="blue",
            outline="darkblue",
            width=1
        )
        
        # Bind events to all elements
        for item in [self.canvas_image, self.border, self.text]:
            self.canvas.tag_bind(item, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(item, "<B1-Motion>", self.on_drag)
            self.canvas.tag_bind(item, "<ButtonPress-3>", self.on_right_click)
        
        # Bind resize handle
        self.canvas.tag_bind(self.resize_handle, "<ButtonPress-1>", self.on_resize_start)
        self.canvas.tag_bind(self.resize_handle, "<B1-Motion>", self.on_resize_drag)
        self.canvas.tag_bind(self.resize_handle, "<Enter>", lambda e: self.canvas.config(cursor="size_nw_se"))
        self.canvas.tag_bind(self.resize_handle, "<Leave>", lambda e: self.canvas.config(cursor=""))
    
    def select(self):
        """Select this image"""
        # Deselect any previously selected image
        if app.selected_image and app.selected_image != self:
            app.selected_image.deselect()
        
        app.selected_image = self
        self.canvas.itemconfig(self.selection_highlight, state='normal')
        self.canvas.tag_raise(self.selection_highlight)
    
    def deselect(self):
        """Deselect this image"""
        self.canvas.itemconfig(self.selection_highlight, state='hidden')
        if app.selected_image == self:
            app.selected_image = None
    
    def load_pdf_thumbnail(self):
        """Load first page of PDF as thumbnail"""
        try:
            pdf_doc = fitz.open(self.image_path)
            first_page = pdf_doc[0]
            
            # Render page to pixmap
            zoom = 2  # Higher zoom for better quality
            mat = fitz.Matrix(zoom, zoom)
            pix = first_page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            from io import BytesIO
            self.original_image = Image.open(BytesIO(img_data))
            
            pdf_doc.close()
        except Exception as e:
            # Create a placeholder image if PDF loading fails
            self.original_image = Image.new('RGB', (200, 250), color='lightgray')
            print(f"Error loading PDF: {e}")
    
    def update_thumbnail(self):
        # Resize image maintaining aspect ratio
        img = self.original_image.copy()
        img.thumbnail((self.size, self.size), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)
        self.actual_width = img.width
        self.actual_height = img.height
    
    def on_press(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
        self.select()  # Select this image when clicked
    
    def on_drag(self, event):
        dx = event.x - self.drag_data["x"]
        dy = event.y - self.drag_data["y"]
        
        # Calculate new position
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Constrain to canvas bounds
        new_x = max(0, min(new_x, canvas_width - self.actual_width))
        new_y = max(0, min(new_y, canvas_height - self.actual_height - 25))  # -25 for text space
        
        # Check for collisions with other images
        for other in app.images:
            if other is self:
                continue
            
            # Check if this position would overlap with another image
            if self.check_collision(new_x, new_y, other):
                # Don't allow this movement
                return
        
        # Calculate actual movement
        actual_dx = new_x - self.x
        actual_dy = new_y - self.y
        
        # Move all elements together
        self.canvas.move(self.canvas_image, actual_dx, actual_dy)
        self.canvas.move(self.border, actual_dx, actual_dy)
        self.canvas.move(self.text, actual_dx, actual_dy)
        self.canvas.move(self.resize_handle, actual_dx, actual_dy)
        self.canvas.move(self.selection_highlight, actual_dx, actual_dy)
        
        self.x = new_x
        self.y = new_y
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def check_collision(self, x, y, other):
        """Check if position (x, y) would cause collision with another image"""
        # Get bounds of this image at new position
        my_left = x
        my_right = x + self.actual_width
        my_top = y
        my_bottom = y + self.actual_height + 25  # Include text space
        
        # Get bounds of other image
        other_left = other.x
        other_right = other.x + other.actual_width
        other_top = other.y
        other_bottom = other.y + other.actual_height + 25
        
        # Check for overlap
        if (my_left < other_right and my_right > other_left and
            my_top < other_bottom and my_bottom > other_top):
            return True
        return False
    
    def on_resize_start(self, event):
        self.resize_start["x"] = event.x
        self.resize_start["y"] = event.y
        self.resize_start["size"] = self.size
        self.select()  # Select this image when resizing
    
    def on_resize_drag(self, event):
        # Calculate size change based on diagonal distance
        dx = event.x - self.resize_start["x"]
        dy = event.y - self.resize_start["y"]
        dist = (dx + dy) / 2  # Average of x and y movement
        
        new_size = max(50, self.resize_start["size"] + dist)  # Minimum size of 50
        self.size = int(new_size)
        self.update_thumbnail()
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        
        # Update border position and size
        self.canvas.coords(self.border, 
                          self.x, self.y, 
                          self.x + self.actual_width, 
                          self.y + self.actual_height)
        
        # Update text position and width
        self.canvas.coords(self.text, 
                          self.x + self.actual_width // 2, 
                          self.y + self.actual_height + 10)
        self.canvas.itemconfig(self.text, width=self.actual_width + 20)
        
        # Update resize handle position
        handle_size = 8
        self.canvas.coords(self.resize_handle,
                          self.x + self.actual_width - handle_size,
                          self.y + self.actual_height - handle_size,
                          self.x + self.actual_width,
                          self.y + self.actual_height)
        
        # Update selection highlight
        self.canvas.coords(self.selection_highlight,
                          self.x - 3, self.y - 3,
                          self.x + self.actual_width + 3,
                          self.y + self.actual_height + 3)
        
        # Update selection highlight
        self.canvas.coords(self.selection_highlight,
                          self.x - 3, self.y - 3,
                          self.x + self.actual_width + 3,
                          self.y + self.actual_height + 3)
    
    def on_right_click(self, event):
        # Show resize menu
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="Resize Larger", command=lambda: self.resize(1.2))
        menu.add_command(label="Resize Smaller", command=lambda: self.resize(0.8))
        menu.add_command(label="Delete", command=self.delete)
        menu.post(event.x_root, event.y_root)
    
    def resize(self, factor):
        self.size = int(self.size * factor)
        self.update_thumbnail()
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        
        # Update border position and size
        self.canvas.coords(self.border, 
                          self.x, self.y, 
                          self.x + self.actual_width, 
                          self.y + self.actual_height)
        
        # Update text position and width
        self.canvas.coords(self.text, 
                          self.x + self.actual_width // 2, 
                          self.y + self.actual_height + 10)
        self.canvas.itemconfig(self.text, width=self.actual_width + 20)
        
        # Update resize handle position
        handle_size = 8
        self.canvas.coords(self.resize_handle,
                          self.x + self.actual_width - handle_size,
                          self.y + self.actual_height - handle_size,
                          self.x + self.actual_width,
                          self.y + self.actual_height)
    
    def delete(self):
        self.canvas.delete(self.canvas_image)
        self.canvas.delete(self.border)
        self.canvas.delete(self.text)
        self.canvas.delete(self.resize_handle)
        self.canvas.delete(self.selection_highlight)
        if app.selected_image == self:
            app.selected_image = None
        if self in app.images:
            app.images.remove(self)

class ThumbnailApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Thumbnail Manager")
        
        # Calculate window size based on screen height and A4 proportions
        screen_height = self.root.winfo_screenheight()
        window_height = int(screen_height * 0.8)
        button_bar_height = 60
        canvas_height = window_height - button_bar_height
        
        # A4 aspect ratio (210mm x 297mm = 1:1.414)
        canvas_width = int(canvas_height / 1.414)
        window_width = canvas_width
        
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(False, False)  # Disable window resizing
        
        self.images = []
        self.selected_image = None  # Track selected image
        
        # Create UI
        self.create_ui()
        
        # Bind backspace to delete selected image
        self.root.bind('<BackSpace>', self.delete_selected)
        self.root.bind('<Delete>', self.delete_selected)
        
        # Enable drag and drop if available
        if DND_AVAILABLE:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind('<<Drop>>', self.on_drop)
    
    def create_ui(self):
        # Top frame with buttons
        top_frame = tk.Frame(self.root, bg="#e0e0e0", height=60)
        top_frame.pack(side=tk.TOP, fill=tk.X)
        top_frame.pack_propagate(False)
        
        btn_add = tk.Button(top_frame, text="Add Images", command=self.add_images, 
                           bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=5)
        btn_add.pack(side=tk.LEFT, padx=10, pady=10)
        
        btn_export = tk.Button(top_frame, text="Export to PDF", command=self.export_pdf,
                              bg="#2196F3", fg="white", font=("Arial", 12), padx=20, pady=5)
        btn_export.pack(side=tk.LEFT, padx=10, pady=10)
        
        btn_clear = tk.Button(top_frame, text="Clear All", command=self.clear_all,
                             bg="#f44336", fg="white", font=("Arial", 12), padx=20, pady=5)
        btn_clear.pack(side=tk.LEFT, padx=10, pady=10)
        
        # Canvas for images - fixed size, no resizing
        canvas_frame = tk.Frame(self.root)
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Prevent canvas from being resized
        self.canvas.bind('<Configure>', self.on_canvas_configure)
    
    def on_canvas_configure(self, event):
        """Maintain A4 aspect ratio when window is resized"""
        # This ensures the canvas maintains its proportions
        pass
    
    def on_drop(self, event):
        files = event.data
        # Handle different formats of dropped data
        if files.startswith('{'):
            # Windows format with braces
            files = files.strip('{}').split('} {')
        else:
            files = files.split()
        
        for file in files:
            file = file.strip()
            if file and os.path.isfile(file) and file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.pdf')):
                self.add_image(file)
    

    
    def add_images(self):
        files = filedialog.askopenfilenames(
            title="Select Images or PDFs",
            filetypes=[("Image and PDF files", "*.png *.jpg *.jpeg *.gif *.bmp *.pdf"), 
                      ("All files", "*.*")]
        )
        for file in files:
            self.add_image(file)
    
    def add_image(self, filepath):
        try:
            # Create image without positioning yet
            img = DraggableImage(self.canvas, filepath, 0, 0)
            self.images.append(img)
            
            # Rearrange all images to fit
            self.rearrange_all_images()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {str(e)}")
    
    def rearrange_all_images(self):
        """Rearrange all images to fit on canvas, resizing if necessary"""
        if not self.images:
            return
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            # Canvas not ready yet, defer rearrangement
            self.canvas.after(100, self.rearrange_all_images)
            return
        
        num_images = len(self.images)
        
        # Calculate optimal grid layout
        cols = int((num_images ** 0.5) * 1.2)  # Slightly favor horizontal layout
        if cols < 1:
            cols = 1
        rows = (num_images + cols - 1) // cols
        
        # Calculate available space per image
        padding = 10
        text_space = 25
        available_width = (canvas_width - padding * (cols + 1)) / cols
        available_height = (canvas_height - padding * (rows + 1) - text_space) / rows
        
        # Determine size for all images (maintain aspect ratio)
        target_size = min(available_width, available_height)
        target_size = max(50, int(target_size))  # Minimum 50px
        
        # Position all images
        for idx, img in enumerate(self.images):
            col = idx % cols
            row = idx // cols
            
            # Resize image
            img.size = target_size
            img.update_thumbnail()
            img.canvas.itemconfig(img.canvas_image, image=img.photo)
            
            # Calculate position
            x = padding + col * (available_width + padding)
            y = padding + row * (available_height + padding)
            
            # Calculate movement needed
            dx = x - img.x
            dy = y - img.y
            
            # Move all image elements
            img.canvas.move(img.canvas_image, dx, dy)
            img.canvas.move(img.border, dx, dy)
            img.canvas.move(img.text, dx, dy)
            img.canvas.move(img.resize_handle, dx, dy)
            img.canvas.move(img.selection_highlight, dx, dy)
            
            # Update position
            img.x = x
            img.y = y
            
            # Update all element positions and sizes
            img.canvas.coords(img.border,
                            img.x, img.y,
                            img.x + img.actual_width,
                            img.y + img.actual_height)
            
            img.canvas.coords(img.text,
                            img.x + img.actual_width // 2,
                            img.y + img.actual_height + 10)
            img.canvas.itemconfig(img.text, width=img.actual_width + 20)
            
            handle_size = 8
            img.canvas.coords(img.resize_handle,
                            img.x + img.actual_width - handle_size,
                            img.y + img.actual_height - handle_size,
                            img.x + img.actual_width,
                            img.y + img.actual_height)
            
            img.canvas.coords(img.selection_highlight,
                            img.x - 3, img.y - 3,
                            img.x + img.actual_width + 3,
                            img.y + img.actual_height + 3)
    
    def clear_all(self):
        if messagebox.askyesno("Confirm", "Clear all images?"):
            for img in self.images[:]:
                img.delete()
            self.images.clear()
            self.selected_image = None
    
    def delete_selected(self, event=None):
        """Delete the currently selected image"""
        if self.selected_image:
            self.selected_image.delete()
    
    def export_pdf(self):
        if not self.images:
            messagebox.showwarning("Warning", "No images to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        
        if not filename:
            return
        
        try:
            # Create a snapshot of the canvas
            self.save_canvas_as_pdf(filename)
            messagebox.showinfo("Success", f"PDF saved to: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export PDF: {str(e)}")
    
    def save_canvas_as_pdf(self, filename):
        """Save canvas as image and embed in PDF"""
        from PIL import ImageGrab
        import tempfile
        
        # Get canvas position on screen
        x = self.canvas.winfo_rootx()
        y = self.canvas.winfo_rooty()
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        # Capture canvas as image
        canvas_image = ImageGrab.grab(bbox=(x, y, x + w, y + h))
        
        # Save to temporary file
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        temp_img_path = temp_img.name
        canvas_image.save(temp_img_path)
        temp_img.close()
        
        # Create PDF with the canvas image
        c = canvas.Canvas(filename, pagesize=letter)
        page_width, page_height = letter
        
        # Calculate scaling to fit page while maintaining aspect ratio
        img_aspect = w / h
        page_aspect = page_width / page_height
        
        if img_aspect > page_aspect:
            # Image is wider - fit to width
            pdf_width = page_width
            pdf_height = page_width / img_aspect
            pdf_x = 0
            pdf_y = (page_height - pdf_height) / 2
        else:
            # Image is taller - fit to height
            pdf_height = page_height
            pdf_width = page_height * img_aspect
            pdf_x = (page_width - pdf_width) / 2
            pdf_y = 0
        
        c.drawImage(temp_img_path, pdf_x, pdf_y, width=pdf_width, height=pdf_height)
        c.save()
        
        # Clean up temp file
        import os
        os.unlink(temp_img_path)

if __name__ == "__main__":
    if DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        print("Note: tkinterdnd2 not installed. Drag-and-drop disabled. Install with: pip install tkinterdnd2")
    
    app = ThumbnailApp(root)
    root.mainloop()
