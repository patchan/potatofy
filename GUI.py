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
        self.init_main_window()

    def init_main_window(self):
        tk.Label(self.frame, text="Portfolio Holdings").grid(row=0, column=0, columnspan=4, ipadx=20, sticky=tk.W)
        tk.Button(self.frame, text="Load Portfolio", command=self.update_portfolio).grid(row=0, column=6)
        tk.Button(self.frame, text="Log in", command=self.open_login_window).grid(row=0, column=7)
        size = self.frame.grid_size()
        for i in size:
            self.frame.grid_columnconfigure(i, minsize=50)

    def open_login_window(self):
        self.new_window = Login(self.frame, self.potatofy)

    def update_portfolio(self):
        try:
            self.potatofy.portfolio.load_accounts()
        except AuthException:
            self.auth_error_prompt()
        tk.Label(self.frame, text="Holding").grid(row=1, column=0)
        tk.Label(self.frame, text="Amount ($)").grid(row=1, column=1)
        tk.Label(self.frame, text="Allocation (%)").grid(row=1, column=2)
        tk.Label(self.frame, text="Target Allocation (%)").grid(row=1, column=3)
        tk.Label(self.frame, text="Target Amount ($)").grid(row=1, column=4)
        tk.Label(self.frame, text="Difference").grid(row=1, column=5)
        tk.Label(self.frame, text="Price Per Share").grid(row=1, column=6)
        tk.Label(self.frame, text="Shares to Buy/Sell").grid(row=1, column=7)
        tk.Label(self.frame, text="Add").grid(row=1, column=8)
        row = 2
        for ticker, amount in self.potatofy.portfolio.get_all_positions().items():
            self.add_holding_ticker(self.frame, ticker, row)
            self.add_holding_amount(self.frame, amount, row)
            self.add_allocation(self.frame, amount, row)
            self.add_target_alloc(self.frame, row)
            row += 1
        self.add_totals()

    def auth_error_prompt(self):
        self.new_window = AuthError(self.parent, self.potatofy)

    def add_holding_ticker(self, window, holding, row):
        tk.Label(window, text=holding).grid(row=row, column=0)

    def add_holding_amount(self, window, amount, row):
        tk.Label(window, text=amount).grid(row=row, column=1, sticky=tk.E)

    def add_allocation(self, window, amount, row):
        allocation = amount / self.potatofy.portfolio.get_total_holdings() * 100
        tk.Label(window, text=round(allocation, 1)).grid(row=row, column=2, sticky=tk.E)

    def add_target_alloc(self, window, row):
        target = tk.StringVar()
        tk.Entry(window, textvariable=target).grid(row=row, column=3)

    def add_totals(self):
        size = self.frame.grid_size()
        tk.Label(self.frame, text="Total Holdings").grid(row=size[0], column=0)
        tk.Label(self.frame, text=self.potatofy.portfolio.get_total_holdings()).grid(row=size[0], column=1, sticky=tk.E)
        # Button(self.window, text="Rebalance", command=self.rebalance).grid(row=size[0], column=7)

    # def rebalance(self):


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
        self.init_main()

    def init_root(self):
        self.parent.title("potatofy")
        self.parent.minsize(400, 300)

    def init_main(self):
        self.main.frame.grid()


def main():
    root = tk.Tk()
    broker = Broker()
    portfolio = Portfolio(broker)
    rebalancer = Rebalancer(portfolio)
    Potatofy(root, broker, portfolio, rebalancer)
    root.mainloop()


if __name__ == "__main__":
    main()