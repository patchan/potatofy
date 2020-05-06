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
        self.positions = {}
        self.init()

    def init(self):
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
        self.setup_headings()
        self.setup_positions()
        self.setup_totals()
        self.setup_cash()
        self.setup_rebalance()

    def refresh_portfolio(self):
        try:
            self.potatofy.load_accounts()
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

    def setup_headings(self):
        tk.Label(self.frame, text="Holding").grid(row=1, column=0)
        tk.Label(self.frame, text="Amount ($)").grid(row=1, column=1, sticky=tk.E)
        tk.Label(self.frame, text="Allocation (%)").grid(row=1, column=2, sticky=tk.E)

    def setup_positions(self):
        row = self.frame.grid_size()[1]
        for ticker, amount in self.potatofy.portfolio.get_all_positions().items():
            row += 1
            self.positions[ticker] = Position(self, ticker, amount, self.potatofy, row)

    def setup_totals(self):
        size = self.frame.grid_size()[1]
        tk.Label(self.frame, text="Total Holdings").grid(row=size+1, column=0)
        tk.Label(self.frame, text=round(self.get_holdings(), 2)).grid(row=size+1, column=1, sticky=tk.E)

    def get_holdings(self):
        return self.potatofy.portfolio.get_total_holdings()

    def get_cash(self):
        return self.potatofy.portfolio.get_cash()

    def setup_cash(self):
        size = self.frame.grid_size()[1]
        pady = 3
        tk.Label(self.frame, text="Cash").grid(row=size+1, column=0, pady=pady)
        self.cash.config(text=self.potatofy.portfolio.get_cash())
        self.cash.grid(row=size+1, column=1, sticky=tk.E, pady=pady)
        tk.Button(self.frame, text="Add cash", command=self.add_new_cash).grid(row=size+1, column=2, pady=pady, sticky=tk.E)

    def add_new_cash(self):
        self.new_window = Cash(self, self.potatofy)

    def setup_rebalance(self):
        size = self.frame.grid_size()[1]
        tk.Button(self.frame, text="Rebalance", command=self.rebalance).grid(row=size+1, column=2, pady=5, sticky=tk.E)

    def rebalance(self):
        self.new_window = Rebalance(self, self.potatofy)

    def add_rebalancing_pane(self, result):
        self.rebalancing.destroy()
        self.rebalancing = tk.Frame(self.frame)
        self.rebalancing.grid(columnspan=3)
        padx = 5
        tk.Label(self.rebalancing, text='Ticker').grid(row=0, column=0, padx=padx)
        tk.Label(self.rebalancing, text='Shares to Purchase').grid(row=0, column=1, padx=padx)
        tk.Label(self.rebalancing, text='Price per share').grid(row=0, column=2, padx=padx)
        tk.Label(self.rebalancing, text='Target Amount ($)').grid(row=0, column=3, padx=padx)
        tk.Label(self.rebalancing, text='Allocation (%)').grid(row=0, column=4, padx=padx)
        row = 1
        for ticker, data in result.items():
            tk.Label(self.rebalancing, text=ticker).grid(row=row, column=0, padx=padx)
            tk.Label(self.rebalancing, text=data['amount']).grid(row=row, column=1, padx=padx)
            tk.Label(self.rebalancing, text=data['price']).grid(row=row, column=2, padx=padx)
            tk.Label(self.rebalancing, text=data['target_pos']).grid(row=row, column=3, sticky=tk.E, padx=padx)
            tk.Label(self.rebalancing, text=data['target_alloc']).grid(row=row, column=4, sticky=tk.E, padx=padx)
            row += 1
        tk.Label(self.rebalancing, text='Total:\t' + str(self.get_total_target(result))).grid(row=row, column=3, sticky=tk.E, padx=padx)

    def get_total_target(self, result):
        total = 0
        for ticker, data in result.items():
            total += result[ticker]['target_pos']
        return total


class Rebalance:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.frame = tk.Toplevel(self.parent.frame)
        self.potatofy = potatofy
        self.inputs = {}
        self.init()

    def init(self):
        self.frame.config(pady=20, padx=20)
        self.frame.grid()
        self.setup_headings()
        self.setup_positions()
        self.add_confirm_button()

    def setup_headings(self):
        tk.Label(self.frame, text="Holding").grid(row=0, column=0)
        tk.Label(self.frame, text="Target Allocation (%)").grid(row=0, column=1, sticky=tk.E)

    def setup_positions(self):
        row = self.frame.grid_size()[1]
        for ticker in self.potatofy.portfolio.get_all_positions():
            row += 1
            tk.Label(self.frame, text=ticker).grid(row=row, column=0)
            allocation = tk.DoubleVar()
            # TODO: add loaded allocations
            self.inputs[ticker] = allocation
            tk.Entry(self.frame, textvariable=allocation, justify=tk.RIGHT).grid(row=row, column=1)

    def get_total_alloc(self):
        total = 0
        for ticker, alloc in self.inputs.items():
            total += alloc.get()
        return total

    def add_confirm_button(self):
        size = self.frame.grid_size()[1]
        top_pad = (10, 0)
        bot_pad = (0, 10)
        tk.Label(self.frame, text='Rebalance Mode:').grid(row=size+1, column=0, sticky=tk.E, pady=top_pad)
        buy_only = tk.BooleanVar()
        tk.Radiobutton(self.frame, text='Buy & Sell', variable=buy_only, value=False).grid(row=size+1, column=1, sticky=tk.W, pady=top_pad)
        tk.Radiobutton(self.frame, text='Buy Only', variable=buy_only, value=True).grid(row=size+2, column=1, sticky=tk.W, pady=bot_pad)
        tk.Button(self.frame, text="Confirm", command=lambda: self.rebalance(buy_only.get())).grid(row=size+3, columnspan=2, pady=5)

    def rebalance(self, buy_only):
        for ticker, alloc in self.inputs.items():
            self.potatofy.rebalancer.set_target_alloc(ticker, round(alloc.get(), 1))
        if buy_only:
            result = self.potatofy.rebalance_buy_only()
        else:
            result = self.potatofy.rebalance()
        if result is not False:
            self.parent.add_rebalancing_pane(result)
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
        self.init()

    def init(self):
        tk.Label(self.frame, text='How much cash do you want to add?').grid(row=0, pady=3)
        cash = tk.IntVar()
        tk.Entry(self.frame, textvariable=cash, justify=tk.RIGHT).grid(row=1, pady=3)
        tk.Button(self.frame, text="Add", command=lambda: self.add_cash(cash)).grid(row=3, pady=3)

    def add_cash(self, cash_var):
        try:
            cash = cash_var.get()
            self.potatofy.add_cash(cash)
            self.update_parent_cash()
            self.frame.destroy()
        except TclError:
            tk.Label(self.frame, text='Please enter a valid number.', fg='red').grid(row=4, pady=3)

    def update_parent_cash(self):
        self.parent.cash.config(text=round(self.potatofy.get_cash(), 2))


class Position:

    def __init__(self, parent, ticker, amount, potatofy, index):
        self.parent = parent
        self.potatofy = potatofy
        self.ticker = ticker
        self.amount = amount
        self.index = index
        self.frame = self.parent.frame
        self.frame.grid()
        self.setup_data()

    def setup_data(self):
        self.add_holding_ticker(self.ticker)
        self.add_holding_amount(self.amount)
        self.add_allocation(self.amount)

    def add_holding_ticker(self, holding):
        tk.Label(self.frame, text=holding).grid(row=self.index, column=0)

    def add_holding_amount(self, amount):
        tk.Label(self.frame, text=amount).grid(row=self.index, column=1, sticky=tk.E)

    def add_allocation(self, amount):
        allocation = amount / self.potatofy.portfolio.get_total_holdings() * 100
        tk.Label(self.frame, text=round(allocation, 1)).grid(row=self.index, column=2, sticky=tk.E)


class Login:

    def __init__(self, parent, potatofy):
        self.parent = parent
        self.potatofy = potatofy
        self.frame = tk.Toplevel(self.parent.frame)
        self.init()

    def init(self):
        self.frame.config(width=250, height=250, padx=20, pady=20)
        self.frame.resizable(False, False)

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
        self.init()
        tk.Label(self.frame)

    def init(self):
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
        self.init()

    def init(self):
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
        self.init()

    def init(self):
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

    def load_accounts(self):
        self.portfolio.load_accounts()

    def get_broker(self):
        return self.broker

    def get_portfolio(self):
        return self.portfolio

    def rebalance(self):
        return self.rebalancer.calculate_purchases()

    def rebalance_buy_only(self):
        return self.rebalancer.calculate_buy_only_purchases()

    def add_cash(self, cash):
        self.rebalancer.add_cash(cash)

    def get_cash(self):
        return self.rebalancer.get_buying_power()


if __name__ == "__main__":
    root = tk.Tk()
    broker = Broker()
    portfolio = Portfolio(broker)
    rebalancer = Rebalancer(portfolio)
    Potatofy(root, broker, portfolio, rebalancer)
    root.mainloop()
