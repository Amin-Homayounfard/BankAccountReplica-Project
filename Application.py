from random import randint
from re import sub
from Database import Database
from datetime import date


class Application:

    ownerNationalID = None

    def __init__(self):
        self.MainMenu()

    def MainMenu(self):
        while True:
            print("Select a number.")
            print("1. Sign up.")
            print("2. Sign in.")
            print("0. Exit.")
            userInput = input(">>> ")
            if userInput == "1":
                self.SignUp()
            elif userInput == "2":
                self.SignIn()
            else:
                return

    def BankingServiceMenu(self):
        while True:
            print("Select a number.")
            print("1. Open an account.")
            print("2. Display account information.")
            print("3. Account managment.")
            print("4. Mark the accounts as frequently used.")
            print("5. Money transfer.")
            print("7. Paying the bill")
            print("8. Requesting a loan.")
            print("9. Close account.")
            print("0. Back to main menu.")
            userInput = input(">>> ")
            if userInput == "1":
                BankSystem.OpenAnAccount()
            elif userInput == "2":
                BankSystem.DisplayInformation()
            elif userInput == "4":
                BankSystem.MarkAsFrequentlyUsed()
            elif userInput == "5":
                BankSystem.MoneyTransfer()
            elif userInput == "9":
                BankSystem.CloseAccount()
            else:
                return

    @staticmethod
    def CheckInputValidity(field, fieldValue, tableName=None):
        if tableName is not None:
            if field.isUnique and db.Select(
                tableName, f'{field.fieldName}=="{fieldValue}"'
            ):
                print(f"{fieldValue} is already exist.")
                return False
        if field.fieldType == "INTEGER" and not fieldValue.isdigit():
            print(f"{fieldValue} must be an integer.")
            return False
        elif "CHAR" in field.fieldType:
            legalCount = int(sub("[()]", "", field.fieldType.replace("CHAR", "")))
            if len(fieldValue) > legalCount:
                print(f"{fieldValue}'s number of characters exceeded {legalCount}.")
                return False
        return True

    @staticmethod
    def FindCorrespondingField(fieldName, tableName):
        for field in db.tables[tableName]:
            if field.fieldName == fieldName:
                return field

    @classmethod
    def ReceiveUserInput(cls, fieldName, tableName, purpose):
        field = cls.FindCorrespondingField(fieldName, tableName)
        while True:
            print(f"Enter your {fieldName}.")
            userInput = input()
            if purpose == "insert":
                if cls.CheckInputValidity(field, userInput, tableName):
                    return userInput
            elif purpose == "select":
                if cls.CheckInputValidity(field, userInput):
                    return userInput

    def SignUp(self):
        name = self.ReceiveUserInput("name", "User", "insert")
        nationalID = self.ReceiveUserInput("nationalID", "User", "insert")
        password = self.ReceiveUserInput("password", "User", "insert")
        phoneNumber = self.ReceiveUserInput("phoneNumber", "User", "insert")
        email = self.ReceiveUserInput("email", "User", "insert")
        joinedAt = str(date.today())
        db.Insert("User", [name, nationalID, password, phoneNumber, email, joinedAt])

    def SignIn(self):
        while True:
            nationalID = self.ReceiveUserInput("nationalID", "User", "select")
            password = self.ReceiveUserInput("password", "User", "select")
            collectedResult = db.Select("User", f'nationalID=="{nationalID}"')
            if collectedResult:
                collectedPassword = collectedResult[0].split()[3]
                if password == collectedPassword:
                    break
                else:
                    print("Wrong password!")
            else:
                print("national ID not exists.")
        Application.ownerNationalID = nationalID
        self.BankingServiceMenu()


class BankSystem:
    @staticmethod
    def OpenAnAccount():
        accountType = Application.ReceiveUserInput("type", "BankAccount", "insert")
        number = "".join(str(randint(1, 9)) for _ in range(10))
        alias = Application.ReceiveUserInput("alias", "BankAccount", "insert")
        password = Application.ReceiveUserInput("password", "BankAccount", "insert")
        balance = "0"
        isFrequent = "False"
        db.Insert(
            "BankAccount",
            [
                accountType,
                number,
                alias,
                password,
                isFrequent,
                Application.ownerNationalID,
                balance,
            ],
        )
        print(f"Your bank number is: {number}")

    @staticmethod
    def DisplayInformation():
        accountsCollectedResult = db.Select(
            "BankAccount", f'ownerNationalID=="{Application.ownerNationalID}"'
        )
        if accountsCollectedResult:
            for account in accountsCollectedResult:
                balance = account.split()[-1]
                number = account.split()[2]
                transactions = [
                    f'{" ".join(transaction.split()[1:])}'
                    for transaction in db.Select(
                        "Transactions", f'sourceNumber=="{number}"'
                    )
                ]
                print(f"Balance: {balance}")
                print(f"Transactions: {transactions}")

    @staticmethod
    def MoneyTransfer():
        while True:
            sourceNumber = Application.ReceiveUserInput(
                "sourceNumber", "Transactions", "select"
            )
            password = Application.ReceiveUserInput("password", "BankAccount", "select")
            sourceCollectedResult = db.Select(
                "BankAccount", f'number=="{sourceNumber}"'
            )
            if sourceCollectedResult:
                collectedPassword = sourceCollectedResult[0].split()[4]
                if password == collectedPassword:
                    break
                else:
                    print("Wrong password!")
            else:
                print("Account number not exists.")
        while True:
            destinationNumber = Application.ReceiveUserInput(
                "destinationNumber", "Transactions", "insert"
            )
            moneyAmount = Application.ReceiveUserInput(
                "amount", "Transactions", "insert"
            )
            happenedAt = str(date.today())
            destinationCollectedResult = db.Select(
                "BankAccount", f'number=="{destinationNumber}"'
            )
            if destinationCollectedResult:
                destinationCurrentBalance = int(
                    destinationCollectedResult[0][1:].split()[-1]
                )
                sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
                if sourceCurrentBalance >= int(moneyAmount):
                    db.Insert(
                        "Transactions",
                        [sourceNumber, destinationNumber, moneyAmount, happenedAt],
                    )
                    sourceUpdatedValues = sourceCollectedResult[0][1:].split()[:-1] + [
                        str(sourceCurrentBalance - int(moneyAmount))
                    ]
                    destinationUpdatedValues = destinationCollectedResult[0][
                        1:
                    ].split()[:-1] + [str(destinationCurrentBalance + int(moneyAmount))]
                    db.Update(
                        "BankAccount", sourceUpdatedValues, f'number=="{sourceNumber}"'
                    )
                    db.Update(
                        "BankAccount",
                        destinationUpdatedValues,
                        f'number=="{destinationNumber}"',
                    )
                    break
                else:
                    print("Not enough money.")

    @staticmethod
    def TransferRemainingMoney(sourceNumber, moneyAmount):
        sourceCollectedResult = db.Select("BankAccount", f'number=="{sourceNumber}"')
        while True:
            destinationNumber = Application.ReceiveUserInput(
                "destinationNumber", "Transactions", "insert"
            )
            happenedAt = str(date.today())
            db.Insert(
                "Transactions",
                [sourceNumber, destinationNumber, moneyAmount, happenedAt],
            )
            destinationCollectedResult = db.Select(
                "BankAccount", f'number=="{destinationNumber}"'
            )
            if destinationCollectedResult:
                destinationCurrentBalance = int(
                    destinationCollectedResult[0][1:].split()[-1]
                )
                sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
                if sourceCurrentBalance >= int(moneyAmount):
                    sourceUpdatedValues = sourceCollectedResult[0][1:].split()[:-1] + [
                        str(sourceCurrentBalance - int(moneyAmount))
                    ]
                    destinationUpdatedValues = destinationCollectedResult[0][
                        1:
                    ].split()[:-1] + [str(destinationCurrentBalance + int(moneyAmount))]
                    db.Update(
                        "BankAccount", sourceUpdatedValues, f'number=="{sourceNumber}"'
                    )
                    db.Update(
                        "BankAccount",
                        destinationUpdatedValues,
                        f'number=="{destinationNumber}"',
                    )
                    break
                else:
                    print("Not enough money.")

    def MarkAsFrequentlyUsed():
        while True:
            numbers = []
            collectedResults = []
            print("How many numbers you want to mark as frequently used?")
            n = input()
            if not n.isdigit():
                print("You must enter a didgit.")
                continue
            print("Enter numbers that you want to mark as frequently used.")
            for _ in range(int(n)):
                numbers.append(
                    Application.ReceiveUserInput("number", "BankAccount", "select")
                )
            for number in numbers:
                collectedResult = db.Select(
                    "BankAccount",
                    f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
                )
                if not collectedResult:
                    continue
                collectedResults.append(collectedResult[0])
            print("Choose an alias for your frequently used numbers.")
            alias = Application.ReceiveUserInput("alias", "BankAccount", "select")
            break
        for number, collectedResult in zip(numbers, collectedResults):
            print(collectedResult.split()[1:3])
            print([alias])
            updatedValues = (
                collectedResult.split()[1:3]
                + [alias]
                + [collectedResult.split()[4]]
                + ["True"]
                + collectedResult.split()[6:]
            )
            db.Update("BankAccount", updatedValues, f'number=="{number}"')

    @staticmethod
    def CloseAccount():
        while True:
            sourceNumber = Application.ReceiveUserInput(
                "number", "BankAccount", "select"
            )
            password = Application.ReceiveUserInput("password", "BankAccount", "select")
            sourceCollectedResult = db.Select(
                "BankAccount", f'number=="{sourceNumber}"'
            )
            if sourceCollectedResult:
                collectedPassword = sourceCollectedResult[0].split()[4]
                if password == collectedPassword:
                    break
                else:
                    print("Wrong password!")
            else:
                print("Account number not exists.")

        sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
        if sourceCurrentBalance > 0:
            BankSystem.TransferRemainingMoney(sourceNumber, str(sourceCurrentBalance))
        db.Delete("BankAccount", f'number=="{sourceNumber}"')


db = Database()
app = Application()
