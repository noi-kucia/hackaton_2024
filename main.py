import customtkinter as ctk


class App(ctk.CTk):

    def __init__(self):
        self.window = super().__init__()


if __name__ == '__main__':
    window = App()
    window.title("hackaton")
    window.mainloop()
