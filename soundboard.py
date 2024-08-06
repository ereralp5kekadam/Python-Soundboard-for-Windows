import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import pygame
import os
import sounddevice as sd
import numpy as np
import threading

# Parameters
SAMPLE_RATE = 44100  # Sample rate in Hz
AMPLIFICATION_FACTOR = 10.0  # Factor by which to amplify the audio (adjusted for practicality)

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

def choose_folder_and_mic(root):
    folder_path = filedialog.askdirectory()
    if folder_path:
        load_sounds_from_directory(folder_path, root)
        
        # Add the empty button after loading sounds
        empty_button = tk.Button(root, text="Choose Microphone", command=lambda: choose_microphone(root))
        empty_button.grid(row=10, column=12, padx=10, pady=12, sticky='se')

def list_microphones():
    devices = sd.query_devices()
    mic_devices = [device for device in devices if device['max_input_channels'] > 0]
    return mic_devices

def choose_microphone(root):
    mic_devices = list_microphones()
    if not mic_devices:
        messagebox.showinfo("No Microphones", "No microphone devices found.")
        return

    mic_names = [device['name'] for device in mic_devices]
    mic_names.append("Cancel")  # Add an option to cancel

    selected_mic = simpledialog.askstring("Select Microphone", "Available Microphones:\n" + "\n".join(mic_names))
    if selected_mic == "Cancel" or selected_mic not in mic_names:
        return
    
    selected_index = mic_names.index(selected_mic)
    if selected_index < len(mic_devices):
        mic_device = mic_devices[selected_index]
        start_audio_stream(mic_device['name'])
        messagebox.showinfo("Microphone Selected", f"Selected Microphone: {mic_device['name']}")
    else:
        messagebox.showinfo("Action Cancelled", "Microphone selection was canceled.")

def audio_callback(indata, frames, time, status):
    if status:
        print(f"Status: {status}")

    # Amplify the audio data
    amplified_data = indata * AMPLIFICATION_FACTOR
    
    # Ensure values are within the valid range [-1.0, 1.0] to prevent distortion
    amplified_data = np.clip(amplified_data, -1.0, 1.0)
    
    # Print statistics about the audio data
    min_amplitude = np.min(amplified_data)
    max_amplitude = np.max(amplified_data)
    avg_amplitude = np.mean(np.abs(amplified_data))
    
    print(f"Min Amplitude: {min_amplitude:.5f}")
    print(f"Max Amplitude: {max_amplitude:.5f}")
    print(f"Average Amplitude: {avg_amplitude:.5f}")

    # Output the amplified audio
    sd.play(amplified_data, samplerate=SAMPLE_RATE)

def start_audio_stream(mic_name):
    def audio_thread():
        # Find the device index by name
        device_index = None
        devices = sd.query_devices()
        for index, device in enumerate(devices):
            if device['name'] == mic_name:
                device_index = index
                break

        if device_index is not None:
            try:
                with sd.InputStream(device=device_index, channels=1, samplerate=SAMPLE_RATE, callback=audio_callback):
                    print("Audio stream started")
                    sd.sleep(-1)  # Keep the stream open indefinitely
            except Exception as e:
                print(f"Error starting audio stream: {e}")
        else:
            messagebox.showerror("Error", f"Microphone '{mic_name}' not found.")

    threading.Thread(target=audio_thread, daemon=True).start()

def main():
    root = tk.Tk()
    root.title("Soundboard")
    root.geometry("1200x500")

    # Frame for sound buttons
    sound_frame = tk.Frame(root)
    sound_frame.grid(row=0, column=0, sticky='nsew')

    # Button to choose folder
    choose_folder_and_mic_button = tk.Button(root, text="Choose Folder", command=lambda: choose_folder_and_mic(root))
    choose_folder_and_mic_button.grid(row=0, column=0, pady=10)

    # Configure grid row and column weights to ensure proper placement
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=0)
    root.grid_columnconfigure(1, weight=0)

    root.mainloop()

if __name__ == "__main__":
    main()
