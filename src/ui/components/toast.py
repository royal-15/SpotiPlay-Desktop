"""Toast notification widget for non-intrusive messages."""
from PySide6.QtWidgets import QLabel, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

from ...config.constants import COLORS_DARK, ANIMATION_MEDIUM, BORDER_RADIUS


class Toast(QLabel):
    """Non-intrusive notification toast."""
    
    def __init__(self, message: str, toast_type: str = "info", parent=None, duration: int = 3000):
        super().__init__(parent)
        self.message = message
        self.toast_type = toast_type
        self.duration = duration
        
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self) -> None:
        """Setup toast appearance."""
        # Set text and alignment
        self.setText(self.message)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setWordWrap(True)
        
        # Set font
        font = QFont("Segoe UI", 13)
        self.setFont(font)
        
        # Set colors based on type
        colors = {
            "info": COLORS_DARK["info"],
            "success": COLORS_DARK["success"],
            "warning": COLORS_DARK["warning"],
            "error": COLORS_DARK["error"],
        }
        bg_color = colors.get(self.toast_type, COLORS_DARK["info"])
        
        # Apply styles
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {bg_color};
                color: white;
                padding: 16px 24px;
                border-radius: {BORDER_RADIUS}px;
                border: none;
            }}
        """)
        
        # Set size constraints
        self.setMinimumWidth(250)
        self.setMaximumWidth(500)
        self.adjustSize()
        
        # Set window flags for overlay
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
    
    def _setup_animation(self) -> None:
        """Setup fade-in/out animations."""
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        # Fade in animation
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(ANIMATION_MEDIUM)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # Fade out animation
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(ANIMATION_MEDIUM)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out.finished.connect(self.close)
    
    def show_toast(self) -> None:
        """Show the toast with fade-in animation."""
        # Position at top-center of parent or screen
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.center().x() - self.width() // 2
            y = parent_geometry.top() + 80
            self.move(x, y)
        
        self.show()
        self.fade_in.start()
        
        # Auto-dismiss after duration
        QTimer.singleShot(self.duration, self._start_fade_out)
    
    def _start_fade_out(self) -> None:
        """Start fade-out animation."""
        self.fade_out.start()
    
    @staticmethod
    def show_message(parent, message: str, toast_type: str = "info", duration: int = 3000) -> None:
        """Static method to show a toast notification."""
        toast = Toast(message, toast_type, parent, duration)
        toast.show_toast()
