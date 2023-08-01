import os
import ffmpeg
import subprocess
import tkinter as tk
from tkinter import filedialog

# Set the path to your FFmpeg executable
ffmpeg_path = 'ffmpeg/bin/ffmpeg.exe'

# Function to process the files
def process_files():
    input_folder = input_folder_var.get()
    output_folder = output_folder_var.get()

    # Ensure that the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # List all files in the input folder
    input_files = os.listdir(input_folder)
    # Count the total number of .mkv files
    total_files = sum(1 for file in input_files if file.lower().endswith('.mkv'))

    # Update the status label to display the current file being processed and progress
    current_file_label.config(text="Processing: 0 / {}".format(total_files))
    root.update()

    # Process each file in the input folder
    completed_files = 0
    # Update the status label to display the current file being processed
    for file in input_files:
        if file.lower().endswith('.mkv'):
            current_file_label.config(text="Processing: {} / {}\nFile: {}".format(completed_files, total_files, file))
            root.update()

            input_file = os.path.join(input_folder, file)
            output_file = os.path.join(output_folder, os.path.splitext(file)[0] + '.mp4')
            
            # Check if the file has at least two audio tracks
            probe = ffmpeg.probe(input_file)
            audio_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'audio']
            if len(audio_streams) < 2:
                print(f"Skipping {input_file}: File doesn't have exactly two audio tracks (stereo).")
                completed_files += 1
                continue
                
            # Define the input stream for the current input file
            input_stream = ffmpeg.input(input_file)

            # Change the mapping to put track 1 into left channel and track 2 into right channel
            filter_complex = '[0:a:0][0:a:1]amerge=inputs=2,pan=stereo|c0<c0+c1|c1<c2+c3'

            # Define the output stream with the filter_complex and other options
            output_stream = ffmpeg.output(input_stream, output_file, filter_complex=filter_complex, **{'c:v': 'copy'})

            # Run the FFmpeg command and display progress
            ffmpeg.run(output_stream, cmd=ffmpeg_path, overwrite_output=True)
            
            completed_files += 1
    # Show a message box when processing is done
    current_file_label.config(text="Processing: Complete")
    root.update()
    tk.messagebox.showinfo("Processing Complete", "Audio channels mapping is done!")

# Function to select the input folder
def select_input_folder():
    folder = filedialog.askdirectory()
    input_folder_var.set(folder)

# Function to select the output folder
def select_output_folder():
    folder = filedialog.askdirectory()
    output_folder_var.set(folder)

# Main GUI window
root = tk.Tk()
root.title("KJB 2TRACK Audio Channels Mapping")

# Set the window size
root.geometry("600x200")

# Variables to store the selected folders
input_folder_var = tk.StringVar()
output_folder_var = tk.StringVar()

# Label and Entry for selecting input folder
input_label = tk.Label(root, text="Select Input Folder:")
input_label.grid(row=0, column=0, padx=10, pady=5)
input_entry = tk.Entry(root, textvariable=input_folder_var, width=50)
input_entry.grid(row=0, column=1, padx=10, pady=5)
input_button = tk.Button(root, text="Browse", command=select_input_folder)
input_button.grid(row=0, column=2, padx=10, pady=5)

# Label and Entry for selecting output folder
output_label = tk.Label(root, text="Select Output Folder:")
output_label.grid(row=1, column=0, padx=10, pady=5)
output_entry = tk.Entry(root, textvariable=output_folder_var, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=5)
output_button = tk.Button(root, text="Browse", command=select_output_folder)
output_button.grid(row=1, column=2, padx=10, pady=5)

# Label to display the current file being processed
current_file_label = tk.Label(root, text="", wraplength=500)
current_file_label.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

# Button to start processing
process_button = tk.Button(root, text="Start Processing", command=process_files)
process_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# Run the GUI main loop
root.mainloop()
