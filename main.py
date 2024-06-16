import json
import tkinter

import customtkinter as ctk
from CTkMessagebox import CTkMessagebox
from typing import List, Tuple, Generator
from abc import ABC, abstractmethod
from PIL import Image, ImageTk


class Cell(ABC):
    """
    Base class for all cells in file

    every instance of this class must realize _open_ and _edit_ methods that changes current layout
    """

    @abstractmethod
    def __init__(self, data):
        self.__data__: dict = data
        self.view_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = self._open_()  # showing data
        self.edit_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = None
        self._render_()  # rendering data
        ...

    @abstractmethod
    def _import_(self) -> dict:
        """
        returns formated tuple which will be saved into file
        {
            "cell_type": <type>,
            "data": <data>
        }
        :return: dictionary
        """

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
        current_width = int(self.winfo_width() / 1.2)
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
        self.root = parent

        self.configure()
        self.__data__: dict = data
        self.view_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = None
        self.edit_frame: [ctk.CTkFrame, ctk.CTkScrollableFrame] = None
        self._render_()  # rendering data
        self._open_()  # showing data

    def _import_(self) -> dict:
        return {"cell_type": "plain text", "data": self.__data__}

    def on_click(self, event=None):
        self.root.select_frame(self)

    def _render_(self):
        data = self.__data__

        new_frame = ctk.CTkFrame(self, corner_radius=15, border_width=2)
        new_frame.columnconfigure(0, weight=1)
        new_frame.rowconfigure(0, weight=1)

        if self.view_frame:
            self.view_frame.destroy()
            self.view_frame = None
        self.view_frame = new_frame
        self.view_frame.pack(fill='both', padx=2, pady=2)

        text = data["text"]
        text_frame = AutoWrappingCTkLabel(master=new_frame, text=text, font=('Arial', 20), justify='left', corner_radius=15)
        text_frame.grid(row=0, column=0, sticky='NSEW')
        text_frame.bind('<Double-Button-1>', self._edit_)
        text_frame.bind("<Button-1>", self.on_click)

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
        super().__init__(parent)
        self.bind("<Button-1>", self.on_click)
        self.configure()
        self.__data__ = data
        self.view_frame = None
        self.edit_frame = None
        self.answer_vars = []
        self._render_()  # rendering data
        self._open_()  # showing data

    def _import_(self) -> dict:
        return {"cell_type": "quiz", "data": self.__data__}

    def on_click(self, event=None):
        self.master.select_frame(self)

    def _render_(self):
        if self.view_frame:
            self.view_frame.pack_forget()

        data = self.__data__

        new_frame = ctk.CTkFrame(self, corner_radius=8, width=500, height=300)
        new_frame.columnconfigure(0, weight=1)
        new_frame.bind("<Button-1>", self.on_click)
        self.view_frame = new_frame
        self.view_frame.pack(fill='both', expand=True, pady=2, padx=2)

        # Display the question text
        question_text = data["text"]
        question_label = ctk.CTkLabel(new_frame, text=question_text, font=('Arial', 20))
        question_label.bind("<Button-1>", self.on_click)
        question_label.grid(row=0, column=0, sticky='W', padx=10, pady=5)

        # Display the answers with checkboxes
        answers = data.get("answers", [])
        self.answer_vars = []
        for idx, answer in enumerate(answers):
            answer_var = ctk.StringVar(value="")
            self.answer_vars.append(answer_var)
            answer_checkbox = ctk.CTkCheckBox(new_frame, text=answer, variable=answer_var, onvalue=answer, offvalue="",
                                              font=('Arial', 20))
            answer_checkbox.grid(row=idx + 1, column=0, padx=20, pady=2, sticky='W')

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

        new_frame = ctk.CTkScrollableFrame(self, corner_radius=8, border_width=2, width=500,
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
            result_color = "#00FF00"
        else:
            result_text = "Incorrect!"
            result_color = "#FF0000"

        # Display result
        result_label = ctk.CTkLabel(self.view_frame, text=result_text, font=('Arial', 20), text_color=result_color)
        result_label.grid(row=len(self.answer_vars) + 2, column=0, pady=10)


class FlashCard(ctk.CTkFrame):
    def __init__(self, parent, data):
        super().__init__(parent, fg_color='transparent')
        self.__data__ = data
        self.card_color = data["color"]

        self.current_side = 'front'  # Flag to track if currently showing back side

        # front side
        self.front_text = data["front"]
        self.front_label = AutoWrappingCTkLabel(self, text=self.front_text, font=('Arial', 20), width=225,
                                                height=300, fg_color=self.card_color, corner_radius=15)
        self.front_label.pack(fill='both', expand=True, padx=5, pady=5)
        self.front_label.bind('<Button-1>', self.flip)

        # back side  (initially hidden)
        self.back_text = data["back"]
        self.back_label = AutoWrappingCTkLabel(self, text=self.back_text, font=('Arial', 20), width=200,
                                               height=300, fg_color=self.card_color, corner_radius=15)
        self.back_label.bind('<Button-1>', self.flip)

    def flip(self, event=None):
        if self.current_side == 'front':
            self.front_label.pack_forget()
            self.back_label.pack(fill='both', expand=True, padx=5, pady=5)

        else:
            self.back_label.pack_forget()
            self.front_label.pack(fill='both', expand=True, padx=5, pady=5)

        self.current_side = 'front' if self.current_side == 'back' else 'back'


class FlashcardCell(ctk.CTkFrame, Cell):
    def __init__(self, parent, data):
        """
        :param data: [{"front": <front side text>, "back": <back side text>, "color": <color>}, ...]
        """
        super().__init__(parent, height=230)
        self.bind("<Double-Button-1>", self._edit_)
        self.bind("<Button-1>", self.on_click)
        self.__data__ = data

        self.view_frame = None
        self.edit_frame = None

        self._render_()  # Rendering data
        self._open_()  # Showing data

    def on_click(self, event=None):
        self.master.select_frame(self)

    def _import_(self) -> dict:
        return {"cell_type": "flash cards", "data": self.__data__}

    def _render_(self):

        if self.view_frame:  # deleting old frame
            self.view_frame.destroy()

        new_frame = ctk.CTkFrame(self, corner_radius=15, width=125, height=225)
        new_frame.bind("<Double-Button-1>", self._edit_)
        new_frame.bind("<Button-1>", self.on_click)
        self.view_frame = new_frame

        data = self.__data__
        self.cards = []

        for i, card_data in enumerate(data):
            self.cards.append(FlashCard(self.view_frame, card_data))
            self.cards[-1].grid(row=0, column=i, pady=2, padx=5, sticky='NS')

    def _open_(self):
        if self.edit_frame:
            self.edit_frame.destroy()

        self.view_frame.pack(fill='both', expand=True, pady=2, padx=2)

    def _edit_(self, event=None):
        pass

    def _save_(self, new_front, new_back):
        self.__data__["front"] = new_front
        self.__data__["back"] = new_back
        if self.edit_frame:
            self.edit_frame.destroy()
        self._render_()
        self._open_()

    def _delete_(self):
        self.parent.remove_flashcard(self)
        if self.edit_frame:
            self.edit_frame.destroy()


class Viewer(ctk.CTkScrollableFrame):

    def __init__(self, parent):
        super().__init__(parent)
        self.selected_frame: ctk.CTkFrame = None  # currently selected frame

        self.cells: List[Cell] = []
        self.__draw__()

    def shift_cell_down(self, event=None):
        if not self.selected_frame:
            return

        selected_index = self.cells.index(self.selected_frame)
        before, after = self.cells[:selected_index], self.cells[selected_index + 1:]
        if not after:
            return
        else:
            after.insert(1, self.selected_frame)
        self.cells = before + after
        self.__draw__()

    def shift_cell_up(self, event=None):
        if not self.selected_frame:
            return

        selected_index = self.cells.index(self.selected_frame)
        before, after = self.cells[:selected_index], self.cells[selected_index + 1:]
        if not before:
            return
        else:
            before.insert(-1, self.selected_frame)
        self.cells = before + after
        self.__draw__()

    def create_text_cell(self, event=None):
        if not self.selected_frame:
            self.cells.append(PlainTextCell(self, {"text": ""}))
            self.__draw__()
            return

        selected_index = self.cells.index(self.selected_frame)
        self.cells.insert(selected_index + 1, PlainTextCell(self, {"text": ""}))
        self.__draw__()
        return

    def create_quiz_cell(self, event=None):
        if not self.selected_frame:
            self.cells.append(QuizCell(self, {"text": "Question", "answers": ["A", "B", "C", "D"],
            "correct_answers": []}))
            self.__draw__()
            return

        selected_index = self.cells.index(self.selected_frame)
        self.cells.insert(selected_index + 1, QuizCell(self, {"text": "Question", "answers": ["A", "B", "C", "D"],
            "correct_answers": []}))
        self.__draw__()
        return

    def remove_cell(self, event=None):
        if not self.selected_frame:
            return

        selected_index = self.cells.index(self.selected_frame)
        msg_box = CTkMessagebox(title="Delete?", message="Do you want to delete this cell?",
                        icon="question", option_1="No", option_2="Yes")
        response = msg_box.get()
        if response == "Yes":
            self.selected_frame.grid_forget()
            self.selected_frame.destroy()
            self.cells.remove(self.selected_frame)
            self.selected_frame = None
        self.__draw__()
        return

    def create_img_cell(self, event=None):

        filename = ctk.filedialog.askopenfilename( title="Select a file",
                                                   filetypes=(("Image format", "*.png"), ("All files", "*.*")))

        if not self.selected_frame:
            self.cells.append(ImageCell(self, {"path": filename}))
            self.__draw__()
            return

        selected_index = self.cells.index(self.selected_frame)
        self.cells.insert(selected_index + 1, ImageCell(self, {"path": filename}))
        self.__draw__()
        return
    def __draw__(self):
        [cell.grid_forget() for cell in self.cells]
        for cell_num, cell in enumerate(self.cells):
            self.columnconfigure(0, weight=99)
            self.rowconfigure(0, weight=99)
            cell.grid(row=cell_num, column=0, sticky='WE', pady=5)

    def select_frame(self, frame: ctk.CTkFrame):
        if self.selected_frame:
            self.selected_frame.configure(border_width=0)  # unselect previous one ( delete boarding)
        self.selected_frame = frame

        frame.configure(border_width=2, border_color='#5584e0')

    def save_file(self, event=None):
        filename = ctk.filedialog.asksaveasfile().name
        if not filename:
            return

        file_data = []
        for cell in self.cells:
            file_data.append(cell._import_())

        with open(filename, 'w') as file:
            json.dump(file_data, file, indent=4)


class UpperMenu(ctk.CTkFrame):
    """
    frame with instruments for editing
    """

    def __init__(self, parent):
        super().__init__(parent, height=75)
        self.add_buttons()

    def add_buttons(self):
        viewer = self.master.viewer
        app = self.master

        load_texture = ctk.CTkImage(dark_image=Image.open('open.png'))
        self.open_button = ctk.CTkButton(self, image=load_texture, text="", width=32, fg_color='transparent')
        self.open_button.pack(side='left', fill='y')
        self.open_button.bind('<Button-1>', app.open_file)

        save_texture = ctk.CTkImage(dark_image=Image.open('save.png'))
        self.save_button = ctk.CTkButton(self, image=save_texture, text="", width=32, fg_color='transparent')
        self.save_button.pack(side='left', fill='y')
        self.save_button.bind('<Button-1>', viewer.save_file)

        trash_bin_texture = ctk.CTkImage(dark_image=Image.open('trash_bin.png'))
        self.delete_button = ctk.CTkButton(self, image=trash_bin_texture, text="", width=32, fg_color='transparent')
        self.delete_button.pack(side='right', fill='y')
        self.delete_button.bind('<Button-1>', viewer.remove_cell)

        down_arrow_texture = ctk.CTkImage(dark_image=Image.open('down_arrow.png'))
        self.down_arrow_button = ctk.CTkButton(self, image=down_arrow_texture, text="", width=32,
                                               fg_color='transparent')
        self.down_arrow_button.pack(side='right', fill='y')
        self.down_arrow_button.bind('<Button-1>', viewer.shift_cell_down)

        upper_arrow_texture = ctk.CTkImage(dark_image=Image.open('uppper_arrow.png'))
        self.upper_arrow_button = ctk.CTkButton(self, image=upper_arrow_texture, text="", width=32,
                                                fg_color='transparent')
        self.upper_arrow_button.pack(side='right', fill='y')
        self.upper_arrow_button.bind('<Button-1>', viewer.shift_cell_up)

        image_texture = ctk.CTkImage(dark_image=Image.open('image.png'))
        self.add_image_button = ctk.CTkButton(self, image=image_texture, text="", width=32, fg_color='transparent')
        self.add_image_button.pack(side='right', fill='y')
        self.add_image_button.bind('<Button-1>', viewer.create_img_cell)

        quiz_texture = ctk.CTkImage(dark_image=Image.open('quiz.png'))
        self.add_quiz_button = ctk.CTkButton(self, image=quiz_texture, text="", width=32, fg_color='transparent')
        self.add_quiz_button.pack(side='right', fill='y')
        self.add_quiz_button.bind('<Button-1>', viewer.create_quiz_cell)

        text_texture = ctk.CTkImage(dark_image=Image.open('text.png'))
        self.add_text_button = ctk.CTkButton(self, image=text_texture, text="", width=32, fg_color='transparent')
        self.add_text_button.pack(side='right', fill='y')
        self.add_text_button.bind('<Button-1>', viewer.create_text_cell)


class ImageCell(ctk.CTkFrame, Cell):

    def __init__(self, parent, data):
        """

        :param parent:
        :param data: {"path": <path to the image>}
        """
        super().__init__(parent)
        self.__data__ = data
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.view_frame: ctk.CTkImage = None
        self.edit_frame: ctk.CTkFrame = None

        self._render_()  # rendering data
        self._open_()  # showing data

    def _edit_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        pass

    def _open_(self) -> [ctk.CTkFrame, ctk.CTkScrollableFrame]:
        self.view_frame.grid(row=0, column=0, padx=3, pady=3, sticky="SWEN")

    def on_click(self, event=None):
        self.master.select_frame(self)

    def _render_(self):
        img = Image.open(self.__data__['path'])
        self.image_frame = ctk.CTkImage(dark_image=img, size=img.size)
        self.view_frame = ctk.CTkFrame(self)
        self.image_label = ctk.CTkLabel(self.view_frame, text="", image=self.image_frame)
        self.image_label.bind('<Button-1>', self.on_click)
        self.image_label.pack()

    def _save_(self):
        pass

    def _import_(self) -> dict:
        return {"cell_type": "image", "data": self.__data__}


class App(ctk.CTk):

    def __init__(self):
        self.window = super().__init__()

        # gridding viewer
        viewer_coords = (1, 0)
        self.grid_columnconfigure(viewer_coords[1], weight=14)
        self.grid_rowconfigure(viewer_coords[0], weight=50)
        self.viewer = Viewer(self)
        self.viewer.grid(row=viewer_coords[0], column=viewer_coords[1], sticky='SWEN')

        # gridding upper menu
        upper_menu_coords = (0, 0)
        self.grid_rowconfigure(upper_menu_coords[0], weight=2)
        self.grid_columnconfigure(upper_menu_coords[1], weight=1)
        self.upper_menu = UpperMenu(self)
        self.upper_menu.grid(row=upper_menu_coords[0], column=upper_menu_coords[1], columnspan=2, sticky='SWEN', pady=5)

    def open_file(self, event=None):
        filename = ctk.filedialog.askopenfilename( title="Select a file",
                                                   filetypes=(("Open interactive book format", "*.ibf"), ("All files", "*.*")))
        if not filename:
            return

        if not filename.split('.')[-1] == 'ibf':
            print('file must have .ibf extension')
            return

        # reading cells from file
        with open(filename, 'r') as file:
            try:
                file_data = json.load(file)
                loaded_cells: List[Cell] = []
                for cell in file_data:
                    cell_type = cell['cell_type']
                    cell_data = cell['data']
                    match cell_type:
                        case 'image':
                            loaded_cells.append(ImageCell(self.viewer, cell_data))
                        case 'plain text':
                            loaded_cells.append(PlainTextCell(self.viewer, cell_data))
                        case 'quiz':
                            loaded_cells.append(QuizCell(self.viewer, cell_data))
                        case 'flash cards':
                            loaded_cells.append(FlashcardCell(self.viewer, cell_data))

                # clearing viewer
                for cell in self.viewer.cells:
                    cell.grid_forget()
                    cell.destroy()
                self.viewer.selected_frame = None
                self.viewer.cells.clear()

                # adding cells from file data
                self.viewer.cells = loaded_cells
                self.viewer.__draw__()

            except Exception as e:
                print(f'got {e} while reading file {filename}')


if __name__ == '__main__':
    window = App()
    window.title("Open-IBF editor")
    window.minsize(800, 1100)
    window.mainloop()
