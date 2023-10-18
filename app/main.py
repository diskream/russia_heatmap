import tkinter as tk

from app.core.init_dialog_frame import DialogFrame


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Тепловая карта Российской Федерации")

        self.table_list_frame = DialogFrame(self)
        self.table_list_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)


if __name__ == "__main__":
    app = App()
    app.mainloop()
