from tkinter import *
from Portfolio import Portfolio


class GUI:

    def __init__(self):
        self.portfolio = Portfolio()
        self.window = Tk()
        self.window.title("potatofy")
        Label(self.window, text="Portfolio Holdings").grid(row=0, column=0, columnspan=4, ipadx=20, sticky=W)
        Button(self.window, text="Refresh Portfolio", command=self.update_portfolio).grid(row=0, column=6)
        Button(self.window, text="Log in", command=self.login_window).grid(row=0, column=7)
        size = self.window.grid_size()
        for i in size:
            self.window.grid_columnconfigure(i, minsize=50)
        self.window.mainloop()

    def update_portfolio(self):
        self.portfolio.register_accounts()
        Label(self.window, text="Holding").grid(row=1, column=0)
        Label(self.window, text="Amount").grid(row=1, column=1)
        Label(self.window, text="Current Allocation").grid(row=1, column=2)
        Label(self.window, text="Target Allocation").grid(row=1, column=3)
        Label(self.window, text="Target Amount").grid(row=1, column=4)
        Label(self.window, text="Difference").grid(row=1, column=5)
        Label(self.window, text="Price Per Share").grid(row=1, column=6)
        Label(self.window, text="Shares to Purchase/Sell").grid(row=1, column=7)
        row = 2
        for ticker, amount in self.portfolio.get_all_positions().items():
            self.add_holding_ticker(self.window, ticker, row)
            self.add_holding_amount(self.window, amount, row)
            self.add_allocation(self.window, amount, row)
            self.add_target_alloc(self.window, row)
            row += 1
        self.add_totals()

    def add_holding_ticker(self, window, holding, row):
        Label(window, text=holding).grid(row=row, column=0)

    def add_holding_amount(self, window, amount, row):
        Label(window, text=amount).grid(row=row, column=1, sticky=E)

    def add_allocation(self, window, amount, row):
        allocation = amount / self.portfolio.get_total_holdings() * 100
        Label(window, text=round(allocation, 1)).grid(row=row, column=2, sticky=E)

    def add_target_alloc(self, window, row):
        target = StringVar()
        Entry(window, textvariable=target).grid(row=row, column=3)

    def add_totals(self):
        size = self.window.grid_size()
        Label(self.window, text="Total Holdings").grid(row=size[0], column=0)
        Label(self.window, text=self.portfolio.get_total_holdings()).grid(row=size[0], column=1, sticky=E)

    def login_window(self):
        login_window = Toplevel(self.window)
        login_window.title("potatofy")
        Label(login_window, text="Log in to Questrade").grid(row=0, columnspan=2, pady=3)

        Label(login_window, text="User ID").grid(row=1, column=0, pady=1, sticky=E)
        username = StringVar()
        Entry(login_window, textvariable=username).grid(row=1, column=1, pady=1)

        Label(login_window, text="Password").grid(row=2, column=0, pady=1, sticky=E)
        password = StringVar()
        Entry(login_window, textvariable=password, show="*").grid(row=2, column=1, pady=1)

        Button(login_window, text="Log In", command=self.login).grid(row=3, columnspan=2, pady=3)

    def login(self):
        usr = username.get()
        pw = password.get()
        self.portfolio.get_broker().authenticate(usr, pw)
