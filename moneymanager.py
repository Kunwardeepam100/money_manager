class MoneyManager():

    def __init__(self):
        '''Constructor to set usernumber to int, pin_number to an empty string,
           balance to 0.0, and transaction_list to an empty list.'''
        self.user_number = 0
        self.pin_number = ''
        self.balance = 0.0
        self.transaction_list = []

    def add_entry(self, amount, entry_type):
        '''Function to add and entry an amount to the tool. Raises an
           exception if it receives a value for amount that cannot be cast to float. Raises an exception
           if the entry_type is not valid - i.e. not food, rent, bills, entertainment or other'''
        try:

            if float(self.balance) < float(amount):
                raise ValueError
            self.balance = float(self.balance) - float(amount)

            if entry_type not in ['food', 'rent', 'bills', 'entertainment', 'other']:
                raise TypeError

            self.transaction_list.append((entry_type, float(amount)))

            return "Entry Successful"

        except ValueError:
            return "No Sufficient balance"

        except TypeError:
            return "Entry type not valid"

    def deposit_funds(self, amount):
        '''Function to deposit an amount to the user balance. Raises an
           exception if it receives a value that cannot be cast to float. '''
        try:
            self.balance = float(self.balance) + float(amount)
            self.transaction_list.append(("Deposit", float(amount)))
            return "Deposit Successful"

        except (TypeError,ValueError):
            return "Invalid Data Format"

    def get_transaction_string(self):
        '''Function to create and return a string of the transaction list. Each transaction
           consists of two lines - either the word "Deposit" or the entry type - food etc - on
           the first line, and then the amount deposited or entry amount on the next line.'''
        transaction_string = ''
        for transaction in self.transaction_list:
            transaction_type, amount = transaction
            transaction_string += str(transaction_type) + '\n' + str(amount) + '\n'
        return transaction_string

    def save_to_file(self):
        '''Function to overwrite the user text file with the current user
           details. user number, pin number, and balance (in that
           precise order) are the first four lines - there are then two lines
           per transaction as outlined in the above 'get_transaction_string'
           function.'''
        file = str(self.user_number) + '.txt'

        with open(file, 'w') as f:
            f.write("%s\n" % self.user_number)
            f.write("%s\n" % self.pin_number)
            f.write("%s\n" % self.balance)

            for transaction in self.transaction_list:
                transaction_type, amount = transaction
                f.write("%s\n" % transaction_type)
                f.write("%s\n" % amount)


        



        
