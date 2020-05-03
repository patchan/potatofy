import tkinter as tk
from PIL import Image, ImageTk
from Rebalancer import Rebalancer
from Portfolio import Portfolio
from Broker import Broker

from Error.AuthError import AuthError
from Error.LoginError import LoginError


class Main:

    def __init__(self, root, potatofy):
        self.parent = root
        self.potatofy = potatofy
        self.frame = tk.Frame(self.parent)
        self.init_start_window()
        self.positions = {}

    def init_start_window(self):
        self.frame.pack(expand=True, pady=50, padx=50)
        self.parent.minsize(350, 350)
        tk.Label(self.frame, text="potatofy").pack(pady=20)
        tk.Button(self.frame, text="Load Portfolio", command=self.load_holdings).pack(pady=10)
        tk.Button(self.frame, text="Log in", command=self.open_login_window).pack(pady=10)

    def open_login_window(self):
        self.new_window = Login(self, self.potatofy)

    def load_holdings(self):
        self.frame.destroy()
        new_frame = Holdings(self.parent, self.potatofy)
        self.frame = new_frame

    def auth_error_prompt(self):
        self.new_window = Authenticate(self, self.potatofy)


class Holdings:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.positions = {}
        self.frame = tk.Frame(self.parent, padx=30, pady=30)
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
        except Authenticate:
            self.auth_error_prompt()

    def init_control_bar(self):
        tk.Label(self.frame, text="Portfolio Holdings").grid(row=0, column=0, columnspan=4, ipadx=20, sticky=tk.W)
        tk.Button(self.frame, text="Refresh Portfolio", command=self.refresh_portfolio).grid(row=0, column=6)
        tk.Button(self.frame, text="Log in", command=self.open_login_window).grid(row=0, column=7)

    def auth_error_prompt(self):
        self.new_window = Authenticate(self, self.potatofy)

    def open_login_window(self):
        self.new_window = Login(self, self.potatofy)

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
            self.positions[ticker] = Position(self, ticker, amount, self.potatofy)

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
        self.frame = tk.Frame(self.parent.frame)
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
        self.frame = tk.Toplevel(self.parent.frame, width=250, height=250, padx=20, pady=20)
        self.frame.resizable(False, False)
        self.add_labels()
        tk.Label(self.frame)

    def add_labels(self):
        icon = ImageTk.PhotoImage(Image.open('./icons/Questrade.png').resize((209, 75)))
        img_label = tk.Label(self.frame, image=icon)
        img_label.image = icon
        img_label.grid(row=0, columnspan=2, pady=5)

        tk.Label(self.frame, text="Please authenticate your Questrade account.", anchor='center').grid(row=1, columnspan=2, pady=3)

        tk.Label(self.frame, text="User ID").grid(row=2, column=0, pady=1, sticky=tk.E)
        username = tk.StringVar()
        tk.Entry(self.frame, textvariable=username).grid(row=2, column=1, pady=1)

        tk.Label(self.frame, text="Password").grid(row=3, column=0, pady=1, sticky=tk.E)
        password = tk.StringVar()
        tk.Entry(self.frame, textvariable=password, show="*").grid(row=3, column=1, pady=1)

        tk.Button(self.frame, text="Log In",
                  command=lambda: self.login(username.get(), password.get())).grid(row=4, columnspan=2, pady=3)

    def login(self, username, password):
        try:
            question = self.potatofy.broker.authenticate(username, password)
            self.new_window = Security(self, self.potatofy, question)
        except LoginError:
            tk.Label(self.frame, text="Invalid username or password. Please try again.", fg='red').grid(row=5, columnspan=2)
        except:
            self.new_window = Authenticate(self, self.potatofy)

    def login_success(self):
        self.frame.destroy()
        self.frame = Success(self.parent)


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
            self.parent.login_success()
        except AuthError:
            self.new_window = Authenticate(self.parent, self.potatofy)
        else:
            self.frame.destroy()


class Authenticate:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.frame = tk.Toplevel(self.parent.frame)
        self.frame.title('Error')
        tk.Label(self.frame, text="Failed to authenticate your account.\nPlease log in.").grid(row=0, pady=3)
        tk.Button(self.frame, text="Ok", command=lambda: self.prompt_login()).grid(row=1, pady=3)

    def prompt_login(self):
        self.new_window = Login(self, self.potatofy)
        self.frame.destroy()


class Success:

    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Toplevel(self.parent.frame)
        self.frame.title('potatofy')
        tk.Label(self.frame, text='Success!').pack()
        tk.Button(self.frame, text="Ok", command=self.confirm).pack()

    def confirm(self):
        self.parent.load_holdings()
        self.frame.destroy()


class Potatofy:

    def __init__(self, root, broker, portfolio, rebalancer):
        self.parent = root
        self.main = Main(self.parent, self)
        self.broker = broker
        self.portfolio = portfolio
        self.rebalancer = rebalancer
        self.init_root()

    def init_root(self):
        self.parent.title("potatofy")


if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    portfolio = Portfolio(broker)
    rebalancer = Rebalancer(portfolio)
    Potatofy(root, broker, portfolio, rebalancer)
    root.mainloop()
