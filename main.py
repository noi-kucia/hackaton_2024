import tkinter

import customtkinter as ctk
from typing import List, Tuple, Generator
from abc import ABC, abstractmethod
from PIL import Image

class Cell(ABC):
    """
    Base class for all cells in file

    every instance of this class must realize _open_ and _edit_ methods that changes current layout
    """

    @abstractmethod
    def __init__(self, data):
        self.__data__: dict = data
        self._render_()  # rendering data
        self.view_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = self._open_()  # showing data
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


class AutoWrappingCTkLabel(ctk.CTkLabel):
    def __init__(self, master=None, **kwargs):
        self.text = kwargs.pop("text", "")
        super().__init__(master, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.configure(text=self.text)
        self.update_wraplength()

    def on_resize(self, event):
        self.update_wraplength()

    def update_wraplength(self):
        current_width = int(self.winfo_width() / 1.6)
        if current_width > 1:  # Avoid wraplength of 0
            self.configure(wraplength=current_width)

    def set_text(self, new_text):
        self.text = new_text
        self.configure(text=self.text)
        self.update_wraplength()


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
        self._open_()  # showing data

    def _render_(self):
        data = self.__data__

        new_frame = ctk.CTkFrame(self, corner_radius=8, border_width=2)
        new_frame.columnconfigure(0, weight=1)
        new_frame.rowconfigure(0, weight=1)

        if self.view_frame:
            self.view_frame.destroy()
            self.view_frame = None
        self.view_frame = new_frame
        self.view_frame.pack(fill='both')

        text = data["text"]
        text_frame = AutoWrappingCTkLabel(master=new_frame, text=text, font=('Arial', 20), justify='left')
        text_frame.grid(row=0, column=0, sticky='NSEW')
        text_frame.bind('<Double-Button-1>', self._edit_)

    def _open_(self, event=None) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        # if self.edit_frame:
        #     self.edit_frame.destroy()
        if not self.view_frame:
            self._render_()
        if self.edit_frame:
            self.edit_frame.destroy()
            self.edit_frame = None
        self.view_frame.tkraise()

    def _save_(self):
        new_text = self.entry_frame.get("0.0", "end")
        self.__data__["text"] = new_text
        print("don't forget to save into file")

    def _edit_(self, event=None) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        data = self.__data__
        new_frame = ctk.CTkFrame(self, corner_radius=8, border_width=2)
        new_frame.columnconfigure(0, weight=1)
        new_frame.rowconfigure(0, weight=1)

        if self.edit_frame:
            self.edit_frame.destroy()
            self.edit_frame = None
        if self.view_frame:
            self.view_frame.destroy()
            self.view_frame = None
        self.edit_frame = new_frame
        self.edit_frame.pack(fill='both', expand=True, side='top')

        def exit_edit_mode(event=None):
            self._save_()
            self._open_()

        self.entry_frame = ctk.CTkTextbox(new_frame, font=('Arial', 20), wrap='word')
        self.entry_frame.insert('0.0', data["text"])
        self.entry_frame.grid(row=0, column=0, sticky='NSEW')
        self.entry_frame.bind('<Shift-Return>', exit_edit_mode)

        self.edit_frame.tkraise()


class QuizCell(ctk.CTkFrame, Cell):
    def __init__(self, parent, data):
        """
        :param data: {"text": <some text>, "answers": [<answer1>, <answer2>, ...], "correct_answers": [<correct1>, <correct2>, ...] }
        """
        super().__init__(parent, border_width=0)
        self.configure()
        self.__data__ = data
        self.view_frame = None
        self.edit_frame = None
        self.answer_vars = []
        self._render_()  # rendering data
        self._open_()  # showing data

    def _render_(self):
        if self.view_frame:
            self.view_frame.pack_forget()

        data = self.__data__

        new_frame = ctk.CTkFrame(self, corner_radius=8, width=500, height=300)
        new_frame.columnconfigure(0, weight=1)
        self.view_frame = new_frame
        self.view_frame.pack(fill='both', expand=True)

        # Display the question text
        question_text = data["text"]
        question_label = ctk.CTkLabel(new_frame, text=question_text, font=('Arial', 20))
        question_label.grid(row=0, column=0, sticky='WE', padx=10, pady=5)

        # Display the answers with checkboxes
        answers = data.get("answers", [])
        self.answer_vars = []
        for idx, answer in enumerate(answers):
            answer_var = ctk.StringVar(value="")
            self.answer_vars.append(answer_var)
            answer_checkbox = ctk.CTkCheckBox(new_frame, text=answer, variable=answer_var, onvalue=answer, offvalue="")
            answer_checkbox.grid(row=idx + 1, column=0, padx=20, pady=2)

        # Add a button to check answers
        check_button = ctk.CTkButton(new_frame, text="Check Answer", command=self.check_answer)
        check_button.grid(row=len(answers) + 1, column=0, pady=10)

        # Bind double-click event
        new_frame.bind("<Double-Button-1>", self._edit_)

    def _open_(self):
        self.view_frame.tkraise()

    def _save_(self):
        # Save edited data
        new_question_text = self.question_entry.get()
        new_answers = []
        new_correct_answers = []

        for entry, checkbox in zip(self.answer_entries, self.correct_checkboxes):
            answer = entry.get()
            if answer:
                new_answers.append(answer)
                if checkbox.get():
                    new_correct_answers.append(answer)

        self.__data__['text'] = new_question_text
        self.__data__['answers'] = new_answers
        self.__data__['correct_answers'] = new_correct_answers

        self.edit_frame.pack_forget()
        self._render_()

    def _edit_(self, event=None):
        if self.edit_frame:
            self.edit_frame.pack_forget()

        new_frame = ctk.CTkScrollableFrame(self, corner_radius=8, border_width=2, width=300,
                                           height=300)  # Adjust size as needed
        self.edit_frame = new_frame
        self.edit_frame.pack(expand=True, fill='both')

        # Display editable question
        self.question_entry = ctk.CTkEntry(new_frame, width=400)
        self.question_entry.insert(0, self.__data__['text'])
        self.question_entry.grid(row=0, column=0, columnspan=3, padx=10, pady=5)

        # Display editable answers
        self.answer_entries = []
        self.correct_checkboxes = []
        answers = self.__data__.get("answers", [])
        correct_answers = self.__data__.get("correct_answers", [])
        for idx, answer in enumerate(answers):
            self._add_answer_row(new_frame, idx, answer, answer in correct_answers)

        # Add button to save changes
        save_button = ctk.CTkButton(new_frame, text="Save", command=self._save_)
        save_button.grid(row=len(answers) + 1, column=0, pady=10)

        # Add button to add a new answer
        add_answer_button = ctk.CTkButton(new_frame, text="Add Answer", command=self._add_new_answer)
        add_answer_button.grid(row=len(answers) + 2, column=0, pady=10)

    def _add_answer_row(self, frame, idx, answer_text='', is_correct=False):
        answer_entry = ctk.CTkEntry(frame)
        answer_entry.insert(0, answer_text)
        answer_entry.grid(row=idx + 1, column=0, padx=10, pady=2, sticky='W')
        self.answer_entries.append(answer_entry)

        correct_var = ctk.BooleanVar(value=is_correct)
        correct_checkbox = ctk.CTkCheckBox(frame, variable=correct_var, text="Correct")
        correct_checkbox.grid(row=idx + 1, column=1, padx=10, pady=2, sticky='W')
        self.correct_checkboxes.append(correct_checkbox)

        # Add delete button for each answer
        delete_button = ctk.CTkButton(frame, text="Delete", command=lambda: self._delete_answer_row(frame, idx))
        delete_button.grid(row=idx + 1, column=2, padx=10, pady=2, sticky='W')

    def _delete_answer_row(self, frame, idx):
        self.answer_entries[idx].grid_forget()
        self.correct_checkboxes[idx].grid_forget()
        self.answer_entries.pop(idx)
        self.correct_checkboxes.pop(idx)

        # Adjust remaining rows
        for i in range(idx, len(self.answer_entries)):
            self.answer_entries[i].grid_configure(row=i + 1)
            self.correct_checkboxes[i].grid_configure(row=i + 1)

        # Redraw the save and add answer buttons
        self._redraw_save_and_add_buttons()

    def _add_new_answer(self):
        idx = len(self.answer_entries)
        self._add_answer_row(self.edit_frame, idx)

        # Redraw the save and add answer buttons
        self._redraw_save_and_add_buttons()

    def _redraw_save_and_add_buttons(self):
        # Remove existing buttons
        for widget in self.edit_frame.grid_slaves():
            if int(widget.grid_info()["row"]) >= len(self.answer_entries) + 1:
                widget.grid_forget()

        # Add button to save changes
        save_button = ctk.CTkButton(self.edit_frame, text="Save", command=self._save_)
        save_button.grid(row=len(self.answer_entries) + 1, column=0, pady=10)

        # Add button to add a new answer
        add_answer_button = ctk.CTkButton(self.edit_frame, text="Add Answer", command=self._add_new_answer)
        add_answer_button.grid(row=len(self.answer_entries) + 2, column=0, pady=10)

    def check_answer(self):
        # Get the selected answers
        selected_answers = [var.get() for var in self.answer_vars if var.get()]
        correct_answers = self.__data__.get("correct_answers", [])

        # Check if the selected answers match the correct answers
        if set(selected_answers) == set(correct_answers):
            result_text = "Correct!!!"
            result_color = '#00FF00'
        else:
            result_text = "Incorrect!"
            result_color = '#FF0000'

        # Display result
        result_label = ctk.CTkLabel(self.view_frame, text=result_text, font=('Arial', 20), text_color=result_color)
        result_label.grid(row=len(self.answer_vars) + 2, column=0, pady=10)


class Viewer(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_frame: ctk.CTkFrame = None  # curently selected frame

        # test cells
        cell1 = PlainTextCell(self, {
            "text": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. In ac sollicitudin eros. Duis vitae arcu maximus, congue enim et, pretium lorem. Sed mauris nisi, pharetra id cursus nec, viverra ut diam. Proin scelerisque molestie turpis, sit amet posuere nisl mattis at. Donec in aliquam massa. Pellentesque ullamcorper scelerisque consectetur. Phasellus blandit massa ex, vel molestie sem malesuada vitae. Mauris euismod egestas mi, nec cursus mi accumsan non. Etiam odio dui, ornare nec iaculis eu, ullamcorper at lorem. Vestibulum tristique, massa et auctor dictum, sem lorem viverra massa, in fringilla velit nisi a diam. Vivamus pharetra placerat ligula, quis congue sem suscipit eget. Donec ullamcorper, leo nec laoreet hendrerit, ligula nisl egestas lacus, id scelerisque tortor justo vel metus. Quisque at dui at diam aliquet lobortis ac in nunc. Sed in tincidunt massa, eget volutpat ipsum. Integer tincidunt eleifend gravida. "})

        cell2 = QuizCell(self, {
            "text": "What are the primary colors?",
            "answers": [
                "Red",
                "Green",
                "Blue",
                "Yellow"
            ],
            "correct_answers": [
                "Red",
                "Blue",
                "Yellow"
            ]
        })

        cell3 = PlainTextCell(self, {
            "text": """
             Donec quis convallis metus. Fusce varius malesuada mollis. Nam bibendum lectus non diam molestie dapibus. Phasellus at vehicula enim. Etiam blandit vehicula lorem vitae aliquet. Sed ac finibus purus, ac ornare dolor. Nunc consectetur porta velit, a hendrerit orci varius a. Maecenas lacinia venenatis hendrerit. Vestibulum non orci porta, accumsan sem vel, mattis purus. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.

Phasellus quis lectus blandit, feugiat arcu sit amet, vulputate ex. Integer vitae nisl ante. Aenean non magna tempus, porttitor dolor nec, iaculis felis. Quisque convallis, nisl sit amet interdum iaculis, massa eros auctor erat, quis facilisis ipsum justo non leo. Nam laoreet, justo sit amet aliquet mattis, felis eros sagittis sapien, quis finibus est lacus vel ligula. Morbi eget suscipit massa. Nulla nec metus in ex egestas semper. Cras consequat felis non scelerisque iaculis. Pellentesque dictum dictum nulla, ut efficitur lorem tincidunt sit amet. Phasellus tempor placerat nisl et fermentum. Vestibulum maximus hendrerit leo id mattis. Nulla quis leo in est malesuada fringilla. Nunc dignissim aliquet lorem, eu varius augue imperdiet sit amet. Nam venenatis metus scelerisque bibendum malesuada. 
"""})

        self.cells: List[Cell] = [cell1, cell2, cell3]
        self.__draw__()

    def __draw__(self):
        for cell_num, cell in enumerate(self.cells):
            self.columnconfigure(0, weight=99)
            self.rowconfigure(0, weight=99)
            cell.grid(row=cell_num, column=0, sticky='WE', pady=5)

    def select_frame(self, frame: ctk.CTkFrame):
        # unselect previous one ( delete boarding)

        frame.configure(border_width=2, border_color='#5584e0')
        pass


class UpperMenu(ctk.CTkFrame):
    """
    frame with instruments for editing
    """

    def __init__(self, parent):
        super().__init__(parent, height=75)
        self.add_buttons()

    def add_buttons(self):

        upper_arrow_texture = ctk.CTkImage(dark_image=Image.open('uppper_arrow.png'))
        self.upper_arrow_button = ctk.CTkButton(self, image=upper_arrow_texture, text="", width=28, fg_color='transparent')
        self.upper_arrow_button.pack(side='left', fill='y')

        down_arrow_texture = ctk.CTkImage(dark_image=Image.open('down_arrow.png'))
        self.down_arrow_button = ctk.CTkButton(self, image=down_arrow_texture, text="", width=28, fg_color='transparent')
        self.down_arrow_button.pack(side='left', fill='y')


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
    window.minsize(720, 480)
    window.mainloop()
