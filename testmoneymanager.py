import unittest

from moneymanager import MoneyManager

class TestMoneyManager(unittest.TestCase):

    def setUp(self):
        # Create a test BankAccount object
        self.user = MoneyManager()

        # Provide it with some initial balance values        
        self.user.balance = 1000.0

    def test_legal_deposit_works(self):
        # Your code here to test that depsositing money using the account's
        # 'deposit_funds' function adds the amount to the balance.
        self.user.deposit_funds(100)
        self.assertEqual(self.user.balance, 1100)

    def test_illegal_deposit_raises_exception(self):
        # Your code here to test that depositing an illegal value (like 'bananas'
        # or such - something which is NOT a float) results in an exception being
        # raised.
        self.assertRaises((TypeError, ValueError), self.user.deposit_funds('bananas'))
        self.assertRaises((TypeError, ValueError), self.user.deposit_funds('1000'))

    def test_legal_entry(self):
        # Your code here to test that adding a new entry with a a legal amount subtracts the
        # funds from the balance.
        self.user.add_entry(500,'food')
        self.assertEqual(self.user.balance, 500)

    def test_illegal_entry_amount(self):
        # Your code here to test that withdrawing an illegal amount (like 'bananas'
        # or such - something which is NOT a float) raises a suitable exception.
        self.assertRaises((TypeError, ValueError), self.user.add_entry('bananas','food'))
        self.assertRaises((TypeError, ValueError), self.user.add_entry('500','food'))

        
    def test_illegal_entry_type(self):
        # Your code here to test that adding an illegal entry type (like 'bananas'
        # or such - something which is NOT a float) raises a suitable exception.
        self.assertRaises((TypeError, ValueError), self.user.add_entry(500, 'bananas'))
        self.assertRaises((TypeError, ValueError), self.user.add_entry(500, 1200))

    def test_insufficient_funds_entry(self):
        # Your code here to test that you can only spend funds which are available.
        # For example, if you have a balance of 500.00 dollars then that is the maximum
        # that can be spent. If you tried to spend 600.00 then a suitable exception
        # should be raised and the withdrawal should NOT be applied to the user balance
        # or the user's transaction list.
        self.assertRaises((TypeError, ValueError), self.user.add_entry(2000, 'food'))

# Run the unit tests in the above test case
unittest.main()
