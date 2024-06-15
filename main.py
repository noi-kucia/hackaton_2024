import customtkinter as ctk
from typing import List, Tuple, Generator
from abc import ABC, abstractmethod


class Cell(ABC):
    """
    Base class for all cells in file

    every instance of this class must realize _open_ and _edit_ methods that changes current layout
    """

    @abstractmethod
    def __init__(self, data):
        self.__data__: dict = data
        self._render_()  # rendering data
        self.view_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = self._open_()    # showing data
        self.edit_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = None
        ...

    @abstractmethod
    def _render_(self):
        """
        creates new view frame based on __data__
        :return:
        """
        ...

    @abstractmethod
    def _save_(self):
        """
        saves  changes into file
        :return:
        """
        ...

    @abstractmethod
    def _open_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        """
        changes current layout to view mode and renders it again

        :return: CTkFrame[Scrollable] object with rendered information ( rather not editable )
        """
        ...

    @abstractmethod
    def _edit_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        """
        changes current layout to edit mode

        :return:  CTkFrame[Scrollable] object allows to edit data in it
        """
        ...


class PlainTextCell(ctk.CTkFrame, Cell):

    def __init__(self, parent, data):
        """
        :param data: {"text": <some text> }
        """
        super().__init__(parent)
        self.configure()
        self.__data__: dict = data
        self.view_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = None
        self.edit_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = None
        self._render_()  # rendering data
        self._open_()    # showing data

    def _render_(self):
        data = self.__data__

        new_frame = ctk.CTkFrame(self, corner_radius=8, border_width=2)
        new_frame.columnconfigure(0, weight=1)
        self.view_frame = new_frame
        self.view_frame.pack()

        text = data["text"]
        text_frame = ctk.CTkLabel(new_frame, text=text, font=('Arial', 16))
        text_frame.grid(row=0, column=0, sticky='WE')

    def _open_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        self.view_frame.tkraise()

    def _save_(self):
        pass

    def _edit_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        new_frame = ctk.CTkFrame(self, corner_radius=8, border_width=2, fg_color='#00FFAA')
        self.edit_frame = new_frame
        self.edit_frame.pack(expand=True, fill='x')
        self.edit_frame.tkraise()


class Viewer(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.columnconfigure(0, weight=99)

        # test cells
        cell1 = PlainTextCell(self, {"text": "some \nmultiline\ntext\t\t2131 ,kf ,kf kfjalfjl;kafjsdljl"})

        self.cells: List[Cell] = [cell1]

        self.__draw__()

    def __draw__(self):
        for cell_num, cell in enumerate(self.cells):
            cell.grid(row=cell_num, column=0, sticky='WE')


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
