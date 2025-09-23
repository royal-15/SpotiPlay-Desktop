import os
import sys
import json
import appdirs


class DataWriter:
    def __init__(self, filename="data.json", showMessage=None):
        self.showMessage = showMessage

        try:
            if getattr(sys, "frozen", False):
                # Running as bundled exe
                app_name = "SpotiPlay"
                app_author = "SpotiPlay"
                data_dir = appdirs.user_data_dir(app_name, app_author)
                os.makedirs(data_dir, exist_ok=True)
                self.filename = os.path.join(data_dir, filename)
            else:
                # Running as script
                self.filename = filename

            # Initialize file if missing or empty
            if not os.path.exists(self.filename) or os.stat(self.filename).st_size == 0:
                self._write_data({"url": "", "path": ""})

            print(f"Data file location: {self.filename}")

        except Exception as e:
            error_message = f"Error initializing data file: {str(e)}"
            if self.showMessage:
                self.showMessage("Data File Error", error_message, "e")

    def _read_data(self):
        """Internal: Read entire JSON object from file."""
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            return {"url": "", "path": ""}
        except json.JSONDecodeError:
            return {"url": "", "path": ""}
        except Exception as e:
            warning_message = f"Error reading data: {str(e)}"
            if self.showMessage:
                self.showMessage("Read Error", warning_message, "w")
            return {"url": "", "path": ""}

    def _write_data(self, data):
        """Internal: Write entire JSON object to file."""
        try:
            with open(self.filename, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2)
        except Exception as e:
            warning_message = f"Error writing data: {str(e)}"
            if self.showMessage:
                self.showMessage("Write Error", warning_message, "w")
            return False
        return True

    def write_url_path(self, url, path):
        """Update only the URL in the JSON file."""
        try:
            data = self._read_data()
            data["url"] = url
            data["path"] = path
            return self._write_data(data)
        except Exception as e:
            warning_message = f"Error writing: {str(e)}"
            if self.showMessage:
                self.showMessage("Save Error", warning_message, "w")
            return False

    def read_url(self):
        """Get the URL value from the JSON file."""
        try:
            data = self._read_data()
            return data.get("url", "")
        except Exception as e:
            warning_message = f"Error reading URL: {str(e)}"
            if self.showMessage:
                self.showMessage("URL Read Error", warning_message, "w")
            return ""

    def read_path(self):
        """Get the path value from the JSON file."""
        try:
            data = self._read_data()
            return data.get("path", "")
        except Exception as e:
            warning_message = f"Error reading path: {str(e)}"
            if self.showMessage:
                self.showMessage("Path Read Error", warning_message, "w")
            return ""
