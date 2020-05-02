from tkinter import *

from AuthException import AuthException


class GUI:

    def __init__(self, broker, portfolio, rebalancer):
        self.broker = broker
        self.portfolio = portfolio
        self.rebalancer = rebalancer
        self.window = Tk()
        self.init_main_window()

    def init_main_window(self):
        self.window.title("potatofy")
        Label(self.window, text="Portfolio Holdings").grid(row=0, column=0, columnspan=4, ipadx=20, sticky=W)
        Button(self.window, text="Load Portfolio", command=self.update_portfolio).grid(row=0, column=6)
        Button(self.window, text="Log in", command=self.login_window).grid(row=0, column=7)
        size = self.window.grid_size()
        for i in size:
            self.window.grid_columnconfigure(i, minsize=50)
        self.window.mainloop()

    def update_portfolio(self):
        try:
            self.portfolio.load_accounts()
        except AuthException:
            self.auth_error()
        Label(self.window, text="Holding").grid(row=1, column=0)
        Label(self.window, text="Amount ($)").grid(row=1, column=1)
        Label(self.window, text="Allocation (%)").grid(row=1, column=2)
        Label(self.window, text="Target Allocation (%)").grid(row=1, column=3)
        Label(self.window, text="Target Amount ($)").grid(row=1, column=4)
        Label(self.window, text="Difference").grid(row=1, column=5)
        Label(self.window, text="Price Per Share").grid(row=1, column=6)
        Label(self.window, text="Shares to Buy/Sell").grid(row=1, column=7)
        Label(self.window, text="Add").grid(row=1, column=8)
        row = 2
        for ticker, amount in self.portfolio.get_all_positions().items():
            self.add_holding_ticker(self.window, ticker, row)
            self.add_holding_amount(self.window, amount, row)
            self.add_allocation(self.window, amount, row)
            self.add_target_alloc(self.window, row)
            row += 1
        self.add_totals()

    def auth_error(self):
        auth_err = Toplevel(self.window)
        auth_err.title("Error")
        Label(auth_err, text="Failed to authenticate your account.\nPlease log in.").grid(row=0, pady=3)
        Button(auth_err, text="Ok", command=lambda: self.prompt_login(auth_err)).grid(row=1, pady=3)

    def prompt_login(self, auth_err):
        auth_err.destroy()
        self.login_window()

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
        # Button(self.window, text="Rebalance", command=self.rebalance).grid(row=size[0], column=7)

    # def rebalance(self):
        # self.rebalancer

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

        Button(login_window, text="Log In", command=lambda: self.login(username.get(), password.get(), login_window)).grid(row=3, columnspan=2, pady=3)

    def login(self, username, password, window):
        self.security_check(self.broker.authenticate(username, password), window)

    def security_check(self, question, window):
        window = Toplevel(window)
        window.title("potatofy")
        Label(window, text="Security Question").pack()

        Label(window, text=question).pack()
        answer = StringVar()
        Entry(window, textvariable=answer, show="*").pack()

        Button(window, text="Submit", command=lambda: self.two_factor(answer.get(), window)).pack()

    def two_factor(self, answer, window):
        window.destroy()
        try:
            self.broker.authenticate_two_factor(answer)
        except AuthException:
            self.auth_error()
