import tkinter as tk
from Rebalancer import Rebalancer
from Portfolio import Portfolio
from Broker import Broker

from AuthException import AuthException


class Main:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.frame = tk.Frame(self.parent)
        self.init_start_window()
        self.positions = {}

    def init_start_window(self):
        self.frame.pack()
        # TODO: center items
        tk.Label(self.frame, text="potatofy").pack()
        tk.Button(self.frame, text="Load Portfolio", command=self.load_holdings).pack()
        tk.Button(self.frame, text="Log in", command=self.open_login_window).pack()

    def open_login_window(self):
        self.new_window = Login(self.frame, self.potatofy)

    def load_holdings(self):
        self.frame.destroy()
        new_frame = Holdings(self.parent, self.potatofy)
        self.frame = new_frame

    def auth_error_prompt(self):
        self.new_window = AuthError(self.parent, self.potatofy)


class Holdings:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.positions = {}
        self.frame = tk.Frame(self.parent)
        self.frame.grid()
        self.init_control_bar()
        self.refresh_portfolio()
        self.add_headings()
        self.add_positions()
        self.add_totals()
        self.set_grid_size()

    def set_grid_size(self):
        size = self.frame.grid_size()
        for i in size:
            self.frame.grid_columnconfigure(i, minsize=50)

    def refresh_portfolio(self):
        try:
            self.potatofy.portfolio.load_accounts()
        except AuthException:
            self.auth_error_prompt()

    def init_control_bar(self):
        tk.Label(self.frame, text="Portfolio Holdings").grid(row=0, column=0, columnspan=4, ipadx=20, sticky=tk.W)
        tk.Button(self.frame, text="Refresh Portfolio", command=self.refresh_portfolio).grid(row=0, column=6)
        tk.Button(self.frame, text="Log in", command=self.open_login_window).grid(row=0, column=7)

    def auth_error_prompt(self):
        self.new_window = AuthError(self.parent, self.potatofy)

    def open_login_window(self):
        self.new_window = Login(self.frame, self.potatofy)

    def add_headings(self):
        tk.Label(self.frame, text="Holding").grid(row=1, column=0)
        tk.Label(self.frame, text="Amount ($)").grid(row=1, column=1)
        tk.Label(self.frame, text="Allocation (%)").grid(row=1, column=2)
        tk.Label(self.frame, text="Target Allocation (%)").grid(row=1, column=3)
        tk.Label(self.frame, text="Target Amount ($)").grid(row=1, column=4)
        tk.Label(self.frame, text="Difference").grid(row=1, column=5)
        tk.Label(self.frame, text="Price Per Share").grid(row=1, column=6)
        tk.Label(self.frame, text="Shares to Buy/Sell").grid(row=1, column=7)
        tk.Label(self.frame, text="Add").grid(row=1, column=8)

    def add_positions(self):
        # TODO: fix alignment of positions
        for ticker, amount in self.potatofy.portfolio.get_all_positions().items():
            self.positions[ticker] = Position(self.frame, ticker, amount, self.potatofy)

    def add_totals(self):
        size = self.frame.grid_size()
        tk.Label(self.frame, text="Total Holdings").grid(row=size[0], column=0)
        tk.Label(self.frame, text=self.potatofy.portfolio.get_total_holdings()).grid(row=size[0], column=1, sticky=tk.E)
        # Button(self.window, text="Rebalance", command=self.rebalance).grid(row=size[0], column=7)

    # def rebalance(self):


class Position:

    def __init__(self, parent, ticker, amount, potatofy):
        self.parent = parent
        self.ticker = ticker
        self.amount = amount
        self.potatofy = potatofy
        self.frame = tk.Frame(self.parent)
        self.frame.grid()
        self.add_data()

    def add_data(self):
        self.add_holding_ticker(self.ticker)
        self.add_holding_amount(self.amount)
        self.add_allocation(self.amount)
        self.add_target_alloc()

    def add_holding_ticker(self, holding):
        tk.Label(self.frame, text=holding).grid(row=0, column=0)

    def add_holding_amount(self, amount):
        tk.Label(self.frame, text=amount).grid(row=0, column=1, sticky=tk.E)

    def add_allocation(self, amount):
        allocation = amount / self.potatofy.portfolio.get_total_holdings() * 100
        tk.Label(self.frame, text=round(allocation, 1)).grid(row=0, column=2, sticky=tk.E)

    def add_target_alloc(self):
        target = tk.StringVar()
        tk.Entry(self.frame, textvariable=target).grid(row=0, column=3)


class Login:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.frame = tk.Toplevel(self.parent)
        self.add_labels()
        tk.Label(self.frame)

    def add_labels(self):
        tk.Label(self.frame, text="Log in to Questrade").grid(row=0, columnspan=2, pady=3)

        tk.Label(self.frame, text="User ID").grid(row=1, column=0, pady=1, sticky=tk.E)
        username = tk.StringVar()
        tk.Entry(self.frame, textvariable=username).grid(row=1, column=1, pady=1)

        tk.Label(self.frame, text="Password").grid(row=2, column=0, pady=1, sticky=tk.E)
        password = tk.StringVar()
        tk.Entry(self.frame, textvariable=password, show="*").grid(row=2, column=1, pady=1)

        tk.Button(self.frame, text="Log In",
                  command=lambda: self.login(username.get(), password.get())).grid(row=3, columnspan=2, pady=3)

    def login(self, username, password):
        question = self.potatofy.broker.authenticate(username, password)
        self.new_window = Security(self, self.potatofy, question)


class Security:

    def __init__(self, parent, potatofy, question):
        self.parent = parent
        self.potatofy = potatofy
        self.question = question
        self.frame = tk.Toplevel(self.parent.frame)
        self.add_labels()
        tk.Label(self.frame)

    def add_labels(self):
        tk.Label(self.frame, text="Security Question").pack()

        tk.Label(self.frame, text=self.question).pack()
        answer = tk.StringVar()
        tk.Entry(self.frame, textvariable=answer, show="*").pack()

        tk.Button(self.frame, text="Submit", command=lambda: self.two_factor(answer.get())).pack()

    def two_factor(self, answer):
        try:
            self.potatofy.broker.authenticate_two_factor(answer)
            self.parent.frame.destroy()
        except AuthException:
            self.new_window = AuthError(self.parent, self.potatofy)
        else:
            self.frame.destroy()


class AuthError:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.frame = tk.Toplevel(self.parent)
        self.frame.title('Error')
        tk.Label(self.frame, text="Failed to authenticate your account.\nPlease log in.").grid(row=0, pady=3)
        tk.Button(self.frame, text="Ok", command=lambda: self.prompt_login()).grid(row=1, pady=3)

    def prompt_login(self):
        self.new_window = Login(self.parent, self.potatofy)
        self.frame.destroy()


class Potatofy:

    def __init__(self, parent, broker, portfolio, rebalancer):
        self.parent = parent
        self.main = Main(self.parent, self)
        self.broker = broker
        self.portfolio = portfolio
        self.rebalancer = rebalancer
        self.init_root()

    def init_root(self):
        self.parent.title("potatofy")
        self.parent.minsize(400, 300)


def main():
    root = tk.Tk()
    broker = Broker()
    portfolio = Portfolio(broker)
    rebalancer = Rebalancer(portfolio)
    Potatofy(root, broker, portfolio, rebalancer)
    root.mainloop()


if __name__ == "__main__":
    main()