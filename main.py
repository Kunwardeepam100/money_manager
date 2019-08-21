import tkinter as tk
from tkinter import *
from tkinter import messagebox
from pylab import plot, show, xlabel, ylabel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import defaultdict
from pprint import pprint
import matplotlib.pyplot as plt

from moneymanager import MoneyManager

win = tk.Tk()

#Set window size here to '540 x 640'
win.geometry('540x640+700+200')

#Set the window title to ' Money Manager'
win.title(' Money Management System')

#The user number and associated variable
user_number_var = tk.StringVar()
user_number_var.set('123456')
user_number_entry = tk.Entry(win, textvariable=user_number_var)
user_number_entry.focus_set()

#The pin number entry and associated variables
#Modify the following to display a series of * rather than the pin ie **** not 1234
pin_number_var = tk.StringVar()
pin_number_var.set('7890')
user_pin_entry = tk.Entry(win, text='PIN Number', textvariable=pin_number_var, show='*')


#set the user file by default to an empty string
user_file = ''

# The balance label and associated variable
balance_var = tk.StringVar()
balance_var.set('Balance: $0.00')
balance_label = tk.Label(win, textvariable=balance_var)

# The Entry widget to accept a numerical value to deposit or withdraw
#amount_var = tk.StringVar()
tkVar=StringVar(win)
amount_entry = tk.Entry(win)
entry_type=tk.StringVar()
entry_type.set('food')

# The transaction text widget holds text of the transactions
transaction_text_widget = tk.Text(win, height=10, width=48)

# The money manager object we will work with
user = MoneyManager()

# ---------- Button Handlers for Login Screen ----------

def clear_pin_entry():
    '''Function to clear the PIN number entry when the Clear / Cancel button is clicked.'''    
    # Clear the pin number entry here
    pin_number_var.set("")

def handle_pin_button(event=None):
    '''Function to add the number of the button clicked to the PIN number entry.'''    

    input = event.widget["text"]
    pin = pin_number_var.get()
    new_pin = pin+str(input)

    # Limit to 4 chars in length
    if len(new_pin) > 4:
        return messagebox.showerror("Error", "pin number should be four digits only!")

    # Set the new pin number on the pin_number_var
    pin_number_var.set(new_pin)

def log_in(event=None):
    '''Function to log in to the banking system using a known user number and PIN.'''
    global user
    global pin_number_var
    global user_number_var
    global user_file
    global user_num_entry

    # Create the filename from the entered account number with '.txt' on the end
    file_name = user_number_var.get() + ".txt"

    # Try to open the account file for reading
    try:

        # Open the account file for reading
        user_file = open(file_name, 'r')
        file_data = user_file.read().split('\n')

        # First line is account number
        if file_data[0] == user_number_var.get():
            user.user_number = file_data[0]
        else:
            raise Exception("Invalid user number")

        # Second line is PIN number, raise exceptionk if the PIN entered doesn't match account PIN read 
        if file_data[1] == pin_number_var.get():
            user.pin_number = file_data[1]
        else:
            raise Exception("Invalid pin number")

        # Read third and fourth lines (balance and interest rate) 
        user.balance = file_data[2]
        balance_var.set('Balance: ' + str(user.balance))

        # Section to read account transactions from file - start an infinite 'do-while' loop here

            # Attempt to read a line from the account file, break if we've hit the end of the file. If we
            # read a line then it's the transaction type, so read the next line which will be the transaction amount.
            # and then create a tuple from both lines and add it to the account's transaction_list            
        user_file.seek(0, 0)

        while True:
            line = read_line_from_user_file()
            if not line:
                break
            """ detect only transaction lines """
            if line.startswith("Deposit") or line in ['food', 'rent', 'bills', 'entertainment', 'other']:
                amount = read_line_from_user_file()
                user.transaction_list.append((line, amount))

        # Close the file now we're finished with it
        user_file.close()


        # Catch exception if we couldn't open the file or PIN entered did not match account PIN
    except Exception as errorMsg:
        if "No such file or directory" in str(errorMsg):
            errorMsg = "Invalid user number - please try again!"

        # Show error messagebox and & reset BankAccount object to default...
        messagebox.showerror("Error", errorMsg)
        user = MoneyManager()

        #  ...also clear PIN entry and change focus to account number entry
        clear_pin_entry()
        user_number_entry.focus_set()
        return
    # Got here without raising an exception? Then we can log in - so remove the widgets and display the account screen
    remove_all_widgets()
    create_user_screen()


# ---------- Button Handlers for User Screen ----------

def save_and_log_out():
    '''Function  to overwrite the user file with the current state of
       the user object (i.e. including any new transactions), remove
       all widgets and display the login screen.'''
    global user

    # Save the account with any new transactions
    user.save_to_file()

    # Reset the bank acount object
    user = MoneyManager()

    # Reset the account number and pin to blank
    clear_pin_entry()
    user_number_var.set('')
    user_number_entry.focus_set()

    # Remove all widgets and display the login screen again
    remove_all_widgets()
    create_login_screen()

def perform_deposit():
    '''Function to add a deposit for the amount in the amount entry to the
       user's transaction list.'''
    global user
    global amount_entry
    global balance_label
    global balance_var


    # Try to increase the account balance and append the deposit to the account file
    try:

        # Get the cash amount to deposit. Note: We check legality inside account's deposit method
        amount_to_deposit = amount_entry.get()

        # Deposit funds
        deposit_funds_msg = user.deposit_funds(amount_to_deposit)

        if deposit_funds_msg != "Deposit Successful":
            raise Exception(deposit_funds_msg)

        # Update the transaction widget with the new transaction by calling account.get_transaction_string()
        # Note: Configure the text widget to be state='normal' first, then delete contents, then instert new
        #       contents, and finally configure back to state='disabled' so it cannot be user edited.
        transaction_text_widget['state'] = 'normal'
        transaction_text_widget.delete(0.0, tk.END)
        transaction_text_widget.insert(tk.END, user.get_transaction_string())
        transaction_text_widget['state'] = 'disabled'

        # Change the balance label to reflect the new balance
        balance_var.set('Balance: ' + str(user.balance))

        # Clear the amount entry
        amount_entry.delete(0, 'end')

        # Update the interest graph with our new balance
        plot_spending_graph()

    # Catch and display exception as a 'showerror' messagebox with a title of 'Transaction Error' and the text of the exception
    except Exception as errorMsg:
        return messagebox.showerror("Transaction Error", errorMsg)

def perform_transaction():
    '''Function to add the entry the amount in the amount entry from the user balance and add an entry to the transaction list.'''
    global user
    global amount_entry
    global balance_label
    global balance_var
    global entry_type

    # Try to decrease the account balance and append the deposit to the account file
    try:
        # Get the cash amount to use. Note: We check legality inside account's withdraw_funds method
        amount_to_use = amount_entry.get()

        # Get the type of entry that will be added ie rent etc
        type_of_entry = entry_type.get()

        # Withdraw funds from the balance
        withdraw_funds_msg = user.add_entry(amount_to_use, str(type_of_entry))

        if withdraw_funds_msg != "Entry Successful":
            raise Exception(withdraw_funds_msg)

        # Update the transaction widget with the new transaction by calling user.get_transaction_string()
        # Note: Configure the text widget to be state='normal' first, then delete contents, then instert new
        #       contents, and finally configure back to state='disabled' so it cannot be user edited.
        transaction_text_widget['state'] = 'normal'
        transaction_text_widget.delete(0.0, tk.END)
        transaction_text_widget.insert(tk.END, user.get_transaction_string())
        transaction_text_widget['state'] = 'disabled'

        # Change the balance label to reflect the new balance
        balance_var.set('Balance: ' + str(user.balance))

        # Clear the amount entry
        amount_entry.delete(0, 'end')

        # Update the graph
        plot_spending_graph()

    # Catch and display any returned exception as a messagebox 'showerror'
    except Exception as errorMsg:
        return messagebox.showerror("Transaction Error", errorMsg)

def remove_all_widgets():
    '''Function to remove all the widgets from the window.'''
    global win
    for widget in win.winfo_children():
        widget.grid_remove()

def read_line_from_user_file():
    '''Function to read a line from the users file but not the last newline character.
       Note: The user_file must be open to read from for this function to succeed.'''
    global user_file
    return user_file.readline()[0:-1]

def plot_spending_graph():
    '''Function to plot the user spending here.'''
    # YOUR CODE to generate the x and y lists here which will be plotted
    x = []
    y = []
    for data in user.transaction_list:
        a,b = data
        x.append(a)
        y.append(float(b))

    #Your code to display the graph on the screen here - do this last
    figure = Figure(figsize=(5, 2), dpi=100)
    canvas = FigureCanvasTkAgg(figure, master=win)
    canvas.get_tk_widget().grid(row=5, column=0, columnspan=5, sticky='nsew')
    figure.suptitle('User Spending Graph')

    a = figure.gca()
    a.bar(x, y)
    a.set_ylabel('Amount($)', fontsize=10)
    canvas.draw()


    
# ---------- UI Drawing Functions ----------

def create_login_screen():
    '''Function to create the login screen.'''    
    

    # ----- Row 0 -----

    # 'FedUni Money Manager' label here. Font size is 28.
    tk.Label(win, text=" Money Manager", fg="black", font="none 32").grid(row=0, column=0, columnspan=3, sticky='nsew')

    # ----- Row 1 -----

    #  User Number / Pin label here
    tk.Label(win, text="User Number/PIN", height=4, width=20
             ).grid(row=1, column=0, sticky="nsew")

    # User number entry here
    user_number_entry.grid(row=1, column=1, sticky="nsew")

    # User pin entry here
    user_pin_entry.grid(row=1, column=2, sticky="nsew")
    
 

    # ----- Row 2 -----

    # Buttons 1, 2 and 3 here. Buttons are bound to 'handle_pin_button' function via '<Button-1>' event.
    button_1 = tk.Button(win, text="1")
    button_1.grid(row=2, column=0, sticky="nsew")
    button_1.bind("<Button-1>", handle_pin_button)

    button_2 = tk.Button(win, text="2")
    button_2.grid(row=2, column=1, sticky="nsew")
    button_2.bind("<Button-1>", handle_pin_button)

    button_3 = tk.Button(win, text="3")
    button_3.grid(row=2, column=2, sticky="nsew")
    button_3.bind("<Button-1>", handle_pin_button)

    # ----- Row 3 -----

    # Buttons 4, 5 and 6 here. Buttons are bound to 'handle_pin_button' function via '<Button-1>' event.
    button_4 = tk.Button(win, text="4")
    button_4.grid(row=3, column=0, sticky="nsew")
    button_4.bind("<Button-1>", handle_pin_button)

    button_5 = tk.Button(win, text="5")
    button_5.grid(row=3, column=1, sticky="nsew")
    button_5.bind("<Button-1>", handle_pin_button)

    button_6 = tk.Button(win, text="6")
    button_6.grid(row=3, column=2, sticky="nsew")
    button_6.bind("<Button-1>", handle_pin_button)

    # ----- Row 4 -----

    # Buttons 7, 8 and 9 here. Buttons are bound to 'handle_pin_button' function via '<Button-1>' event.
    button_7 = tk.Button(win, text="7")
    button_7.grid(row=4, column=0, sticky="nsew")
    button_7.bind("<Button-1>", handle_pin_button)

    button_8 = tk.Button(win, text="8")
    button_8.grid(row=4, column=1, sticky="nsew")
    button_8.bind("<Button-1>", handle_pin_button)

    button_9 = tk.Button(win, text="9")
    button_9.grid(row=4, column=2, sticky="nsew")
    button_9.bind("<Button-1>", handle_pin_button)

    # ----- Row 5 -----

    # Cancel/Clear button here. 'bg' and 'activebackground' should be 'red'. But calls 'clear_pin_entry' function.
    tk.Button(win, text="Cancel/Clear", bg="red",activebackground="red", command=clear_pin_entry).grid(row=5, column=0, sticky="nsew")

    # Button 0 here
    button_0 = tk.Button(win, text="0")
    button_0.grid(row=5, column=1, sticky="nsew")
    button_0.bind("<Button-1>", handle_pin_button)

    # Login button here. 'bg' and 'activebackground' should be 'green'). Button calls 'log_in' function.
    tk.Button(win, text="Login", bg="green",activebackground="green", command=log_in).grid(row=5, column=2, sticky="nsew")

    # ----- Set column & row weights -----

    # Set column and row weights. There are 5 columns and 6 rows (0..4 and 0..5 respectively)
    win.columnconfigure(0, weight=1)
    win.columnconfigure(1, weight=1)
    win.columnconfigure(2, weight=1)
    win.columnconfigure(3, weight=1)
    win.rowconfigure(0, weight=1)
    win.rowconfigure(2, weight=1)
    win.rowconfigure(3, weight=1)
    win.rowconfigure(4, weight=1)
    win.rowconfigure(5, weight=1)

def create_user_screen():
    '''Function to create the user screen.'''
    global amount_text
    global amount_label
    global transaction_text_widget
    global balance_var
    global entry_type
    
    # ----- Row 0 -----

    # FedUni Money Manager label here. Font size should be 22.
    tk.Label(win, text=" Money Manager", font="none 22").grid(row=0, column=0, sticky='nsew', columnspan=4)

    # ----- Row 1 -----

    # User number label here
    user_label = "User Number: "+str(user_number_var.get())
    tk.Label(win, text=user_label, height=4, width=28).grid(row=1, column=0, sticky='nsew')

    # Balance label here
    balance_label.grid(row=1, column=1, sticky='nsew')

    # Log out button here
    tk.Button(win, text="Log Out", command=save_and_log_out).grid(row=1, column=2, sticky="nsew", columnspan=2)

    # ----- Row 2 -----

    # Amount label here
    tk.Label(win, text="Amount($)").grid(row=2, column=0, sticky='nsew')

    # Amount entry here
    amount_entry.grid(row=2, column=1, sticky='nsew')

    # Deposit button here
    tk.Button(win, text="Deposit", command=perform_deposit, width=12).grid(row=2, column=2, sticky="nsew")

    # NOTE: Bind Deposit and Withdraw buttons via the command attribute to the relevant deposit and withdraw
    #       functions in this file. If we "BIND" these buttons then the button being pressed keeps looking as
    #       if it is still pressed if an exception is raised during the deposit or withdraw operation, which is
    #       offputting.
    
    
    # ----- Row 3 -----
    # Entry type label here
    tk.Label(win, text="Entry Type").grid(row=3, column=0, sticky='nsew')

    # Entry drop list here
    l = ['food', 'rent', 'bills', 'entertainment', 'other']
    drop = tk.OptionMenu(win,entry_type, *l)
    drop.grid(row=3, column=1, sticky="nsew")

    # Add entry button here
    tk.Button(win, text="Add Entry", command=perform_transaction, width=12).grid(row=3, column=2, sticky="nsew")

    # ----- Row 4 -----

    # Declare scrollbar (text_scrollbar) here (BEFORE transaction text widget)
    text_scrollbar = tk.Scrollbar(win)
    text_scrollbar.grid(row=4, column=1, columnspan=5, sticky='nse')

    # Add transaction Text widget and configure to be in 'disabled' mode so it cannot be edited.
    # Note: Set the yscrollcommand to be 'text_scrollbar.set' here so that it actually scrolls the Text widget
    # Note: When updating the transaction text widget it must be set back to 'normal mode' (i.e. state='normal') for it to be edited
    transaction_text_widget['wrap'] = tk.NONE
    transaction_text_widget['bd'] = 0
    transaction_text_widget['state'] = 'disabled'
    transaction_text_widget['yscrollcommand'] = text_scrollbar.set
    transaction_text_widget.grid(row=4, column=0, columnspan=5, sticky='nsew')

    # Now add the scrollbar and set it to change with the yview of the text widget
    text_scrollbar.config(command=transaction_text_widget.yview)

    transaction_text_widget['state'] = 'normal'
    transaction_text_widget.delete(0.0, tk.END)
    transaction_text_widget.insert(tk.END, user.get_transaction_string())
    transaction_text_widget['state'] = 'disabled'
    # ----- Row 5 - Graph -----

    # Call plot_interest_graph() here to display the graph
    plot_spending_graph()

    # ----- Set column & row weights -----

    # Set column and row weights here - there are 6 rows and 5 columns (numbered 0 through 4 not 1 through 5!)
    win.columnconfigure(0, weight=1)
    win.columnconfigure(1, weight=1)
    win.columnconfigure(2, weight=1)
    win.columnconfigure(3, weight=1)
    win.rowconfigure(0, weight=1)
    win.rowconfigure(2, weight=1)
    win.rowconfigure(3, weight=1)
    win.rowconfigure(4, weight=1)
    win.rowconfigure(5, weight=1)



# ---------- Display Login Screen & Start Main loop ----------

create_login_screen()
win.mainloop()
