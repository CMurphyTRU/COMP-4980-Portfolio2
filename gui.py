
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk
from threading import Thread
from queue import Queue, Empty
import random
import time
import math

from main import generate_fractal
from randomizer import randomize_settings


class FractalGUI:
    def __init__(self, root):
        self.root = root
        root.title("Fractal Art Generator")
        root.geometry("1200x800")
        root.minsize(850, 550)

        self.image = self.preview = self.settings = None
        self.busy = False
        self.results = Queue()

        defaults = {
            "fractal_type": "mandelbrot", "palette": "rainbow",
            "width": 800, "height": 600, "iterations": 300,
            "zoom": 1.0, "center_x": -0.75, "center_y": 0.0,
            "julia_real": -0.7, "julia_imag": 0.27015,
            "seed": "", "randomize": False
        }
        self.vars = {
            k: (tk.BooleanVar if isinstance(v, bool) else
                tk.IntVar if isinstance(v, int) else
                tk.DoubleVar if isinstance(v, float) else tk.StringVar)(value=v)
            for k, v in defaults.items()
        }

        self.build_gui()
        self.root.after(50, self.check_results)

    def build_gui(self):
        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main, padding=10)
        left.pack(side="left", fill="both", expand=True)

        ttk.Label(left, text="Fractal Preview",
                  font=("Arial", 16, "bold")).pack(pady=10)

        self.preview_area = ttk.Frame(left)
        self.preview_area.pack(fill="both", expand=True)

        self.preview_label = ttk.Label(
            self.preview_area, text="Generate a fractal to preview it."
        )
        self.preview_label.place(relx=0.5, rely=0.5, anchor="center")

        # Scrollable settings panel.
        right = ttk.Frame(main, width=350)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        canvas = tk.Canvas(right, highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        controls = ttk.Frame(canvas, padding=15)
        window = canvas.create_window((0, 0), window=controls, anchor="nw")

        controls.bind("<Configure>", lambda e:
                      canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e:
                    canvas.itemconfigure(window, width=e.width))
        canvas.bind("<MouseWheel>", lambda e:
                    canvas.yview_scroll(-int(e.delta / 120), "units"))

        def heading(text):
            ttk.Label(controls, text=text,
                      font=("Arial", 12, "bold")).pack(anchor="w", pady=10)

        def field(label, key, options=None):
            ttk.Label(controls, text=label).pack(anchor="w")
            if options:
                widget = ttk.Combobox(
                    controls, textvariable=self.vars[key],
                    values=options, state="readonly"
                )
            else:
                widget = ttk.Entry(controls, textvariable=self.vars[key])
            widget.pack(fill="x", pady=(0, 8))

        heading("Fractal Settings")
        field("Fractal Type", "fractal_type", ["mandelbrot", "julia"])
        field("Color Palette", "palette",
              ["rainbow", "fire", "ocean", "grayscale"])
        field("Image Width", "width")
        field("Image Height", "height")
        field("Maximum Iterations", "iterations")

        heading("Position and Magnification")
        for label, key in [
            ("Zoom", "zoom"),
            ("Center X", "center_x"),
            ("Center Y", "center_y")
        ]:
            field(label, key)

        heading("Julia Settings")
        field("Julia Constant (Real)", "julia_real")
        field("Julia Constant (Imaginary)", "julia_imag")

        heading("Randomization")
        ttk.Checkbutton(
            controls, text="Randomize Settings",
            variable=self.vars["randomize"]
        ).pack(anchor="w", pady=5)
        field("Random Seed (optional)", "seed")

        self.button = ttk.Button(
            controls, text="Generate Fractal", command=self.generate
        )
        self.button.pack(fill="x", pady=5)

        ttk.Button(
            controls, text="Save Image", command=self.save
        ).pack(fill="x", pady=5)

        self.status = ttk.Label(controls, text="Ready")
        self.status.pack(pady=10)

        heading("Generated Settings")
        self.info = tk.Text(
            controls, height=11, width=35,
            font=("Consolas", 9), state="disabled"
        )
        self.info.pack(fill="x")

    def generate(self):
        if self.busy:
            return

        try:
            v = {k: x.get() for k, x in self.vars.items()}
            width, height, iterations = (
                v["width"], v["height"], v["iterations"]
            )

            if min(width, height, iterations) <= 0:
                raise ValueError("Dimensions and iterations must be positive.")

            if not math.isfinite(v["zoom"]) or v["zoom"] <= 0:
                raise ValueError("Zoom must be positive and finite.")

            settings = {
                "fractal_type": v["fractal_type"],
                "palette": v["palette"],
                "zoom": v["zoom"],
                "center_x": v["center_x"],
                "center_y": v["center_y"],
                "julia_c": complex(v["julia_real"], v["julia_imag"])
            }

            seed = None
            if v["randomize"]:
                seed = (int(v["seed"]) if v["seed"].strip()
                        else random.SystemRandom().randrange(2**32))
                settings = randomize_settings(seed)

            self.settings = settings.copy()

            # Show randomized parameters in the editable fields.
            for key in ("fractal_type", "palette", "zoom",
                        "center_x", "center_y"):
                self.vars[key].set(settings[key])

            if settings["julia_c"] is not None:
                self.vars["julia_real"].set(settings["julia_c"].real)
                self.vars["julia_imag"].set(settings["julia_c"].imag)

        except (ValueError, tk.TclError) as error:
            messagebox.showerror("Invalid Settings", str(error))
            return

        self.busy = True
        self.button.config(state="disabled")
        self.status.config(text="Generating...")

        # Generate outside the GUI thread.
        def worker():
            try:
                start = time.perf_counter()
                image = generate_fractal(
                    settings["fractal_type"], settings["center_x"],
                    settings["center_y"], settings["zoom"],
                    settings["palette"], settings["julia_c"], None,
                    width=width, height=height, max_iterations=iterations
                )
                self.results.put(("success", image,
                                  time.perf_counter() - start,
                                  settings, seed, width, height, iterations))
            except Exception as error:
                self.results.put(("error", str(error)))

        Thread(target=worker, daemon=True).start()

    def check_results(self):
        try:
            while True:
                result = self.results.get_nowait()

                if result[0] == "error":
                    self.status.config(text="Generation failed")
                    messagebox.showerror("Generation Error", result[1])
                else:
                    _, self.image, elapsed, s, seed, w, h, it = result

                    preview = self.image.copy()
                    preview.thumbnail((
                        max(100, self.preview_area.winfo_width() - 20),
                        max(100, self.preview_area.winfo_height() - 20)
                    ))

                    self.preview = ImageTk.PhotoImage(preview)
                    self.preview_label.config(image=self.preview, text="")

                    information = (
                        f"Type: {s['fractal_type']}\n"
                        f"Palette: {s['palette']}\n"
                        f"Zoom: {s['zoom']:.6f}\n"
                        f"Center X: {s['center_x']:.12f}\n"
                        f"Center Y: {s['center_y']:.12f}\n"
                        f"Julia Constant: {s['julia_c']}\n"
                        f"Seed: {seed}\n"
                        f"Resolution: {w}x{h}\n"
                        f"Iterations: {it}"
                    )
                    self.info.config(state="normal")
                    self.info.delete("1.0", tk.END)
                    self.info.insert("1.0", information)
                    self.info.config(state="disabled")
                    self.status.config(text=f"Generated in {elapsed:.2f}s")

                self.busy = False
                self.button.config(state="normal")

        except Empty:
            pass

        self.root.after(50, self.check_results)

    def save(self):
        if self.image is None:
            messagebox.showinfo("No Image", "Generate a fractal first.")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Images", "*.png")]
        )
        if path:
            self.image.save(path)


if __name__ == "__main__":
    root = tk.Tk()
    FractalGUI(root)
    root.mainloop()
