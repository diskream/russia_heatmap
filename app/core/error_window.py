import tkinter as tk
import tkinter.ttk as ttk


class TopErrorWindow(tk.Toplevel):
    def __init__(self, *, title, message, detail, ok_callable = None, detail_btn_text='Detail'):
        tk.Toplevel.__init__(self)
        self.details_expanded = False
        self.title(title)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.ok_callable = ok_callable

        button_frame = tk.Frame(self)
        button_frame.grid(row=0, column=0, sticky='nsew')
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)

        text_frame = tk.Frame(self)
        text_frame.grid(row=1, column=0, padx=(7, 7), pady=(7, 7), sticky='nsew')
        text_frame.rowconfigure(0, weight=1)
        text_frame.columnconfigure(0, weight=1)

        ttk.Label(button_frame, text=message).grid(row=0, column=0, columnspan=2, pady=(7, 7))
        ttk.Button(
            button_frame,
            text='Открыть карту',
            command=self._call_and_destroy,
            state='enabled' if self.ok_callable else 'disabled',
        ).grid(row=1, column=0)
        ttk.Button(button_frame, text='Выйти', command=self.destroy).grid(row=1, column=1)
        ttk.Button(button_frame, text=detail_btn_text, command=self.toggle_details).grid(row=2, column=0, columnspan=2)

        self.textbox = tk.Text(text_frame, height=6)
        self.textbox.insert('1.0', detail)
        self.textbox.config(state='disabled')
        self.scrollb = tk.Scrollbar(text_frame, command=self.textbox.yview)
        self.textbox.config(yscrollcommand=self.scrollb.set)

    def _call_and_destroy(self):
        if self.ok_callable:
            self.ok_callable()
        self.destroy()

    def toggle_details(self):
        if self.details_expanded:
            self.textbox.grid_forget()
            self.scrollb.grid_forget()
            self.geometry('350x75')
            self.details_expanded = False
        else:
            self.textbox.grid(row=0, column=0, sticky='nsew')
            self.scrollb.grid(row=0, column=1, sticky='nsew')
            self.geometry('350x160')
            self.details_expanded = True