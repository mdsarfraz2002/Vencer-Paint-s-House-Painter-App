'''Vencer Paint's House Painter App using Tkinter and OpenCV'''

# Importing the necessary packages
import os
import numpy as np
import cv2
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from FewColors import ColorPicker
from sklearn.cluster import KMeans
from PIL import Image, ImageTk, ImageDraw
from PIL import ImageDraw


# Creating the HousePainterApp class
class HousePainterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vencer Paint's House Painter App")
        self.root.configure(bg="#f0f0f0")  # Setting background color
        self.root.geometry("1200x900")

        # Creating frames for canvas and buttons
        self.canvas_frame = tk.Frame(root, bg="#f0f0f0")
        self.canvas_frame.grid(row=0, column=0, sticky="nsew")

        self.button_frame = tk.Frame(root, bg="#f0f0f0")
        self.button_frame.grid(row=0, column=1, padx=20, sticky="ns")

        # Creating canvas inside canvas frame
        self.canvas = tk.Canvas(self.canvas_frame, bg="white", borderwidth=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0, uniform="right_column")

        self.upload_image_path = "Images/1.png"
        self.pick_color_image_path = "Images/2.png"
        self.undo_image_path = "Images/3.png"
        self.clear_paint_image_path = "Images/4.png"
        self.save_image_path = "Images/5.png"
        self.eraser_image_path = "Images/eraser.png"


        # Creating PhotoImage objects for each button
        self.upload_image = self.load_and_resize_image(self.upload_image_path, (50, 50))
        self.pick_color_image = self.load_and_resize_image(self.pick_color_image_path, (50, 50))
        self.undo_image = self.load_and_resize_image(self.undo_image_path, (50, 50))
        self.eraser_image = self.load_and_resize_image(self.eraser_image_path, (50, 50))
        self.clear_paint_image = self.load_and_resize_image(self.clear_paint_image_path, (50, 50))
        self.saving_image = self.load_and_resize_image(self.save_image_path, (50, 50))

        self.max_canvas_width = 1100
        self.max_canvas_height = 900
        # Loading and resizing the logo image
        self.logo_image_path = "Images/logo.png"
        self.logo_image = self.load_and_resize_image(self.logo_image_path, (120, 80))
        
        # Creating a frame for logo and buttons
        self.logo_button_frame = tk.Frame(self.button_frame, bg="#f0f0f0")
        self.logo_button_frame.pack(fill=tk.X, pady=(40, 80))

        # Adding the logo label to the logo_button_frame
        self.logo_label = tk.Label(self.logo_button_frame, image=self.logo_image, bg="#f0f0f0")
        self.logo_label.pack(fill=tk.X)

        self.load_button = tk.Button(self.button_frame, image=self.upload_image,  command=self.load_photo, text="Upload", compound=tk.LEFT, bg="#4CAF50", fg="black", borderwidth=0, highlightthickness=0)
        self.load_button.pack(fill=tk.X, pady=18)

        self.color_picker_button = tk.Button(self.button_frame, image=self.pick_color_image, command=self.pick_color, text="Paint",compound=tk.LEFT, bg="#FFC107", fg="black", borderwidth=0, highlightthickness=0)
        self.color_picker_button.pack(fill=tk.X, pady=18)

        self.clear_button = tk.Button(self.button_frame, image=self.undo_image, command=self.undo_paint, text = "Undo", bg="#E91E63",compound=tk.LEFT, fg="black", borderwidth=0, highlightthickness=0)
        self.clear_button.pack(fill=tk.X, pady=18)

        self.segmented_image = None
        self.color = None
        self.undo_stack = []

        self.eraser_button = tk.Button(self.button_frame, image=self.eraser_image, command=self.set_eraser, text="Eraser", compound=tk.LEFT, bg="#FFFFFF", fg="black", borderwidth=0, highlightthickness=0)
        self.eraser_button.pack(fill=tk.X, pady=18)

        self.clear_paint_button = tk.Button(self.button_frame, image=self.clear_paint_image, command=self.clear_paint, text="Clear",compound=tk.LEFT, bg="#FF5722", fg="black", borderwidth=0, highlightthickness=0)
        self.clear_paint_button.pack(fill=tk.X, pady=18)

        self.save_button = tk.Button(self.button_frame, image=self.saving_image, command=self.save_image, text="Save", bg="#2196F3",compound=tk.LEFT, fg="black", borderwidth=0, highlightthickness=0)
        self.save_button.pack(fill=tk.X, pady=18)
        self.root.grid_columnconfigure(1, weight=0, uniform="right_column")
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.original_colors = set()

    # Function to load and resize images
    def load_and_resize_image(self, image_path, size):
        image = Image.open(image_path)
        resized_image = image.resize(size, Image.LANCZOS)

        return ImageTk.PhotoImage(resized_image)
    
    # Function to set the eraser
    def set_eraser(self):
        self.color = "#FFFFFF"
        self.color_picker_button.config(bg=self.color)

    # Function to load the image
    def load_photo(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            house_image = cv2.imread(file_path)
            self.segmented_image = house_image.copy()
            self.undo_stack = []
            self.display_image(self.segmented_image)

    # Function to display the image
    def display_image(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width, _ = image_rgb.shape

        canvas_width = self.canvas.winfo_width()  
        canvas_height = self.canvas.winfo_height()  

        # Calculating aspect ratios
        img_aspect = width / height
        canvas_aspect = canvas_width / canvas_height

        # Determining new dimensions based on aspect ratios
        if img_aspect > canvas_aspect:
            # Width will be the limiting factor
            new_width = canvas_width
            new_height = int(canvas_width / img_aspect)
        else:
            # Height will be the limiting factor
            new_height = canvas_height
            new_width = int(canvas_height * img_aspect)

        # Resizing and displaying image
        pil_image = Image.fromarray(cv2.resize(image_rgb, (new_width, new_height)))
        self.photo = ImageTk.PhotoImage(image=pil_image)
        
        # Centering the image on the canvas
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        self.canvas.config(width=new_width, height=new_height)
        self.canvas.create_image(center_x, center_y, anchor="center", image=self.photo)
        
        # Storing the dimensions for later use
        self.image_width = new_width
        self.image_height = new_height
        
        self.canvas.image = self.photo  # Keeping a reference to avoid garbage collection

    # Function to handle mouse clicks on the canvas
    def on_canvas_click(self, event):
        if self.segmented_image is not None:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            img_height, img_width, _ = self.segmented_image.shape

            # Calculating the offsets to center the image
            x_offset = (canvas_width - self.image_width) // 2
            y_offset = (canvas_height - self.image_height) // 2

            # Converting canvas coordinates to image coordinates, accounting for the offset
            x = int((event.x - x_offset) / self.image_width * img_width)
            y = int((event.y - y_offset) / self.image_height * img_height)


            if 0 <= x < img_width and 0 <= y < img_height:
                if self.color == "#FFFFFF":  # If eraser is selected
                    self.paint_selected_area(x, y, (255, 255, 255))  # Filling with eraser color
                else:
                    if self.color is not None:
                        hex_color = self.color  # Getting the color as a string
                        bgr_color = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))  # Skipping '#' character
                        bgr_color = (bgr_color[2], bgr_color[1], bgr_color[0])  # Converting RGB to BGR
                        self.paint_selected_area(x, y, bgr_color)


    # Function to paint the selected area
    def paint_selected_area(self, x, y, color):
        if self.segmented_image is not None:
            mask = np.zeros((self.segmented_image.shape[0] + 2, self.segmented_image.shape[1] + 2), np.uint8)
            seed_point = (x, y)
            target_color = self.segmented_image[y, x]

            # Explicitly casting the color to a tuple of integers
            fill_color = tuple(map(int, color))

            # Save the state before painting for undo functionality
            self.undo_stack.append(self.segmented_image.copy())

            try:
                # Test with hardcoded values
                cv2.floodFill(self.segmented_image.copy(), mask.copy(), seed_point, (0, 255, 0),
                            loDiff=(20, 20, 20, 20), upDiff=(20, 20, 20, 20))

                # Actual flood fill call
                cv2.floodFill(self.segmented_image, mask, seed_point, fill_color,
                            loDiff=(20, 20, 20, 20), upDiff=(20, 20, 20, 20))
            except Exception as e:
                print(f"Exception: {e}")

            self.display_image(self.segmented_image)

    # Function to fill the region
    def fill_region(self, mask, seed_point, target_color, fill_color):
        stack = [seed_point]
        while stack:
            x, y = stack.pop()
            if mask[y, x].any():
                continue
            if self.is_similar_color(self.segmented_image[y, x], target_color):
                mask[y, x] = fill_color
                if x > 0:
                    stack.append((x - 1, y))
                if x < self.segmented_image.shape[1] - 1:
                    stack.append((x + 1, y))
                if y > 0:
                    stack.append((x, y - 1))
                if y < self.segmented_image.shape[0] - 1:
                    stack.append((x, y + 1))

    # Function to check if two colors are similar
    def is_similar_color(self, color1, color2, tolerance=20):
        diff = np.abs(np.array(color1, dtype=np.int16) - np.array(color2, dtype=np.int16))
        return np.all(diff <= tolerance)

    # Function to pick the color
    def pick_color(self):
        color_picker = ColorPicker(self.root, self.update_color)

    # Function to update the color
    def update_color(self, color):
        self.color = color
        self.color_picker_button.config(bg=color)

    # Function to undo the paint
    def undo_paint(self):
        if self.segmented_image is not None and self.undo_stack:
            self.segmented_image = self.undo_stack.pop()
            painted_mask = np.where(self.segmented_image != self.segmented_image[0, 0], 255, 0).astype(np.uint8)
            clear_mask = cv2.bitwise_not(painted_mask)
            self.segmented_image = np.where(clear_mask != 0, self.segmented_image[0, 0], self.segmented_image)
            self.display_image(self.segmented_image)

    # Function to clear the paint 
    def clear_paint(self):
        if self.segmented_image is not None and self.undo_stack:
            # Reverting to the original image
            self.segmented_image = self.undo_stack[0]
            self.undo_stack.clear()  # Clearing the undo stack
            self.display_image(self.segmented_image)

    # Function to extract unique colors
    def extract_unique_colors(image, n_clusters=10):
        image_reshaped = image.reshape((-1, 3))
        kmeans = KMeans(n_clusters=n_clusters).fit(image_reshaped)
        unique_colors = np.round(kmeans.cluster_centers_).astype(int)
        return set([tuple(color) for color in unique_colors])
    
    # Function to round the color
    def round_color(self, value, base=10):
        return base * round(value/base)

    # Function to extract unique colors
    def extract_unique_colors(self,image):
        image = self.segmented_image
        unique_colors = set()
        for y in range(image.shape[0]):
            for x in range(image.shape[1]):
                b, g, r = image[y, x]
                rb, rg, rr = self.round_color(b), self.round_color(g), self.round_color(r)
                unique_colors.add((rb, rg, rr))
        return unique_colors

    # Function to save the image
    def save_image(self):
        if self.segmented_image is not None:
            filetypes = [
                ("PDF files", "*.pdf"),
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg;*.jpeg")
            ]
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=filetypes)
            
            if not save_path:
                return  # User canceled the save dialog
            
            extension = os.path.splitext(save_path)[1].lower()

            # Calculating positions
            logo_size = (100, 100)  # Logo width and height
            logo_position = (10, 10)  # Logo's top left position
            image_position = (10, 130)  # Image's top left position, 20px below the logo
            colors_position = (10, self.segmented_image.shape[0] + 250)  # Colors starting position

            width, height = self.segmented_image.shape[1], self.segmented_image.shape[0]
            canvas_height = colors_position[1] + 150  # Space for color details

            # Creating a new canvas (an empty image)
            canvas_image = Image.new('RGB', (width + 20, canvas_height), 'white')  # +20 for right and left margins

            # Pasting the logo with transparency
            logo_image = Image.open(self.logo_image_path).resize(logo_size)
            canvas_image.paste(logo_image, logo_position, logo_image)  # Using logo_image as the mask to keep transparency

            # Pasting the painted image below the logo
            painted_image_pil = Image.fromarray(cv2.cvtColor(self.segmented_image, cv2.COLOR_BGR2RGB))
            canvas_image.paste(painted_image_pil, image_position)

            # Drawing the colors used
            draw = ImageDraw.Draw(canvas_image)
            current_colors = self.extract_unique_colors(self.segmented_image)
            painted_colors = current_colors - self.original_colors

            start_x, start_y = colors_position
            for color in painted_colors:
                color_hex = '#%02x%02x%02x' % (color[2], color[1], color[0])
                draw.rectangle([(start_x, start_y), (start_x + 50, start_y + 50)], fill=color_hex)
                draw.text((start_x + 60, start_y + 15), f"Color Code: {color_hex}", fill="black")
                start_y += 70  # Adjusting based on the box size and the desired spacing

            # Saving the canvas in the chosen format
            if extension == ".pdf":
                pdf_path = "temp_canvas_image.png"
                canvas_image.save(pdf_path)
                
                pdf_canvas = canvas.Canvas(save_path, pagesize=letter)
                pdf_canvas.drawImage(ImageReader(pdf_path), 0, 0, width=width + 20, height=canvas_height)
                os.remove(pdf_path)
                pdf_canvas.save()
            elif extension in [".png", ".jpg", ".jpeg"]:
                canvas_image.save(save_path)

# Main function
if __name__ == "__main__":
    root = tk.Tk()
    app = HousePainterApp(root)
    root.mainloop()