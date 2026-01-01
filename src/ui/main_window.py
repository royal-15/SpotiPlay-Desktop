"""Main application window."""
import sys
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QComboBox, QLabel,
    QTableWidget, QTableWidgetItem, QProgressBar,
    QFileDialog, QHeaderView, QMessageBox, QSpinBox,
    QDialog, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QCloseEvent

from ..config.settings import SettingsManager
from ..config.constants import (
    APP_NAME, APP_VERSION, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
    QUALITY_OPTIONS, FORMAT_OPTIONS,
    STATUS_QUEUED, STATUS_DOWNLOADING, STATUS_COMPLETED, STATUS_FAILED,
)
from ..core.download_manager import DownloadManager
from ..core.download_worker import DownloadTask
from ..utils.validators import parse_multiple_urls, is_valid_directory, is_spotify_url, is_youtube_url
from ..utils.logger import logger
from .styles.theme import Theme
from .components.toast import Toast


class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Load settings
        self.settings_manager = SettingsManager()
        self.settings = self.settings_manager.settings
        
        # Initialize theme
        self.theme = Theme(self.settings.theme)
        
        # Initialize download manager
        self.download_manager = DownloadManager(self.settings, self)
        
        # Setup UI
        self._setup_window()
        self._setup_ui()
        self._apply_theme()
        self._connect_signals()
        
        # Show disclaimer if first run
        if self.settings.first_run:
            self._show_disclaimer()
        
        logger.info(f"{APP_NAME} v{APP_VERSION} started")
    
    def _setup_window(self) -> None:
        """Configure main window properties."""
        self.setWindowTitle(f"{APP_NAME} - Modern Music Downloader")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        
        # Restore window size
        if self.settings.window_maximized:
            self.showMaximized()
        else:
            self.resize(self.settings.window_width, self.settings.window_height)
    
    def _setup_ui(self) -> None:
        """Setup user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(16, 16, 16, 16)
        
        # Title
        title_label = QLabel(f"🎵 {APP_NAME}")
        title_label.setObjectName("subtitle")
        main_layout.addWidget(title_label)
        
        # Input section
        input_layout = QHBoxLayout()
        input_layout.setSpacing(8)
        
        # URL/Search input
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste URL or enter song name...")
        self.url_input.returnPressed.connect(self._on_add_clicked)
        input_layout.addWidget(self.url_input, 3)
        
        # Query type selector
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "Auto",
            "Spotify URL/Search",
            "YouTube URL",
            "Search on YouTube",
            "Search on Spotify"
        ])
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.currentTextChanged.connect(self._on_mode_changed)
        input_layout.addWidget(self.mode_combo, 1)
        
        # Quality selector
        quality_label = QLabel("Quality:")
        input_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(QUALITY_OPTIONS)
        self.quality_combo.setCurrentText(self.settings.default_quality)
        self.quality_combo.currentTextChanged.connect(self._on_quality_changed)
        input_layout.addWidget(self.quality_combo)
        
        # Format selector
        format_label = QLabel("Format:")
        input_layout.addWidget(format_label)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(FORMAT_OPTIONS)
        self.format_combo.setCurrentText(self.settings.default_format)
        self.format_combo.currentTextChanged.connect(self._on_format_changed)
        input_layout.addWidget(self.format_combo)
        
        # Add button
        self.add_button = QPushButton("Add to Queue")
        self.add_button.clicked.connect(self._on_add_clicked)
        input_layout.addWidget(self.add_button)
        
        main_layout.addLayout(input_layout)
        
        # Queue table
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(6)
        self.queue_table.setHorizontalHeaderLabels([
            "ID", "URL", "Status", "Progress", "Speed", "ETA"
        ])
        self.queue_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.queue_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.queue_table.setAlternatingRowColors(True)
        main_layout.addWidget(self.queue_table, 1)
        
        # Bottom controls
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(8)
        
        # Output directory
        dir_label = QLabel("Output:")
        bottom_layout.addWidget(dir_label)
        
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setText(self.settings.output_dir)
        bottom_layout.addWidget(self.output_dir_input, 2)
        
        self.browse_button = QPushButton("Browse...")
        self.browse_button.setObjectName("secondaryButton")
        self.browse_button.clicked.connect(self._on_browse_clicked)
        bottom_layout.addWidget(self.browse_button)
        
        bottom_layout.addStretch()
        
        # Control buttons
        self.start_all_button = QPushButton("Start All")
        self.start_all_button.clicked.connect(self._on_start_all_clicked)
        bottom_layout.addWidget(self.start_all_button)
        
        self.cancel_all_button = QPushButton("Cancel All")
        self.cancel_all_button.setObjectName("secondaryButton")
        self.cancel_all_button.clicked.connect(self._on_cancel_all_clicked)
        bottom_layout.addWidget(self.cancel_all_button)
        
        self.clear_completed_button = QPushButton("Clear Completed")
        self.clear_completed_button.setObjectName("secondaryButton")
        self.clear_completed_button.clicked.connect(self._on_clear_completed_clicked)
        bottom_layout.addWidget(self.clear_completed_button)
        
        self.clear_failed_button = QPushButton("Clear Failed")
        self.clear_failed_button.setObjectName("secondaryButton")
        self.clear_failed_button.clicked.connect(self._on_clear_failed_clicked)
        bottom_layout.addWidget(self.clear_failed_button)
        
        self.clear_all_button = QPushButton("Clear All")
        self.clear_all_button.setObjectName("dangerButton")
        self.clear_all_button.clicked.connect(self._on_clear_all_clicked)
        bottom_layout.addWidget(self.clear_all_button)
        
        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.setObjectName("secondaryButton")
        self.settings_button.clicked.connect(self._on_settings_clicked)
        bottom_layout.addWidget(self.settings_button)
        
        main_layout.addLayout(bottom_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def _apply_theme(self) -> None:
        """Apply theme to the application."""
        stylesheet = self.theme.get_stylesheet()
        self.setStyleSheet(stylesheet)
    
    def _connect_signals(self) -> None:
        """Connect download manager signals."""
        self.download_manager.task_added.connect(self._on_task_added)
        self.download_manager.task_updated.connect(self._on_task_updated)
        self.download_manager.task_completed.connect(self._on_task_completed)
        self.download_manager.task_failed.connect(self._on_task_failed)
        self.download_manager.queue_changed.connect(self._update_stats)
        self.download_manager.queue_changed.connect(self._refresh_table)
    
    def _on_add_clicked(self) -> None:
        """Handle add button click."""
        query_text = self.url_input.text().strip()
        
        if not query_text:
            Toast.show_message(self, "Please enter a URL or search query", "warning")
            return
        
        # Update settings
        self.settings.output_dir = self.output_dir_input.text().strip() or self.settings.output_dir
        self.settings_manager.save()
        
        # Process query based on mode
        mode = self.mode_combo.currentText()
        queries = self._process_query(query_text, mode)
        
        if not queries:
            Toast.show_message(self, "No valid URLs or queries found", "error")
            return
        
        # Add tasks
        self.download_manager.add_tasks(queries)
        
        # Clear input
        self.url_input.clear()
        
        Toast.show_message(self, f"Added {len(queries)} download(s) to queue", "success")
    
    def _process_query(self, text: str, mode: str) -> list[str]:
        """Process input text based on selected mode."""
        queries = []
        
        # Try to parse as multiple URLs first
        urls = parse_multiple_urls(text)
        
        if urls and mode == "Auto":
            # Multiple URLs detected, use them as-is
            return urls
        elif urls and len(urls) == 1:
            # Single URL, process based on mode
            url = urls[0]
            
            if mode == "Auto":
                return [url]
            elif mode == "Spotify URL/Search":
                if is_spotify_url(url):
                    return [url]
                else:
                    # Treat as search query
                    return [text]
            elif mode == "YouTube URL":
                if is_youtube_url(url):
                    return [url]
                else:
                    return []  # Invalid for this mode
            elif mode == "Search on YouTube":
                # Use yt-dlp search syntax
                return [f"ytsearch1:{text}"]
            elif mode == "Search on Spotify":
                # Use spotdl search (just pass the text)
                return [text]
        else:
            # No valid URLs, treat as search query
            if mode == "Auto" or mode == "Search on YouTube":
                # Default to YouTube search
                return [f"ytsearch1:{text}"]
            elif mode == "Spotify URL/Search" or mode == "Search on Spotify":
                # Spotify search
                return [text]
            elif mode == "YouTube URL":
                # Must be a URL in this mode
                return []
        
        return []
    
    def _on_mode_changed(self, mode: str) -> None:
        """Handle mode selector change."""
        # Update placeholder text based on mode
        placeholders = {
            "Auto": "Paste URL or enter song name...",
            "Spotify URL/Search": "Paste Spotify URL or search for songs...",
            "YouTube URL": "Paste YouTube URL...",
            "Search on YouTube": "Search for songs on YouTube...",
            "Search on Spotify": "Search for songs on Spotify..."
        }
        self.url_input.setPlaceholderText(placeholders.get(mode, "Paste URL or enter song name..."))
    
    def _on_quality_changed(self, quality: str) -> None:
        """Handle quality change."""
        self.settings.default_quality = quality
        self.settings_manager.save()
    
    def _on_format_changed(self, format_str: str) -> None:
        """Handle format change."""
        self.settings.default_format = format_str
        self.settings_manager.save()
    
    def _on_browse_clicked(self) -> None:
        """Handle browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_dir_input.text()
        )
        
        if directory:
            self.output_dir_input.setText(directory)
            self.settings.output_dir = directory
            self.settings_manager.save()
    
    def _on_start_all_clicked(self) -> None:
        """Handle start all button click."""
        self.download_manager.start_all_queued()
    
    def _on_cancel_all_clicked(self) -> None:
        """Handle cancel all button click."""
        self.download_manager.cancel_all()
        Toast.show_message(self, "Cancelled all downloads", "info")
    
    def _on_clear_completed_clicked(self) -> None:
        """Handle clear completed button click."""
        self.download_manager.clear_completed()
        Toast.show_message(self, "Cleared completed downloads", "info", 2000)
    
    def _on_clear_failed_clicked(self) -> None:
        """Handle clear failed button click."""
        self.download_manager.clear_failed()
        Toast.show_message(self, "Cleared failed downloads", "info", 2000)
    
    def _on_clear_all_clicked(self) -> None:
        """Handle clear all button click."""
        reply = QMessageBox.question(
            self,
            "Clear All",
            "Are you sure you want to clear all downloads from the queue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.download_manager.clear_all()
            Toast.show_message(self, "Cleared all downloads", "info", 2000)
    
    def _on_settings_clicked(self) -> None:
        """Handle settings button click."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings_manager.save()
            self.output_dir_input.setText(self.settings.output_dir)
            Toast.show_message(self, "Settings saved", "success")
    
    def _on_task_added(self, task: DownloadTask) -> None:
        """Handle new task added."""
        row = self.queue_table.rowCount()
        self.queue_table.insertRow(row)
        
        self.queue_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
        self.queue_table.setItem(row, 1, QTableWidgetItem(task.url[:80] + "..." if len(task.url) > 80 else task.url))
        self.queue_table.setItem(row, 2, QTableWidgetItem(task.status.capitalize()))
        
        progress_bar = QProgressBar()
        progress_bar.setValue(task.progress)
        self.queue_table.setCellWidget(row, 3, progress_bar)
        
        self.queue_table.setItem(row, 4, QTableWidgetItem(task.speed))
        self.queue_table.setItem(row, 5, QTableWidgetItem(task.eta))
    
    def _on_task_updated(self, task: DownloadTask) -> None:
        """Handle task update."""
        # Find task row
        for row in range(self.queue_table.rowCount()):
            id_item = self.queue_table.item(row, 0)
            if id_item and int(id_item.text()) == task.id:
                # Update status
                status_item = self.queue_table.item(row, 2)
                if status_item:
                    status_item.setText(task.status.capitalize())
                
                # Update progress bar
                progress_bar = self.queue_table.cellWidget(row, 3)
                if isinstance(progress_bar, QProgressBar):
                    progress_bar.setValue(task.progress)
                
                # Update speed and ETA
                speed_item = self.queue_table.item(row, 4)
                if speed_item:
                    speed_item.setText(task.speed or "")
                
                eta_item = self.queue_table.item(row, 5)
                if eta_item:
                    eta_item.setText(task.eta or "")
                
                break
    
    def _on_task_completed(self, task: DownloadTask) -> None:
        """Handle task completion."""
        logger.info(f"Task {task.id} completed")
        Toast.show_message(self, "Download completed!", "success", 2000)
    
    def _on_task_failed(self, task: DownloadTask) -> None:
        """Handle task failure."""
        logger.error(f"Task {task.id} failed: {task.error_message}")
        Toast.show_message(self, f"Download failed: {task.error_message[:50]}", "error", 4000)
    
    def _refresh_table(self) -> None:
        """Rebuild the queue table from current tasks."""
        # Clear the table
        self.queue_table.setRowCount(0)
        
        # Rebuild from download manager tasks
        all_tasks = self.download_manager.get_all_tasks()
        for task in all_tasks:
            row = self.queue_table.rowCount()
            self.queue_table.insertRow(row)
            
            self.queue_table.setItem(row, 0, QTableWidgetItem(str(task.id)))
            self.queue_table.setItem(row, 1, QTableWidgetItem(task.url[:80] + "..." if len(task.url) > 80 else task.url))
            self.queue_table.setItem(row, 2, QTableWidgetItem(task.status.capitalize()))
            
            progress_bar = QProgressBar()
            progress_bar.setValue(task.progress)
            self.queue_table.setCellWidget(row, 3, progress_bar)
            
            self.queue_table.setItem(row, 4, QTableWidgetItem(task.speed or ""))
            self.queue_table.setItem(row, 5, QTableWidgetItem(task.eta or ""))
    
    def _update_stats(self) -> None:
        """Update status bar with statistics."""
        stats = self.download_manager.get_stats()
        status_text = f"Total: {stats['total']} | Downloading: {stats['downloading']} | Completed: {stats['completed']} | Failed: {stats['failed']}"
        self.statusBar().showMessage(status_text)
    
    def _show_disclaimer(self) -> None:
        """Show disclaimer dialog on first run."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle("Disclaimer")
        msg_box.setText(
            "This application is intended only for downloading audio you have the legal "
            "right to download (e.g., your own content or content that is free to download).\n\n"
            "Downloading copyrighted material may violate Terms of Service and/or copyright law "
            "in your jurisdiction.\n\n"
            "By clicking 'I Understand', you acknowledge that you are solely responsible "
            "for how you use this application."
        )
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg_box.button(QMessageBox.StandardButton.Ok).setText("I Understand")
        
        result = msg_box.exec()
        
        if result == QMessageBox.StandardButton.Ok:
            self.settings.disclaimer_accepted = True
            self.settings.first_run = False
            self.settings_manager.save()
        else:
            QTimer.singleShot(0, self.close)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        # Save window state
        self.settings.window_maximized = self.isMaximized()
        if not self.isMaximized():
            self.settings.window_width = self.width()
            self.settings.window_height = self.height()
        
        # Save output directory
        self.settings.output_dir = self.output_dir_input.text().strip() or self.settings.output_dir
        
        self.settings_manager.save()
        
        # Cancel all downloads
        self.download_manager.cancel_all()
        
        logger.info("Application closed")
        event.accept()


class SettingsDialog(QDialog):
    """Settings dialog."""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """Setup dialog UI."""
        layout = QFormLayout(self)
        
        # Max parallel downloads
        self.parallel_spin = QSpinBox()
        self.parallel_spin.setRange(1, 10)
        self.parallel_spin.setValue(self.settings.max_parallel_downloads)
        layout.addRow("Max Parallel Downloads:", self.parallel_spin)
        
        # Tool paths
        self.yt_dlp_input = QLineEdit(self.settings.yt_dlp_path)
        layout.addRow("yt-dlp Path:", self.yt_dlp_input)
        
        self.spotdl_input = QLineEdit(self.settings.spotdl_path)
        layout.addRow("spotDL Path:", self.spotdl_input)
        
        self.ffmpeg_input = QLineEdit(self.settings.ffmpeg_path)
        layout.addRow("FFmpeg Path:", self.ffmpeg_input)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
    
    def accept(self) -> None:
        """Save settings and close."""
        self.settings.max_parallel_downloads = self.parallel_spin.value()
        self.settings.yt_dlp_path = self.yt_dlp_input.text().strip() or "yt-dlp"
        self.settings.spotdl_path = self.spotdl_input.text().strip() or "spotdl"
        self.settings.ffmpeg_path = self.ffmpeg_input.text().strip() or "ffmpeg"
        super().accept()
