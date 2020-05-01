from tkinter import *

class GUI:

    def __init__(self):
        self.login = LoginWindow()

class MainWindow:

    def __init__(self):
        self.window = Tk()
        self.window.title("potatofy")

class LoginWindow:

    def __init__(self):
        self.window = Tk()
        self.window.title("potatofy")
        # self.window.geometry('300x150')
        # self.window.resizable(False, False)
        # Grid.rowconfigure(self.window, 0,weight=1)
        # Grid.columnconfigure(self.window, 0, weight=1)
        Label(self.window, text="Log in to Questrade").grid(row=0, columnspan=2, pady=3)

        Label(self.window, text="User ID").grid(row=1, column=0, pady=1)
        user = StringVar()
        Entry(self.window, textvariable=user).grid(row=1, column=1, pady=1)

        Label(self.window, text="Password").grid(row=2, column=0, pady=1)
        password = StringVar()
        Entry(self.window, textvariable=password, show="*").grid(row=2, column=1, pady=1)

        Button(self.window, text="Log In").grid(row=3, columnspan=2, pady=3)
        self.window.mainloop()
