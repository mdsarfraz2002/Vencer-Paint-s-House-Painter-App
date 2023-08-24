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
from ColorPicker import ColorPicker

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

        # Creating PhotoImage objects for each button
        self.upload_image = self.load_and_resize_image(self.upload_image_path, (50, 50))
        self.pick_color_image = self.load_and_resize_image(self.pick_color_image_path, (50, 50))
        self.undo_image = self.load_and_resize_image(self.undo_image_path, (50, 50))
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

        self.clear_paint_button = tk.Button(self.button_frame, image=self.clear_paint_image, command=self.clear_paint, text="Clear",compound=tk.LEFT, bg="#FF5722", fg="black", borderwidth=0, highlightthickness=0)
        self.clear_paint_button.pack(fill=tk.X, pady=18)

        self.save_button = tk.Button(self.button_frame, image=self.saving_image, command=self.save_image, text="Save", bg="#2196F3",compound=tk.LEFT, fg="black", borderwidth=0, highlightthickness=0)
        self.save_button.pack(fill=tk.X, pady=18)
        self.root.grid_columnconfigure(1, weight=0, uniform="right_column")
        self.canvas.bind("<Button-1>", self.on_canvas_click)

    # Function to load and resize images
    def load_and_resize_image(self, image_path, size):
        image = Image.open(image_path)
        resized_image = image.resize(size, Image.LANCZOS)

        return ImageTk.PhotoImage(resized_image)

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

        # Calculating the dimensions to fit within the maximum canvas dimensions
        if width > self.max_canvas_width or height > self.max_canvas_height:
            aspect_ratio = width / height
            if width > self.max_canvas_width:
                width = self.max_canvas_width
                height = int(width / aspect_ratio)
            if height > self.max_canvas_height:
                height = self.max_canvas_height
                width = int(height * aspect_ratio)

        pil_image = Image.fromarray(cv2.resize(image_rgb, (width, height)))
        self.photo = ImageTk.PhotoImage(image=pil_image)
        self.canvas.config(width=width, height=height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        self.canvas.image = self.photo

    # Function to handle mouse clicks on the canvas
    def on_canvas_click(self, event):
        if self.segmented_image is not None:
            x, y = event.x, event.y
            if 0 <= x < self.segmented_image.shape[1] and 0 <= y < self.segmented_image.shape[0]:
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
            mask = np.zeros_like(self.segmented_image)
            seed_point = (x, y)
            target_color = self.segmented_image[y, x]

            if np.array_equal(color, (255, 255, 255)):  # If eraser color is selected
                fill_color = target_color  # Keeping the original color for erasing
            else:
                fill_color = color

            self.fill_region(mask, seed_point, target_color, fill_color)
            self.undo_stack.append(self.segmented_image.copy())  # Saving the state before painting
            self.segmented_image = np.where(mask != 0, mask, self.segmented_image)
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
    def is_similar_color(self, color1, color2, tolerance=7):
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

    # Function to save the image
    def save_image(self):
        if self.segmented_image is not None and self.color is not None:
            save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
            if save_path:
                pdf_canvas = canvas.Canvas(save_path, pagesize=letter)
                    # Drawing company logo
                logo_path = "Images/logo.png"  
                pdf_canvas.drawImage(ImageReader(logo_path), 100, 700, width=100, height=50)
                    # drawing white color for a gap..
                pdf_canvas.setFillColorRGB(255, 255, 255)
                    # Drawing the painted image
                painted_image_pil = Image.fromarray(cv2.cvtColor(self.segmented_image, cv2.COLOR_BGR2RGB))
                painted_image_path = "painted_image.png"  
                painted_image_pil.save(painted_image_path)  
                pdf_canvas.drawImage(ImageReader(painted_image_path), 100, 400, width=400, height=300)
                    # Deleting the temporary image
                os.remove(painted_image_path)

                # Drawing color box and code
                color_rgb = tuple(int(self.color[i:i+2], 16) for i in (1, 3, 5))
                pdf_canvas.setFillColorRGB(*color_rgb)
                pdf_canvas.rect(100, 100, 50, 50, fill=1)
                pdf_canvas.setFont("Helvetica", 12)
                pdf_canvas.drawString(170, 120, f"Color Code: {self.color}")

                pdf_canvas.save()

# Main function
if __name__ == "__main__":
    root = tk.Tk()
    app = HousePainterApp(root)
    root.mainloop()