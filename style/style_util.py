import customtkinter as ctk

def center(widget):
    widget.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

def fill_screen(widget):
    widget.place(x=0, y=0, relwidth=1, relheight=1)