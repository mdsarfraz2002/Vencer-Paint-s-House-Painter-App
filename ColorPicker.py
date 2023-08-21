'''Color Picker GUI for the app using Tkinter'''

# Importing the required libraries
import tkinter as tk
import pandas as pd
from tkinter import Scrollbar

# Creating the class for the color picker
class ColorPicker:
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback

        self.color_picker_window = tk.Toplevel(self.parent)
        self.color_picker_window.title("Color Picker")
        self.color_picker_window.geometry("900x600")  # Seting window dimensions

        # Choosing Color label
        self.choose_color_label = tk.Label(self.color_picker_window, text="Enter color code or name:")
        self.choose_color_label.pack(anchor=tk.NW, padx=20, pady=10)

        # Extracting unique brand and category values for filter options
        self.color_data = pd.read_excel("Color code vencer paints.xlsx")
        self.unique_brands = ["All Brands"] + self.color_data["brand_id"].unique().tolist()
        self.unique_categories = ["All Categories"] + self.color_data["color_category_id"].unique().tolist()

        # Creating a frame for the top row
        top_row_frame = tk.Frame(self.color_picker_window)
        top_row_frame.pack(padx=20, pady=(0, 10), fill=tk.X)

        # Searching entry and button
        self.search_entry = tk.Entry(top_row_frame)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 10))

        self.search_button = tk.Button(top_row_frame, text="Search", command=self.search_color)
        self.search_button.pack(side=tk.LEFT)

        # Brand filter
        self.brand_filter_var = tk.StringVar()
        self.brand_filter_var.set("All Brands")
        self.brand_filter = tk.OptionMenu(top_row_frame, self.brand_filter_var, *self.unique_brands)
        self.brand_filter.pack(side=tk.LEFT, padx=(10, 0))

        # Category filter
        self.category_filter_var = tk.StringVar()
        self.category_filter_var.set("All Categories")
        self.category_filter = tk.OptionMenu(top_row_frame, self.category_filter_var, *self.unique_categories)
        self.category_filter.pack(side=tk.LEFT)

        # Creating a frame for color display
        self.color_display_frame = tk.Frame(self.color_picker_window, bg="white")
        self.color_display_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

        # Scrollbar for color display frame
        self.scrollbar = Scrollbar(self.color_display_frame, orient="vertical")
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.color_display_canvas = tk.Canvas(self.color_display_frame, yscrollcommand=self.scrollbar.set, bg="white")
        self.color_display_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.color_display_canvas.yview)

        self.color_display_inner_frame = tk.Frame(self.color_display_canvas, bg="white")
        self.color_display_canvas.create_window((0, 0), window=self.color_display_inner_frame, anchor="nw")

        self.color_display_inner_frame.bind("<Configure>", self.on_frame_configure)
        self.color_display_inner_frame.bind("<Enter>", lambda event: self.color_display_canvas.bind_all("<MouseWheel>", lambda event: self.color_display_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")))

        self.search_entry.bind("<Return>", lambda event: self.search_color())

        self.update_color_display()
        self.search_color()

    # Function to configure the frame
    def on_frame_configure(self, event):
        self.color_display_canvas.configure(scrollregion=self.color_display_canvas.bbox("all"))

    # Function to search for the color
    def search_color(self):
        search_term = self.search_entry.get()
        filtered_data = self.color_data[
            (self.color_data["hex_code"].str.contains(search_term, case=False)) |
            (self.color_data["Name"].str.contains(search_term, case=False)) |
            (self.color_data["color_code"].str.contains(search_term, case=False))
        ]
        self.filtered_color_data = filtered_data
        self.update_color_display()

    # Function to update the color display
    def update_color_display(self):
        for widget in self.color_display_inner_frame.winfo_children():
            widget.destroy()

        if hasattr(self, "filtered_color_data"):
            colors_per_row = 3
            row_spacing = 80  
            color_box_padding = 20  
            color_info_padding = 10  
            row_index = 0
            column_index = 0
            total_items = len(self.filtered_color_data)

            for index, row in self.filtered_color_data.iterrows():
                color_box = tk.Frame(self.color_display_inner_frame, width=50, height=50, bg=row["hex_code"])
                color_box.grid(row=row_index, column=column_index, padx=color_box_padding, pady=color_box_padding)
                color_box.bind("<Button-1>", lambda event, color=row["hex_code"]: self.color_selected(color))

                color_info = tk.Label(self.color_display_inner_frame, text=f"{row['Name']} - {row['hex_code']} - {row['color_code']}")
                color_info.grid(row=row_index + 1, column=column_index, padx=color_info_padding, pady=color_info_padding)

                column_index += 1
                if column_index == colors_per_row:
                    row_index += 2  # Moving to the next row
                    column_index = 0

            # Adding a separator at the end of the last row if it's a complete row
            if total_items % colors_per_row == 0:
                row_separator = tk.Frame(self.color_display_inner_frame, height=row_spacing)
                row_separator.grid(row=row_index, column=0, columnspan=colors_per_row)

    # Function to selected the color
    def color_selected(self, color):
        self.color = color
        self.callback(self.color)
        self.color_picker_window.destroy()

# Main function
if __name__ == "__main__":
    def color_callback(selected_color):
        print(f"Selected color: {selected_color}")

    root = tk.Tk()
    app = ColorPicker(root, color_callback)
    root.mainloop()