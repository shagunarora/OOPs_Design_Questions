"""
Simulate splitwise app where users will store from (A), to (B), 
amount (X) which refers to amount X need to be transferred from 
user A to user B.

Splitwise should store all these transactions and also store
transactions need to be done for complete settlement.

Note: In this version having an optimzed settlement algorithm 
is not required.

Solution discussion:
    from, to, amt

    1. Calculate net amount per person.
    2. settle transactions using debtors and creditors.


"""
class Splitwise:
    def __init__(self):
        self.net_amt_per_user = {}
        self.transactions_history = []
        self.transactions = []
        self.settlements = []
    
    def create_transaction(self, from_user: str, to_user: str, amt: int):
        self.transactions.append([from_user, to_user, amt])

        # Store net amount owed/pending for each user in net_amt_per_user
        # map.
        self.net_amt_per_user[from_user] = self.net_amt_per_user.get(from_user, 0) - amt
        self.net_amt_per_user[to_user] = self.net_amt_per_user.get(to_user, 0) + amt

    def get_settlements(self):
        # Store all the debtors and creditors in 2 different list.
        debtors  =[]
        creditors = []
        for user, amt in self.net_amt_per_user.items():
            if amt < 0:
                debtors.append([user, abs(amt)])
            elif amt > 0:
                creditors.append([user, amt])
            
        debtors_itr = 0
        creditors_itr = 0

        while debtors_itr < len(debtors) and creditors_itr < len(creditors):
            debt_user, debt_amt = debtors[debtors_itr]
            credit_user, credit_amt = creditors[creditors_itr]

            if debt_amt < credit_amt:
                self.settlements.append((debt_user, credit_user, debt_amt))
                debtors_itr += 1
                creditors[creditors_itr][1] -= debt_amt
            elif credit_amt < debt_amt:
                self.settlements.append((debt_user, credit_user, credit_amt))
                creditors_itr += 1
                debtors[debtors_itr][1] -= credit_amt
            else:
                self.settlements.append((debt_user, credit_user, credit_amt))
                creditors_itr += 1
                debtors_itr += 1

        return self.settlements

    def clear_settlements(self):
        """
        Clear settlements and reset all net balances after settlements.
        """
        self.transactions_history.extend(self.transactions)
        self.transactions.clear()
        self.net_amt_per_user.clear()
        self.settlements.clear()

# Test
splitwise = Splitwise()
splitwise.create_transaction("A", "B", 400)
splitwise.create_transaction("A", "C", 400)
splitwise.create_transaction("C", "B", 200)
splitwise.create_transaction("C", "D", 100)

print(splitwise.get_settlements())
