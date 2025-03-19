import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import threading
import whisper
import sys
import os

def set_ffmpeg_path():
    """
    If ffmpeg.exe is bundled by PyInstaller, place its directory
    in the PATH so subprocess calls (like whisper) can find it.
    """
    if getattr(sys, 'frozen', False):
        # If we're in a PyInstaller bundle,
        # sys._MEIPASS is where files are extracted.
        exe_dir = sys._MEIPASS
    else:
        # If running in normal Python environment
        exe_dir = os.path.dirname(os.path.abspath(__file__))

    # ffmpeg.exe should be in the same folder as the bundled .exe
    ffmpeg_path = os.path.join(exe_dir, "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        # Prepend that folder to PATH
        os.environ["PATH"] = exe_dir + os.pathsep + os.environ["PATH"]
    else:
        # Fall back to system ffmpeg if not found
        print("Warning: ffmpeg.exe not found in bundle. Using system ffmpeg if available.")


class TranscriptionGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Whisper Video Transcriber by Will Kaufhold")

        # Whisper model to load (e.g. 'tiny', 'base', 'small', 'medium', 'large')
        self.model_name = "base"
        self.model = whisper.load_model(self.model_name)

        # Track file path
        self.input_file_path = tk.StringVar()

        # Checkboxes
        self.subtitles_check = tk.BooleanVar(value=True)   # Create SRT?
        self.timestamps_check = tk.BooleanVar(value=True)  # Include timestamps in TXT?

        # Build the GUI
        self.create_widgets()

    def create_widgets(self):
        # Frame for usage info
        info_frame = ttk.LabelFrame(self.root, text="How to Use")
        info_frame.pack(padx=10, pady=5, fill="x")
        info_label = ttk.Label(
            info_frame,
            text=(
                "1. Select a video or audio file.\n"
                "2. If it's a video, check 'Create SRT Subtitles' if you want subtitles.\n"
                "3. Check 'Include timestamps in TXT' if you want timestamps in the text file.\n"
                "4. Click 'Transcribe' to start.\n\n"
                "The program will save 'filename.txt' (and 'filename.srt' if applicable)\n"
                "in the same folder as your selected file."
            )
        )
        info_label.pack(padx=5, pady=5)

        # Frame for input file
        frame_input = ttk.LabelFrame(self.root, text="Select Video/Audio File")
        frame_input.pack(padx=10, pady=5, fill="x")

        ttk.Label(frame_input, text="Input File:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_input = ttk.Entry(frame_input, textvariable=self.input_file_path, width=50)
        entry_input.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        btn_browse_input = ttk.Button(frame_input, text="Browse...", command=self.browse_input_file)
        btn_browse_input.grid(row=0, column=2, padx=5, pady=5)

        # Frame for options (checkboxes)
        options_frame = ttk.LabelFrame(self.root, text="Transcription Options")
        options_frame.pack(padx=10, pady=5, fill="x")

        chk_subtitles = ttk.Checkbutton(
            options_frame,
            text="Create SRT Subtitles (for Video only)",
            variable=self.subtitles_check
        )
        chk_subtitles.pack(anchor="w", padx=5, pady=2)

        chk_timestamps = ttk.Checkbutton(
            options_frame,
            text="Include timestamps in TXT",
            variable=self.timestamps_check
        )
        chk_timestamps.pack(anchor="w", padx=5, pady=2)

        # Frame for action button + progress
        action_frame = ttk.Frame(self.root)
        action_frame.pack(padx=10, pady=10, fill="x")

        self.progress_bar = ttk.Progressbar(action_frame, orient="horizontal", mode="indeterminate")
        self.progress_bar.pack(side="left", expand=True, fill="x", padx=5)

        btn_transcribe = ttk.Button(action_frame, text="Transcribe", command=self.start_transcription)
        btn_transcribe.pack(side="right", padx=5)

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Video or Audio File",
            filetypes=[
                ("Video/Audio", "*.mp4 *.mov *.mkv *.avi *.mp3 *.wav *.flac *.aac *.m4a"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)

    def start_transcription(self):
        """
        Determine output paths based on the input file name and user settings, then start transcribing.
        """
        input_file = self.input_file_path.get().strip()

        if not input_file or not os.path.isfile(input_file):
            messagebox.showerror("Error", "Please select a valid input file.")
            return

        # Figure out if it's video or audio by extension
        video_exts = {".mp4", ".mov", ".mkv", ".avi"}
        audio_exts = {".mp3", ".wav", ".flac", ".aac", ".m4a"}

        # We'll derive base name from the input file
        base_name, extension = os.path.splitext(input_file)
        extension = extension.lower()

        # .txt file path
        output_txt_path = base_name + ".txt"

        # Decide if we create an .srt
        create_srt = self.subtitles_check.get() and extension in video_exts
        output_srt_path = base_name + ".srt" if create_srt else None

        # Start progress bar
        self.progress_bar.start(10)

        # Use a thread to avoid freezing the GUI
        thread = threading.Thread(
            target=self.transcribe_file,
            args=(input_file, output_txt_path, output_srt_path),
            daemon=True
        )
        thread.start()

    def transcribe_file(self, input_path, output_txt_path, output_srt_path):
        try:
            result = self.model.transcribe(input_path, language="en")
            segments = result["segments"]  # segment-level data

            # Check if user wants timestamps
            include_timestamps = self.timestamps_check.get()

            # Write the TXT file
            with open(output_txt_path, "w", encoding="utf-8") as f_txt:
                if include_timestamps:
                    # Segment-based with [start-end] prefix
                    for seg in segments:
                        start_sec = seg["start"]
                        end_sec = seg["end"]
                        text = seg["text"].strip()
                        f_txt.write(f"[{start_sec:.2f} - {end_sec:.2f}] {text}\n")
                else:
                    # Single block of text with no timestamps
                    # or you can combine segments if you want
                    # result["text"] is the entire transcription
                    f_txt.write(result["text"].strip() + "\n")

            # If we decided to create an SRT (video file + checkbox enabled)
            if output_srt_path:
                with open(output_srt_path, "w", encoding="utf-8") as f_srt:
                    for i, seg in enumerate(segments, start=1):
                        start_str = self.srt_time_format(seg["start"])
                        end_str = self.srt_time_format(seg["end"])
                        text = seg["text"].strip()

                        f_srt.write(f"{i}\n")
                        f_srt.write(f"{start_str} --> {end_str}\n")
                        f_srt.write(f"{text}\n\n")

            # Success message
            msg = f"Transcription complete!\n\nTXT saved to:\n{output_txt_path}"
            if output_srt_path:
                msg += f"\nSRT saved to:\n{output_srt_path}"
            messagebox.showinfo("Success", msg)

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n{e}")
        finally:
            self.progress_bar.stop()

    @staticmethod
    def srt_time_format(seconds):
        """
        Converts float seconds to SRT's HH:MM:SS,mmm format.
        Example: 12.345 -> 00:00:12,345
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds - int(seconds)) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

def main():
    root = tk.Tk()
    app = TranscriptionGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
