from customtkinter import CTkFrame, CTkLabel, CTkImage
from .settings import *
from PIL import Image
import webbrowser


class titleBar(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=WINDOW_FG, height=30)

        title(self).pack(side="left", pady=0)

        self.logo = logo(self)
        self.logo.pack(side="right", padx=7)
        self.logo.bind(
            "<Button-1>",
            lambda e: webbrowser.open("https://www.spotify.com/", new=2),
        )


class title(CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color=WINDOW_FG)

        CTkLabel(
            self, text="SpotiPlay", font=TITLE_FONT1, text_color=TITLE_COLOR1
        ).pack(side="left", padx=8)

        CTkLabel(
            self,
            text="– Your Music, Your Way!",
            font=TITLE_FONT2,
            text_color=TITLE_COLOR2,
        ).pack(side="left")


class logo(CTkLabel):
    def __init__(self, parent):
        logo_image = CTkImage(light_image=Image.open(UI_LOGO), size=(35, 35))
        super().__init__(parent, image=logo_image, text="", cursor="hand2")
