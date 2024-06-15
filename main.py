import customtkinter as ctk
from typing import List, Tuple, Generator
from abc import ABC, abstractmethod


class Cell(ABC):
    """
    Base class for all cells in file

    every instance of this class must realize _open_ and _edit_ methods
    """

    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def _open_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        """
        :return: CTkFrame[Scrollable] object with rendered information ( rather not editable )
        """
        ...

    @abstractmethod
    def _edit_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        """
        :return:  CTkFrame[Scrollable] object allows to edit data in it
        """
        ...


class Viewer(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent)

        self.cells: List[Cell] = []


class UpperMenu(ctk.CTkFrame):
    """
    frame with instruments for editing
    """
    def __init__(self, parent):
        super().__init__(parent, height=75)


class RightMenu(ctk.CTkFrame):
    """
    frame for some instruments from right side of application
    """
    def __init__(self, parent):
        super().__init__(parent)


class App(ctk.CTk):

    def __init__(self):
        self.window = super().__init__()

        # gridding upper menu
        upper_menu_coords = (0, 0)
        self.grid_rowconfigure(upper_menu_coords[0], weight=1)
        self.grid_columnconfigure(upper_menu_coords[1], weight=1)
        self.upper_menu = UpperMenu(self)
        self.upper_menu.grid(row=upper_menu_coords[0], column=upper_menu_coords[1], columnspan=2, sticky='SWEN', pady=5)

        # gridding side menu
        side_menu_coords = (1, 1)
        self.side_menu = RightMenu(self)
        self.side_menu.grid(row=side_menu_coords[0], column=side_menu_coords[1], sticky='SWEN')

        # gridding viewer
        viewer_coords = (1, 0)
        self.grid_columnconfigure(viewer_coords[1], weight=9)
        self.grid_rowconfigure(viewer_coords[0], weight=50)
        self.viewer = Viewer(self)
        self.viewer.grid(row=viewer_coords[0], column=viewer_coords[1], sticky='SWEN')


if __name__ == '__main__':
    window = App()
    window.title("hackaton")
    window.mainloop()
