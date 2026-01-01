from customtkinter import CTk, set_appearance_mode
from concurrent.futures import ThreadPoolExecutor
from modules.settings import WINDOW_FG, WINDOW_LOGO, COLLAPSE_ICON, EXTEND_ICON


class App(CTk):
    def __init__(self):
        # Setup
        super().__init__(fg_color=WINDOW_FG)

        self.isExtended = False

        # Progress tracking state
        self.total_tasks = 0
        self.completed_tasks = 0

        # Initialize basic UI first
        self.setup_basic_ui()

        # Defer heavy operations
        self.after(100, self.setup_remaining_components)

    def setup_basic_ui(self):
        """Setup the basic UI components that are immediately visible"""
        set_appearance_mode("dark")
        self.iconbitmap(WINDOW_LOGO)

        # Window
        self.geometry("600x200")
        self.title("SpotiPlay")
        self.minsize(600, 200)
        self.maxsize(600, 200)

        # Import UI components
        from modules.titlebar_widgets import titleBar
        from modules.inputField_widgets import inputFields
        from modules.controlField_widgets import controlField

        # Layout
        titleBar(self).pack(side="top", fill="x", pady=(4, 2), padx=4)

        self.inputFields = inputFields(self, onSaveClick=self.onSaveClick)
        self.inputFields.pack(side="top", fill="x")

        self.controls = controlField(
            self,
            retryMethod=self.onRetryClick,
            downloadMethod=self.onDownloadClick,
            resizeWindowMethod=self.onResizeWindowClick,
        )
        self.controls.pack(side="bottom", fill="x")

        # Set Closing Protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_remaining_components(self):
        """Setup remaining components after UI is visible"""
        # Create executor and initialize objects
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Import modules only when needed
        from modules.fileHandle import DataWriter
        from modules.downloadSpotify import Spotify
        from modules.downloadYoutube import Youtube

        # Get paths
        # self.getPaths()

        self.dataWriter = DataWriter(showMessage=self.showMessage)
        self.spotify = Spotify(
            self.executor,
            self.showMessage,
            on_tasks_started=self.on_tasks_started,
            on_task_completed=self.on_task_completed,
        )
        self.youtube = Youtube(
            self.executor,
            showMessage=self.showMessage,
            on_tasks_started=self.on_tasks_started,
            on_task_completed=self.on_task_completed,
        )

        # Fill saved data
        self.fill_saved_data()

    def fill_saved_data(self):
        """Fill the input fields with saved data"""
        try:
            url = self.dataWriter.read_url()
            path = self.dataWriter.read_path()

            if url == "" or path == "":
                return

            self.inputFields.input1.getUrlInput().insert(0, url)
            self.inputFields.input2.getPathInput().insert(0, path)
        except Exception as e:
            warning_message = f"Failed to fill saved data: {str(e)}"
            self.showMessage("Data Loading Error", warning_message, "w")

    def onSaveClick(self):
        # write the url to the file
        url = self.inputFields.input1.getUrlInput().get()
        path = self.inputFields.input2.getPathInput().get()

        if url == "" or path == "":
            warning_message = "Please enter a valid URL and path."
            self.showMessage("Save Error", warning_message, "w")
            return

        # Save synchronously; this is fast and keeps logic simple
        self.dataWriter.write_url_path(url, path)

    def onRetryClick(self, event):
        try:
            if self.controls.downloadBtn.cget("state") == "disabled":
                return

            # reset progress and update UI
            self.reset_progress()
            self.controls.status.configure(text="🔄 Retrying downloads, please wait...")
            self.controls.downloadBtn.configure(state="disabled")
            self.controls.status.update_idletasks()
            self.controls.downloadBtn.update_idletasks()

            path = self.inputFields.input2.getPathInput().get()
            self.executor.submit(self.spotify.retryDownloads, path)
        except Exception as e:
            warning_message = f"Failed to retry downloads: {str(e)}"
            self.showMessage("Retry Error", warning_message, "w")

    def onDownloadClick(self):
        # self.showMessage("Debug", "Inside onDownloadClick", "i")

        try:
            # Get inputs
            url = self.inputFields.input1.getUrlInput().get()
            path = self.inputFields.input2.getPathInput().get()

            if url == "" or path == "":
                return

            print(f"🔄 Downloading... '{url}'")

            # reset progress and UI state
            self.reset_progress()
            self.controls.downloadBtn.configure(state="disabled")
            self.controls.status.configure(text="🔄 Starting downloads...")
            self.controls.status.update_idletasks()

            # Check if the URL is a Spotify link
            if self.isSpotifyLink(url):
                # self.showMessage("Debug", "It's a Spotify link", "i")
                self.executor.submit(self.spotify.download, url, path)
            else:  # It's a YouTube link
                # self.showMessage("Debug", "It's a YouTube link", "i")
                self.executor.submit(self.youtube.download, url, path)

            self.inputFields.input1.getUrlInput().delete(0, "end")
        except Exception as e:
            error_message = f"Failed to start download: {str(e)}"
            self.showMessage("Download Error", error_message, "e")

    def onResizeWindowClick(self):
        if self.isExtended:
            self.geometry("600x200")
            self.minsize(600, 200)
            self.maxsize(600, 200)

            self.isExtended = False

            self.controls.resizeWindowBtn.changeImage(EXTEND_ICON)
        else:
            self.geometry("600x400")
            self.minsize(600, 400)
            self.maxsize(600, 400)

            self.isExtended = True

            self.controls.resizeWindowBtn.changeImage(COLLAPSE_ICON)

    def isSpotifyLink(self, url: str) -> bool:
        # Returns True if the given URL is a Spotify link, otherwise returns False for YouTube links.
        youtube_patterns = [
            r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/",
        ]

        import re

        for pattern in youtube_patterns:
            if re.match(pattern, url):
                return False  # It's a YouTube link

        return True  # It's not a YouTube link

    def on_close(self):
        from tkinter import messagebox

        if messagebox.askyesno("Exit", "Are you sure you want to close?"):
            # Shutdown executor (forcefully stop tasks)
            self.executor.shutdown(wait=False, cancel_futures=True)

            # Destroy the Tkinter window
            self.destroy()
            print("🔴 Application closed.")

    def reset_progress(self):
        """Reset progress counters and progress bar."""
        self.total_tasks = 0
        self.completed_tasks = 0
        if hasattr(self.controls, "progressBar"):
            self.controls.progressBar.set(0)
        # Restore default status text
        self.controls.status.configure(text="@royal-15 Officials")
        # Ensure Download button is enabled by default
        self.controls.downloadBtn.configure(state="normal")

    def _update_progress_ui(self):
        """Update status label and progress bar based on current counters."""
        if self.total_tasks <= 0:
            return

        progress = self.completed_tasks / self.total_tasks
        progress = max(0.0, min(1.0, progress))

        if hasattr(self.controls, "progressBar"):
            self.controls.progressBar.set(progress)

        if self.completed_tasks >= self.total_tasks:
            self.controls.status.configure(text="✅ All Done")
            self.controls.downloadBtn.configure(state="normal")
        else:
            self.controls.status.configure(
                text=f"🔄 Downloading {self.completed_tasks} / {self.total_tasks}..."
            )

    def _notify_tasks_started_main_thread(self, count):
        if count <= 0:
            return

        # First task of a new batch
        if self.total_tasks == 0 and self.completed_tasks == 0:
            if hasattr(self.controls, "progressBar"):
                self.controls.progressBar.set(0)
            self.controls.status.configure(
                text=f"🔄 Downloading 0 / {count}..."
            )

        self.total_tasks += count
        # Keep download button disabled while tasks are running
        self.controls.downloadBtn.configure(state="disabled")
        self._update_progress_ui()

    def _notify_task_completed_main_thread(self):
        if self.total_tasks <= 0:
            return

        self.completed_tasks += 1
        self._update_progress_ui()

    def on_tasks_started(self, count: int):
        """Thread-safe callback for workers to report batch start."""
        self.after(0, self._notify_tasks_started_main_thread, count)

    def on_task_completed(self):
        """Thread-safe callback for workers to report task completion."""
        self.after(0, self._notify_task_completed_main_thread)

    def showMessage(self, title, message, type="error"):
        from tkinter import messagebox

        if type == "i":
            print(f"ℹ️ INFO - {title}: {message}")
            messagebox.showinfo(title, message)
        elif type == "w":
            print(f"⚠️ WARNING - {title}: {message}")
            messagebox.showwarning(title, message)
        else:
            # Treat any other value (including "e" or "error") as an error
            print(f"❌ ERROR - {title}: {message}")
            messagebox.showerror(title, message)


# Command to build the exe
# pyinstaller --onefile --noconsole --icon="C:\Users\rajat\Desktop\My Projects\SpotiPlay App\resources\logo1.ico" --add-data "modules;modules" --hidden-import=customtkinter --hidden-import=pillow --hidden-import=mutagen --hidden-import=yt_dlp SpotiPlay.py


if __name__ == "__main__":
    app = App()
    app.mainloop()  # Start the main event loop
