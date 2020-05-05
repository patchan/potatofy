import tkinter as tk
from _tkinter import TclError

from PIL import Image, ImageTk
from Rebalancer import Rebalancer
from Portfolio import Portfolio
from Broker import Broker

from Error.AuthError import AuthError
from Error.LoginError import LoginError


class Main:

    def __init__(self, potatofy):
        self.parent = potatofy.parent
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
        self.parent.minsize(0, 0)
        self.frame = tk.Frame(self.parent, padx=30, pady=25)
        self.frame.grid()
        self.rebalancing = tk.Frame(self.frame)
        self.cash = tk.Label(self.frame)
        self.init_control_bar()
        self.refresh_portfolio()
        self.add_headings()
        self.add_positions()
        self.add_totals()
        self.add_cash()
        self.add_rebalance()

    def refresh_portfolio(self):
        try:
            self.potatofy.portfolio.load_accounts()
        except Authenticate:
            self.auth_error_prompt()

    def init_control_bar(self):
        self.control = tk.Frame(self.frame)
        pady = 10
        self.control.grid(row=0, columnspan=3, pady=pady, sticky=tk.W)
        # TODO: fix refreshing behaviour
        tk.Button(self.control, text="Refresh Portfolio", command=self.refresh_portfolio).grid(row=0, column=0)
        tk.Button(self.control, text="Log in", command=self.open_login_window).grid(row=0, column=1)

    def auth_error_prompt(self):
        self.new_window = Authenticate(self, self.potatofy)

    def open_login_window(self):
        self.new_window = Login(self, self.potatofy)

    def add_headings(self):
        tk.Label(self.frame, text="Holding").grid(row=1, column=0)
        tk.Label(self.frame, text="Amount ($)").grid(row=1, column=1, sticky=tk.E)
        tk.Label(self.frame, text="Allocation (%)").grid(row=1, column=2, sticky=tk.E)
        # tk.Label(self.frame, text="Target Allocation (%)").grid(row=1, column=3)
        # tk.Label(self.frame, text="Target Amount ($)").grid(row=1, column=4)
        # tk.Label(self.frame, text="Difference").grid(row=1, column=5)
        # tk.Label(self.frame, text="Price Per Share").grid(row=1, column=6)
        # tk.Label(self.frame, text="Shares to Buy/Sell").grid(row=1, column=7)
        # tk.Label(self.frame, text="Add").grid(row=1, column=8)

    def add_positions(self):
        row = self.frame.grid_size()[1]
        for ticker, amount in self.potatofy.portfolio.get_all_positions().items():
            row += 1
            self.positions[ticker] = Position(self, ticker, amount, self.potatofy, row)

    def add_totals(self):
        size = self.frame.grid_size()[1]
        tk.Label(self.frame, text="Total Holdings").grid(row=size+1, column=0)
        tk.Label(self.frame, text=round(self.get_holdings(), 2)).grid(row=size+1, column=1, sticky=tk.E)

    def get_holdings(self):
        return self.potatofy.portfolio.get_total_holdings()

    def get_cash(self):
        return self.potatofy.portfolio.get_cash()

    def add_cash(self):
        size = self.frame.grid_size()[1]
        pady = 3
        tk.Label(self.frame, text="Cash").grid(row=size+1, column=0, pady=pady)
        self.cash.config(text=self.potatofy.portfolio.get_cash())
        self.cash.grid(row=size+1, column=1, sticky=tk.E, pady=pady)
        tk.Button(self.frame, text="Add cash", command=self.add_new_cash).grid(row=size+1, column=2, pady=pady, sticky=tk.E)

    def add_new_cash(self):
        self.new_window = Cash(self, self.potatofy)

    def add_rebalance(self):
        size = self.frame.grid_size()[1]
        tk.Button(self.frame, text="Rebalance", command=self.rebalance).grid(row=size+1, column=2, pady=5, sticky=tk.E)

    def rebalance(self):
        self.new_window = Rebalance(self, self.potatofy)

    def add_rebalancing(self, shares):
        self.rebalancing.destroy()
        self.rebalancing = tk.Frame(self.frame)
        self.rebalancing.grid(columnspan=3)
        tk.Label(self.rebalancing, text='Ticker').grid(row=0, column=0)
        tk.Label(self.rebalancing, text='Shares to Purchase').grid(row=0, column=1)
        tk.Label(self.rebalancing, text='Price per share').grid(row=0, column=2)
        tk.Label(self.rebalancing, text='Target Amount ($)').grid(row=0, column=3)
        tk.Label(self.rebalancing, text='Target Allocation (%)').grid(row=0, column=4)
        row = 1
        for ticker, amount in shares.items():
            tk.Label(self.rebalancing, text=ticker).grid(row=row, column=0)
            tk.Label(self.rebalancing, text=amount).grid(row=row, column=1)
            row += 1


class Rebalance:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.frame = tk.Toplevel(self.parent.frame, pady=20, padx=20)
        self.potatofy = potatofy
        self.inputs = {}
        self.init_rebalance()

    def init_rebalance(self):
        self.frame.grid()
        self.add_headings()
        self.add_positions()
        self.add_confirmation()

    def add_headings(self):
        tk.Label(self.frame, text="Holding").grid(row=0, column=0)
        tk.Label(self.frame, text="Target Allocation (%)").grid(row=0, column=1, sticky=tk.E)

    def add_positions(self):
        row = self.frame.grid_size()[1]
        for ticker in self.potatofy.portfolio.get_all_positions():
            row += 1
            tk.Label(self.frame, text=ticker).grid(row=row, column=0)
            allocation = tk.DoubleVar()
            self.inputs[ticker] = allocation
            tk.Entry(self.frame, textvariable=allocation, justify=tk.RIGHT).grid(row=row, column=1)

    def get_total_alloc(self):
        total = 0
        for ticker, alloc in self.inputs.items():
            total += alloc.get()
        return total

    def add_confirmation(self):
        size = self.frame.grid_size()[1]
        tk.Button(self.frame, text="Confirm", command=self.rebalance).grid(row=size+1, columnspan=2, pady=5)

    def rebalance(self):
        for ticker, alloc in self.inputs.items():
            self.potatofy.rebalancer.set_target_alloc(ticker, round(alloc.get(), 1))
        result = self.potatofy.rebalance()
        if result is not False:
            self.parent.add_rebalancing(result)
            self.frame.destroy()
        else:
            size = self.frame.grid_size()[1]
            total = self.get_total_alloc()
            tk.Label(self.frame, text="The total assigned target allocation is " + str(total) + "%.\nPlease try again.", fg='red').grid(row=size+1, columnspan=2)


class Cash:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.frame = tk.Toplevel(self.parent.frame)
        self.init_add_cash()

    def init_add_cash(self):
        tk.Label(self.frame, text='How much cash do you want to add?').grid(row=0, pady=3)
        cash = tk.IntVar()
        tk.Entry(self.frame, textvariable=cash, justify=tk.RIGHT).grid(row=1, pady=3)
        tk.Button(self.frame, text="Add", command=lambda: self.add_cash(cash)).grid(row=3, pady=3)

    def add_cash(self, cash_var):
        try:
            cash = cash_var.get()
            self.potatofy.portfolio.add_cash(cash)
            self.update_parent_cash_label()
            self.frame.destroy()
        except TclError:
            tk.Label(self.frame, text='Please enter a valid number.', fg='red').grid(row=4, pady=3)

    def update_parent_cash_label(self):
        self.parent.cash.config(text=round(self.potatofy.portfolio.get_cash(), 2))


class Position:

    def __init__(self, parent, ticker, amount, potatofy, index):
        self.parent = parent
        self.ticker = ticker
        self.amount = amount
        self.potatofy = potatofy
        self.index = index
        self.frame = self.parent.frame
        self.frame.grid()
        self.add_data()

    def add_data(self):
        self.add_holding_ticker(self.ticker)
        self.add_holding_amount(self.amount)
        self.add_allocation(self.amount)
        # self.add_target_alloc()

    def add_holding_ticker(self, holding):
        tk.Label(self.frame, text=holding).grid(row=self.index, column=0)

    def add_holding_amount(self, amount):
        tk.Label(self.frame, text=amount).grid(row=self.index, column=1, sticky=tk.E)

    def add_allocation(self, amount):
        allocation = amount / self.potatofy.portfolio.get_total_holdings() * 100
        tk.Label(self.frame, text=round(allocation, 1)).grid(row=self.index, column=2, sticky=tk.E)

    # def add_target_alloc(self):
    #     target = tk.StringVar()
    #     tk.Entry(self.frame, textvariable=target).grid(row=0, column=3)


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
        self.frame = Main(self)
        self.broker = broker
        self.portfolio = portfolio
        self.rebalancer = rebalancer
        self.init_root()

    def init_root(self):
        self.parent.title("potatofy")

    def get_broker(self):
        return self.broker

    def get_portfolio(self):
        return self.portfolio

    def rebalance(self):
        return self.rebalancer.calculate_purchases()


if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    portfolio = Portfolio(broker)
    rebalancer = Rebalancer(portfolio)
    Potatofy(root, broker, portfolio, rebalancer)
    root.mainloop()
