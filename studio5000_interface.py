import os
import tkinter as tk
from tkinter import filedialog, messagebox
from studio5000_main import convert

# Initialise and set the size of the window and its title
class StepConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FDS To Studio 5000 Steps")
        self.geometry("720x280")

# Define string variables for the input file path, output directory and sequence name, required for functionality
        self.var_input = tk.StringVar()
        self.var_outdir = tk.StringVar(value=os.path.abspath("output"))
        self.var_seq = tk.StringVar()

        self._build()

# Building of the window layout including buttons, labels and string entry fields
    def _build(self):
        pad = {"padx": 10, "pady": 6}

        tk.Label(self, text="FDS (.docx):").grid(row=0, column=0, sticky="w", **pad)
        tk.Entry(self, textvariable=self.var_input, width=70).grid(row=0, column=1, sticky="we", **pad)
        tk.Button(self, text="Browse...", command=self.browse_file).grid(row=0, column=2, **pad)

        tk.Label(self, text="Output folder:").grid(row=1, column=0, sticky="w", **pad)
        tk.Entry(self, textvariable=self.var_outdir, width=70).grid(row=1, column=1, sticky="we", **pad)
        tk.Button(self, text="Browse...", command=self.browse_output).grid(row=1, column=2, **pad)

        tk.Label(self, text="Sequence name:").grid(row=2, column=0, sticky="w", **pad)
        tk.Entry(self, textvariable=self.var_seq, width=25).grid(row=2, column=1, sticky="w", **pad)

        tk.Button(self, text="Convert", command=self.run).grid(row=3, column=1, sticky="w", **pad)

        self.txt = tk.Text(self, height=6, width=90)
        self.txt.grid(row=4, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(4, weight=1)

# Functionality for the file browsing feature, search for docx files
    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("Word Documents", "*.docx")])
        if path:
            self.var_input.set(path)

# Functionality for the output folder browsing feature, search for folders
    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.var_outdir.set(path)

# Main run function, check valid paths and sequence name, then run conversion and display result
    def run(self):
        inp = self.var_input.get().strip()
        outdir = self.var_outdir.get().strip()
        seq = self.var_seq.get().strip()

# Check for valid input file and valid sequence name with an error message if not valid
        if not inp or not os.path.exists(inp):
            messagebox.showerror("Missing input", "Please select a valid .docx file.")
            return

        if not seq:
            messagebox.showerror("Missing sequence name", "Please enter a sequence name.")
            return

# Run conversion and display the results including how many step records have been parsed
        try:
            output_file, n = convert(inp, outdir, seq)
            self.txt.delete("1.0", tk.END)
            self.txt.insert(tk.END, f"Parsed {n} step records.\n\n")
            self.txt.insert(tk.END, "Output file:\n")
            self.txt.insert(tk.END, f"  {output_file}\n")
            messagebox.showinfo("Done", "Conversion completed successfully.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    StepConverterApp().mainloop()
