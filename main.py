import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os


class RasterizationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Zaawansowana rasteryzacja obrazu")

        self.image_path = None
        self.image = None
        self.tk_image = None
        self.last_dimension = None
        self.last_num_sheets = None

        self.create_widgets()

    def create_widgets(self):
        # Przyciski sterujące
        control_frame = tk.Frame(self.root)
        control_frame.pack(pady=10)

        self.load_button = tk.Button(control_frame, text="Wczytaj obraz", command=self.load_image)
        self.load_button.pack(side=tk.LEFT, padx=5)

        # Pole do wprowadzania liczby arkuszy
        self.sheet_label = tk.Label(control_frame, text="Liczba arkuszy:")
        self.sheet_label.pack(side=tk.LEFT, padx=5)

        self.sheet_entry = tk.Entry(control_frame, width=5)
        self.sheet_entry.pack(side=tk.LEFT, padx=5)

        # Przyciski podglądu
        self.preview_width_btn = tk.Button(control_frame, text="Podgląd pionowe",
                                           command=lambda: self.preview_lines("width"))
        self.preview_width_btn.pack(side=tk.LEFT, padx=5)

        self.preview_height_btn = tk.Button(control_frame, text="Podgląd poziome",
                                            command=lambda: self.preview_lines("height"))
        self.preview_height_btn.pack(side=tk.LEFT, padx=5)

        # Przycisk zapisu
        self.save_btn = tk.Button(control_frame, text="Zapisz arkusze", command=self.save_image)
        self.save_btn.pack(side=tk.LEFT, padx=5)

        # Canvas z przewijaniem
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.h_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.v_scroll = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

        self.h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
        if self.image_path:
            self.image = Image.open(self.image_path)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))
            self.clear_lines()

    def preview_lines(self, dimension):
        if self.image is None:
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz!")
            return

        try:
            num_sheets = int(self.sheet_entry.get())
            if num_sheets <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Błąd", "Podaj poprawną liczbę arkuszy (większą od 0)!")
            return

        self.clear_lines()
        self.last_dimension = dimension
        self.last_num_sheets = num_sheets

        width, height = self.image.size
        line_color = "red"

        if dimension == "width":
            step = width / num_sheets
            for i in range(1, num_sheets):
                x = i * step
                self.canvas.create_line(x, 0, x, height, fill=line_color, tags="line")
        elif dimension == "height":
            step = height / num_sheets
            for i in range(1, num_sheets):
                y = i * step
                self.canvas.create_line(0, y, width, y, fill=line_color, tags="line")

    def clear_lines(self):
        self.canvas.delete("line")

    def save_image(self):
        if not all([self.image, self.last_dimension, self.last_num_sheets]):
            messagebox.showerror("Błąd", "Najpierw wczytaj obraz i wykonaj podgląd!")
            return

        save_dir = filedialog.askdirectory()
        if not save_dir:
            return

        try:
            width, height = self.image.size
            base_name = os.path.splitext(os.path.basename(self.image_path))[0]

            if self.last_dimension == "width":
                step = width / self.last_num_sheets
                for i in range(self.last_num_sheets):
                    left = int(i * step)
                    right = int((i + 1) * step)
                    cropped = self.image.crop((left, 0, right, height))
                    cropped.save(os.path.join(save_dir, f"{base_name}_part_{i + 1}.png"))

            elif self.last_dimension == "height":
                step = height / self.last_num_sheets
                for i in range(self.last_num_sheets):
                    top = int(i * step)
                    bottom = int((i + 1) * step)
                    cropped = self.image.crop((0, top, width, bottom))
                    cropped.save(os.path.join(save_dir, f"{base_name}_part_{i + 1}.png"))

            messagebox.showinfo("Sukces", f"Zapisano {self.last_num_sheets} arkuszy w:\n{save_dir}")
        except Exception as e:
            messagebox.showerror("Błąd", f"Błąd podczas zapisywania: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = RasterizationApp(root)
    root.mainloop()