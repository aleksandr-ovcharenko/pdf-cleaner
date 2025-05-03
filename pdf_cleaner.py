import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import io

class PDFCleaner:
    def __init__(self, master):
        self.master = master
        self.master.title("PDF Cleaner - Зональный выбор")
        self.canvas = tk.Canvas(master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.menu = tk.Menu(master)
        master.config(menu=self.menu)
        self.menu.add_command(label="Открыть PDF", command=self.load_pdf)
        self.menu.add_command(label="Сохранить зоны", command=self.save_zones)

        self.zones = []
        self.current_rect = None
        self.rect_start = None

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.page_image = None
        self.tk_img = None
        self.scale = 1.0

    def load_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if not filepath:
            return

        self.doc = fitz.open(filepath)
        page = self.doc.load_page(0)
        pix = page.get_pixmap(dpi=150)
        img_data = Image.open(io.BytesIO(pix.tobytes("png")))
        self.page_image = img_data
        self.tk_img = ImageTk.PhotoImage(self.page_image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_img)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def on_press(self, event):
        self.rect_start = (event.x, event.y)
        self.current_rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red")

    def on_drag(self, event):
        if self.current_rect:
            self.canvas.coords(self.current_rect, self.rect_start[0], self.rect_start[1], event.x, event.y)

    def on_release(self, event):
        x0, y0, x1, y1 = self.canvas.coords(self.current_rect)
        zone_type = self.ask_zone_type()
        self.zones.append({"rect": (x0, y0, x1, y1), "type": zone_type})

    def ask_zone_type(self):
        popup = tk.Toplevel()
        popup.title("Тип зоны")
        var = tk.StringVar(value="static")

        tk.Label(popup, text="Выберите тип зоны:").pack()
        tk.Radiobutton(popup, text="Статическая (всегда удалять)", variable=var, value="static").pack(anchor="w")
        tk.Radiobutton(popup, text="Динамическая (по признаку)", variable=var, value="dynamic").pack(anchor="w")
        tk.Button(popup, text="OK", command=popup.destroy).pack()
        popup.wait_window()

        return var.get()

    def save_zones(self):
        print("Выделенные зоны:")
        for zone in self.zones:
            print(zone)
        # Здесь можно сохранить конфигурацию или применить фильтрацию

if __name__ == '__main__':
    root = tk.Tk()
    app = PDFCleaner(root)
    root.mainloop()
