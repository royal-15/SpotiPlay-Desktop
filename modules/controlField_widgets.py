from customtkinter import CTkFrame, CTkLabel, CTkImage, CTkButton, CTkProgressBar
from .settings import *
from PIL import Image


class controlField(CTkFrame):
    def __init__(self, parent, retryMethod, downloadMethod, resizeWindowMethod):
        super().__init__(parent)

        # Status Label
        self.status = statusLabel(self)
        self.status.pack(side="left", padx=(15, 0))

        # Progress Bar
        self.progressBar = CTkProgressBar(self, width=180)
        self.progressBar.pack(side="left", padx=(10, 0), pady=(0, 2))
        self.progressBar.set(0)

        # ResizeWindow Button
        img = Image.open(EXTEND_ICON)
        img = img.convert("RGBA")
        ctk_img = CTkImage(light_image=img, dark_image=img, size=(18, 13))
        self.resizeWindowBtn = resizeWindowButton(self, ctk_img, resizeWindowMethod)
        self.resizeWindowBtn.place(relx=0.5, rely=0.5, anchor="center")

        # Download Button
        self.downloadBtn = CTkButton(
            self,
            text="Download",
            fg_color=GREEN_BTN_FG,
            hover_color=GREEN_BTN_FG_HOVER,
            text_color="white",
            font=BUTTON_FONT,
            width=125,
            height=33,
            corner_radius=6,
            command=downloadMethod,
        )
        self.downloadBtn.pack(side="right")

        # Retry Button
        img = Image.open(RETRY_ICON)
        img = img.convert("RGBA")
        ctk_img = CTkImage(light_image=img, dark_image=img, size=(25, 25))
        self.retry_label = CTkLabel(
            self,
            text="",
            image=ctk_img,
            cursor="hand2",
            compound="left",
        )
        self.retry_label.bind("<Button-1>", retryMethod)
        self.retry_label.place(x=444, y=1)


class statusLabel(CTkLabel):
    def __init__(self, parent):
        super().__init__(
            parent,
            text="@royal-15 Officials",
            font=BUTTON_FONT,
            text_color=STATUS_TEXT_COLOR,
        )


class resizeWindowButton(CTkButton):
    def __init__(self, parent, ctk_img, resizeWindowMethod):
        super().__init__(
            parent,
            text="",
            image=ctk_img,
            width=18,
            height=13,
            cursor="hand2",
            command=resizeWindowMethod,
            corner_radius=15,
            fg_color="transparent",
            bg_color=RESIZE_BTN_FG,
            hover_color=RESIZE_BTN_FG_HOVER,
        )

    def changeImage(self, imgPath):
        img = Image.open(imgPath)
        img = img.convert("RGBA")
        ctk_img = CTkImage(light_image=img, dark_image=img, size=(18, 13))
        self.configure(image=ctk_img)
