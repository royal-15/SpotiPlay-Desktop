from customtkinter import CTk, set_appearance_mode
from concurrent.futures import ThreadPoolExecutor
from modules.settings import WINDOW_FG, WINDOW_LOGO, COLLAPSE_ICON, EXTEND_ICON


class App(CTk):
    def __init__(self):
        # Setup
        super().__init__(fg_color=WINDOW_FG)

        self.isExtended = False

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
        self.futures = []
        self.executor = ThreadPoolExecutor(max_workers=5)

        # Import modules only when needed
        from modules.fileHandle import DataWriter
        from modules.downloadSpotify import Spotify
        from modules.downloadYoutube import Youtube

        # Get paths
        # self.getPaths()

        self.dataWriter = DataWriter()
        self.spotify = Spotify(self.executor, self.showMessage)
        self.youtube = Youtube(
            self.executor,
            futures=self.futures,
            showMessage=self.showMessage,
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

        future = self.executor.submit(self.dataWriter.write_url_path, url, path)
        self.futures.append(future)

    def onRetryClick(self, event):
        try:
            if self.controls.downloadBtn.cget("state") == "disabled":
                return

            # ui updates
            self.controls.status.configure(text="🔄 Retrying downloads, Please Wait!!")
            self.controls.downloadBtn.configure(state="disabled")
            self.controls.status.update_idletasks()
            self.controls.downloadBtn.update_idletasks()

            path = self.inputFields.input2.getPathInput().get()
            future = self.executor.submit(self.spotify.retryDownloads, path)
            self.futures.append(future)

            # ui updates
            future.add_done_callback(self.checkStatus)
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

            # Check if the URL is a Spotify link
            if self.isSpotifyLink(url):

                # self.showMessage("Debug", "It's a Spotify link", "i")

                future = self.executor.submit(self.spotify.download, url, path)
                self.futures.append(future)
            else:  # It's a YouTube link

                # self.showMessage("Debug", "It's a YouTube link", "i")

                future = self.executor.submit(self.youtube.download, url, path)
                self.futures.append(future)

            self.inputFields.input1.getUrlInput().delete(0, "end")

            # ui update
            self.controls.status.configure(text="🔄 Downloading...")
            self.controls.status.update_idletasks()

            self.after(3000, self.checkStatus)
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

    def checkStatus(self, future=None):
        # Check if any threads are running & update label accordingly
        active_threads = len(self.executor._threads)

        if active_threads == 0 or all(f.done() for f in self.futures):
            self.controls.status.configure(text="✅ All Done")
            self.controls.downloadBtn.configure(state="normal")
        else:
            self.controls.status.configure(text=f"🔄 Downloading...")

        # Check again after 3 second
        self.after(3000, self.checkStatus)

    def showMessage(self, title, message, type="error"):
        from tkinter import messagebox

        if type == "i":
            print(f"ℹ️ INFO - {title}: {message}")
            messagebox.showinfo(title, message)

        if type == "w":
            print(f"⚠️ WARNING - {title}: {message}")
            messagebox.showwarning(title, message)

        if type == "er":
            print(f"❌ ERROR - {title}: {message}")
            messagebox.showerror(title, message)


# Command to build the exe
# pyinstaller --onefile --noconsole --icon="C:\Users\rajat\Desktop\My Projects\SpotiPlay App\resources\logo1.ico" --add-data "modules;modules" --hidden-import=customtkinter --hidden-import=pillow --hidden-import=mutagen --hidden-import=yt_dlp SpotiPlay.py


if __name__ == "__main__":
    app = App()
    app.mainloop()  # Start the main event loop
