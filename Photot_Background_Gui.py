import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from Add_Background import *
from tkinter import ttk
import time
def main_process_images(input_folder, output_folder, background, watermark_path, new_width, new_height):
    log_text.insert(tk.END, f"Input Folder: {input_folder}\n")
    log_text.insert(tk.END, f"Output Folder: {output_folder}\n")
    log_text.insert(tk.END, f"Background Type: {background}\n")
    log_text.insert(tk.END, f"Watermark Path: {watermark_path}\n")
    log_text.insert(tk.END, f"New Width: {new_width}\n")
    log_text.insert(tk.END, f"New Height: {new_height}\n")
    star_time=time.time()
    process_images(input_folder, output_folder,background=background,watermark_path=watermark_path,new_width=new_width,new_height=new_height,root=root,process_bar=progress_bar)
    log_text.insert(tk.END, f"time cost:{time.time()-star_time}\n")
    log_text.insert(tk.END, "Processing finished.\n")
def choose_input_folder():
    folder_selected = filedialog.askdirectory()
    input_folder_entry.delete(0, tk.END)
    input_folder_entry.insert(0, folder_selected)

def choose_output_folder():
    folder_selected = filedialog.askdirectory()
    output_folder_entry.delete(0, tk.END)
    output_folder_entry.insert(0, folder_selected)

def choose_watermark():
    file_selected = filedialog.askopenfilename()
    watermark_entry.delete(0, tk.END)
    watermark_entry.insert(0, file_selected)

def submit():
    input_folder = input_folder_entry.get()
    output_folder = output_folder_entry.get()
    watermark_path = watermark_entry.get()
    new_width = int(width_entry.get())
    new_height = int(height_entry.get())
    background_type = background_var.get()

    if not input_folder or not output_folder:
        messagebox.showerror("Error", "Input and Output folders are required.")
        return

    log_text.delete(1.0, tk.END)
    progress_bar['value'] = 0

    main_process_images(input_folder, output_folder, background_type, watermark_path, new_width, new_height)


root = tk.Tk()
root.title("Image Processing Tool")


input_folder_label = tk.Label(root, text="Input Folder:")
input_folder_label.pack()
input_folder_entry = tk.Entry(root, width=50)
input_folder_entry.pack()
input_folder_button = tk.Button(root, text="Browse", command=choose_input_folder)
input_folder_button.pack()


output_folder_label = tk.Label(root, text="Output Folder:")
output_folder_label.pack()
output_folder_entry = tk.Entry(root, width=50)
output_folder_entry.pack()
output_folder_button = tk.Button(root, text="Browse", command=choose_output_folder)
output_folder_button.pack()


watermark_label = tk.Label(root, text="Watermark Path:")
watermark_label.pack()
watermark_entry = tk.Entry(root, width=50)
watermark_entry.pack()
watermark_button = tk.Button(root, text="Browse", command=choose_watermark)
watermark_button.pack()


width_label = tk.Label(root, text="New Width:")
width_label.pack()
width_entry = tk.Entry(root, width=50)
width_entry.insert(0, "6000") 
width_entry.pack()


height_label = tk.Label(root, text="New Height:")
height_label.pack()
height_entry = tk.Entry(root, width=50)
height_entry.insert(0, "6000") 
height_entry.pack()


background_label = tk.Label(root, text="Background Type:")
background_label.pack()
background_var = tk.StringVar()
background_var.set("1")
background_option_menu = tk.OptionMenu(root, background_var, "1", "2", "3", "4")
background_option_menu.pack()


log_text = tk.Text(root, height=10, width=50)
log_text.pack()
log_text.insert(tk.END, "Background Type:\n1.dominant_color\n2.dominant_color_circle\n3.blured\n4.white\n")

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack()

submit_button = tk.Button(root, text="Submit", command=submit)
submit_button.pack()


root.mainloop()
