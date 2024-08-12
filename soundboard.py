import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel, Listbox, Scrollbar
import pygame
import os

# Initialize pygame mixer globally for use in the play_sound function
pygame.mixer.init()

def play_sound(sound_path):
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()

def create_button(root, sound_name, sound_path, row, column):
    button = tk.Button(root, text=sound_name, command=lambda: play_sound(sound_path))
    button.grid(row=row, column=column, padx=5, pady=5, sticky='ew')

def load_sounds_from_directory(directory, root):
    for widget in root.winfo_children():
        widget.destroy()  # Clear existing widgets
    
    row = 0
    column = 0
    max_columns = 4  # Number of columns in your grid

    for filename in os.listdir(directory):
        if filename.endswith(".mp3"):
            sound_path = os.path.join(directory, filename)
            sound_name = os.path.splitext(filename)[0]
            create_button(root, sound_name, sound_path, row, column)
            column += 1
            if column >= max_columns:
                column = 0
                row += 1

def choose_folder(root):
    folder_path = filedialog.askdirectory()
    print(f"Selected folder path: {folder_path}")  # Debug print
    if folder_path:
        load_sounds_from_directory(folder_path, root)

def main():
    root = tk.Tk()
    root.title("Soundboard")
    root.geometry("1200x520")

    # Frame for sound buttons
    sound_frame = tk.Frame(root)
    sound_frame.grid(row=0, column=0, sticky='nsew')

    # Button to choose folder
    choose_folder_button = tk.Button(root, text="Choose Folder", command=lambda: choose_folder(root))
    choose_folder_button.grid(row=0, column=0, pady=10, padx=10)

    # Configure grid row and column weights to ensure proper placement
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(1, weight=0)

    root.mainloop()

if __name__ == "__main__":
    main()
