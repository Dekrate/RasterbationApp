import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import os

# Standard A4 size in pixels at 300 DPI
A4_WIDTH = 2480
A4_HEIGHT = 3508

class RasterbationApp:
    def __init__(self, app_root):
        self.root = app_root
        self.root.title("Rasterbation Tool")

        self.image_path = None
        self.image = None
        self.preview_image = None
        self.draw = None

        self.label = tk.Label(root, text="Wybierz obraz do rasteryzacji")
        self.label.pack(pady=10)

        self.load_button = tk.Button(root, text="Wybierz obraz", command=self.load_image)
        self.load_button.pack(pady=5)

        self.format_label = tk.Label(root, text="Format docelowy (np. PNG, JPEG):")
        self.format_label.pack(pady=5)

        self.format_entry = tk.Entry(root)
        self.format_entry.insert(0, "PNG")
        self.format_entry.pack(pady=5)

        self.horizontal_label = tk.Label(root, text="Liczba kartek w poziomie:")
        self.horizontal_label.pack(pady=5)

        self.horizontal_entry = tk.Entry(root)
        self.horizontal_entry.insert(0, "1")
        self.horizontal_entry.pack(pady=5)

        self.vertical_label = tk.Label(root, text="Liczba kartek w pionie:")
        self.vertical_label.pack(pady=5)

        self.vertical_entry = tk.Entry(root)
        self.vertical_entry.insert(0, "1")
        self.vertical_entry.pack(pady=5)

        self.cut_mode_label = tk.Label(root, text="Tryb cięcia:")
        self.cut_mode_label.pack(pady=5)

        self.cut_mode = tk.StringVar(value="both")
        self.cut_both = tk.Radiobutton(root, text="Pion i poziom", variable=self.cut_mode, value="both")
        self.cut_both.pack()
        self.cut_horizontal = tk.Radiobutton(root, text="Tylko poziomy", variable=self.cut_mode, value="horizontal")
        self.cut_horizontal.pack()
        self.cut_vertical = tk.Radiobutton(root, text="Tylko pionowe", variable=self.cut_mode, value="vertical")
        self.cut_vertical.pack()

        self.preview_label = tk.Label(root, text="Podgląd:")
        self.preview_label.pack(pady=10)

        self.preview_canvas = tk.Canvas(root, width=300, height=300)
        self.preview_canvas.pack(pady=10)

        self.generate_button = tk.Button(root, text="Generuj rasteryzację", command=self.generate_rasterbation)
        self.generate_button.pack(pady=20)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp;*.gif")])
        if self.image_path:
            self.image = Image.open(self.image_path)
            self.update_preview()

    def update_preview(self):
        if self.image:
            preview_size = (300, 300)
            resized_image = self.image.copy()
            resized_image.thumbnail(preview_size)

            draw = ImageDraw.Draw(resized_image)
            width, height = resized_image.size

            try:
                horizontal = int(self.horizontal_entry.get())
                vertical = int(self.vertical_entry.get())

                if horizontal > 1:
                    for i in range(1, horizontal):
                        x = width * i // horizontal
                        draw.line((x, 0, x, height), fill="red", width=1)

                if vertical > 1:
                    for j in range(1, vertical):
                        y = height * j // vertical
                        draw.line((0, y, width, y), fill="red", width=1)
            except ValueError:
                pass

            self.preview_image = ImageTk.PhotoImage(resized_image)
            self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_image)

    def generate_rasterbation(self):
        if not self.image:
            messagebox.showerror("Błąd", "Nie wybrano obrazu!")
            return

        try:
            horizontal = int(self.horizontal_entry.get())
            vertical = int(self.vertical_entry.get())
            target_format = self.format_entry.get().strip().upper()
            cut_mode = self.cut_mode.get()

            if horizontal <= 0 or vertical <= 0:
                messagebox.showerror("Błąd", "Liczba kartek musi być większa niż 0!")
                return

            width, height = self.image.size
            tile_width = width // horizontal if cut_mode in ["both", "horizontal"] else width
            tile_height = height // vertical if cut_mode in ["both", "vertical"] else height

            output_dir = "rasterbation_output"
            os.makedirs(output_dir, exist_ok=True)

            for i in range(horizontal if cut_mode in ["both", "horizontal"] else 1):
                for j in range(vertical if cut_mode in ["both", "vertical"] else 1):
                    left = i * tile_width
                    upper = j * tile_height
                    right = left + tile_width
                    lower = upper + tile_height

                    tile = self.image.crop((left, upper, right, lower))

                    a4_tile = tile.resize((A4_WIDTH, A4_HEIGHT))
                    a4_tile.save(f"{output_dir}/tile_{i}_{j}.{target_format.lower()}", format=target_format)

            messagebox.showinfo("Sukces", f"Rasteryzacja zakończona! Pliki zapisano w folderze '{output_dir}'.")
        except ValueError:
            messagebox.showerror("Błąd", "Nieprawidłowe wartości dla liczby kartek!")

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterbationApp(root)
    root.mainloop()