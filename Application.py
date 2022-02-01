from random import randint
from re import sub
from threading import Timer
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

    @staticmethod
    def BankingServiceMenu():
        while True:
            print("Select a number.")
            print("1. Open an account.")
            print("2. Display accounts information.")
            print("3. Account managment.")
            print("4. Mark the accounts as frequently used.")
            print("5. Money transfer.")
            print("6. Paying the bill")
            print("7. Requesting a loan.")
            print("8. Close account.")
            print("0. Back to main menu.")
            userInput = input(">>> ")
            if userInput == "1":
                BankSystem.OpenAnAccount()
            elif userInput == "2":
                BankSystem.DisplayInformation()
            elif userInput == "3":
                BankSystem.AccountManagmentMenu()
            elif userInput == "4":
                BankSystem.MarkAsFrequentlyUsed()
            elif userInput == "5":
                BankSystem.MoneyTransfer()
            elif userInput == "6":
                BankSystem.PayTheBill()
            elif userInput == "7":
                BankSystem.LoanRequest()
            elif userInput == "8":
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

    @classmethod
    def SignUp(cls):
        name = cls.ReceiveUserInput("name", "User", "insert")
        nationalID = cls.ReceiveUserInput("nationalID", "User", "insert")
        password = cls.ReceiveUserInput("password", "User", "insert")
        phoneNumber = cls.ReceiveUserInput("phoneNumber", "User", "insert")
        email = cls.ReceiveUserInput("email", "User", "insert")
        joinedAt = str(date.today())
        db.Insert("User", [name, nationalID, password, phoneNumber, email, joinedAt])

    @classmethod
    def SignIn(cls):
        while True:
            nationalID = cls.ReceiveUserInput("nationalID", "User", "select")
            password = cls.ReceiveUserInput("password", "User", "select")
            collectedResult = db.Select("User", f'nationalID=="{nationalID}"')
            if not collectedResult:
                print("National ID not exists.")
                continue
            collectedPassword = collectedResult[0].split()[3]
            if not password == collectedPassword:
                print("Wrong password!")
                continue
            break
        Application.ownerNationalID = nationalID
        cls.BankingServiceMenu()


class BankSystem:

    installmentDuration = 30

    @staticmethod
    def OpenAnAccount():
        accountType = Application.ReceiveUserInput("type", "BankAccount", "insert")
        number = "".join(str(randint(1, 9)) for _ in range(10))
        alias = Application.ReceiveUserInput("alias", "BankAccount", "insert")
        password = Application.ReceiveUserInput("password", "BankAccount", "insert")
        balance = "0"
        db.Insert(
            "BankAccount",
            [
                accountType,
                number,
                alias,
                password,
                Application.ownerNationalID,
                balance,
            ],
        )
        print(f"Your bank number is: {number}")

    @staticmethod
    def DisplayInformation(
        condition=f'ownerNationalID=="{Application.ownerNationalID}"',
    ):
        accountsCollectedResult = db.Select("BankAccount", condition)
        for i, account in enumerate(accountsCollectedResult):
            balance = account.split()[-1]
            accountType = account.split()[1]
            number = account.split()[2]
            alias = account.split()[3]
            transactions = [
                f'{" ".join(transaction.split()[1:])}'
                for transaction in db.Select(
                    "Transactions", f'sourceNumber=="{number}"'
                )
            ]
            print(f"{i}.")
            print(f"Type: {accountType}")
            print(f"Alias: {alias}")
            print(f"Number: {number}")
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
                "BankAccount",
                f'number=="{sourceNumber}" AND ownerNationalID=="{Application.ownerNationalID}"',
            )
            if not sourceCollectedResult:
                print("Account number not exists.")
                continue
            collectedPassword = sourceCollectedResult[0].split()[4]
            if not password == collectedPassword:
                print("Wrong password!")
                continue
            break
        while True:
            print(
                "Do you want to select the destination account number from the most used account numbers? (y/n)"
            )
            userInput = input()
            if not userInput in ["y", "n"]:
                continue
            if userInput == "y":
                print("Choose the number of one of the most used accounts below.")
                frequentlyUsedCollectedResult = db.Select(
                    "FrequentlyUsedAccounts",
                    f'ownerNationalID=="{Application.ownerNationalID}"',
                )
                print(frequentlyUsedCollectedResult)
                frequentlyUsedAccounts = []
                for result in frequentlyUsedCollectedResult:
                    frequentlyUsedAccounts.append(result.split()[2])
                    print(f"{result.split()[1]}: {result.split()[2]}")
                userInput = input()
                if not userInput in frequentlyUsedAccounts:
                    print("Your selection is not listed.")
                    continue
                destinationNumber = userInput
            elif userInput == "n":
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
            if not destinationCollectedResult:
                print("Destination number not exists.")
                continue
            destinationCurrentBalance = int(
                destinationCollectedResult[0][1:].split()[-1]
            )
            sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
            if not sourceCurrentBalance >= int(moneyAmount):
                print("Not enough money.")
                continue
            db.Insert(
                "Transactions",
                [sourceNumber, destinationNumber, moneyAmount, happenedAt],
            )
            sourceUpdatedValues = sourceCollectedResult[0][1:].split()[:-1] + [
                str(sourceCurrentBalance - int(moneyAmount))
            ]
            db.Update("BankAccount", sourceUpdatedValues, f'number=="{sourceNumber}"')
            destinationUpdatedValues = destinationCollectedResult[0][1:].split()[
                :-1
            ] + [str(destinationCurrentBalance + int(moneyAmount))]
            db.Update(
                "BankAccount",
                destinationUpdatedValues,
                f'number=="{destinationNumber}"',
            )
            break

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
            if not destinationCollectedResult:
                print("Destination number not exists.")
                continue
            destinationCurrentBalance = int(
                destinationCollectedResult[0][1:].split()[-1]
            )
            sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
            if not sourceCurrentBalance >= int(moneyAmount):
                print("Not enough money.")
                continue
            sourceUpdatedValues = sourceCollectedResult[0][1:].split()[:-1] + [
                str(sourceCurrentBalance - int(moneyAmount))
            ]
            destinationUpdatedValues = destinationCollectedResult[0][1:].split()[
                :-1
            ] + [str(destinationCurrentBalance + int(moneyAmount))]
            db.Update("BankAccount", sourceUpdatedValues, f'number=="{sourceNumber}"')
            db.Update(
                "BankAccount",
                destinationUpdatedValues,
                f'number=="{destinationNumber}"',
            )
            break

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
                    f'number=="{number}"',
                )
                if not collectedResult:
                    break
                collectedResults.append(collectedResult[0])
            break
        for number, collectedResult in zip(numbers, collectedResults):
            alias = collectedResult.split()[3]
            db.Insert(
                "FrequentlyUsedAccounts", [alias, number, Application.ownerNationalID]
            )

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
            if not sourceCollectedResult:
                print("Account number not exists.")
                continue
            collectedPassword = sourceCollectedResult[0].split()[4]
            if not password == collectedPassword:
                print("Wrong password!")
                continue
            break
        sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
        if sourceCurrentBalance > 0:
            BankSystem.TransferRemainingMoney(sourceNumber, str(sourceCurrentBalance))
        db.Delete("BankAccount", f'number=="{sourceNumber}"')

    @classmethod
    def LoanRequest(cls):
        while True:
            print("How much money do you ask for?")
            moneyAmount = input()
            if not moneyAmount.isdigit():
                continue
            moneyAmount = int(moneyAmount)
            break
        while True:
            print("How many periods do you intend to pay?")
            periods = input()
            if not periods.isdigit():
                continue
            periods = int(periods)
            break
        while True:
            number = Application.ReceiveUserInput("number", "BankAccount", "select")
            collectedResult = db.Select(
                "BankAccount",
                f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
            )
            if not collectedResult:
                print("The entered card number is incorrect.")
                continue
            break
        currentBalance = int(collectedResult[0].split()[-1])
        updatedValues = collectedResult[0].split()[1:-1] + [
            str(currentBalance + moneyAmount)
        ]
        db.Update(
            "BankAccount",
            updatedValues,
            f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
        )
        eachLoanInstallmentAmount = moneyAmount // periods
        t = Timer(
            cls.installmentDuration,
            cls.LoanInstallmentPayment,
            args=[eachLoanInstallmentAmount, number, periods - 1],
        )
        t.start()

    @classmethod
    def LoanInstallmentPayment(cls, installmentAmount, number, periods):
        t = Timer(
            cls.installmentDuration,
            cls.LoanInstallmentPayment,
            args=[installmentAmount, number, periods - 1],
        )
        t.start()
        if periods == 0:
            t.cancel()
        collectedResult = db.Select(
            "BankAccount",
            f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
        )
        currentBalance = int(collectedResult[0].split()[-1])
        updatedValues = collectedResult[0].split()[1:-1] + [
            str(currentBalance - installmentAmount)
        ]
        db.Update(
            "BankAccount",
            updatedValues,
            f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
        )

    @staticmethod
    def PayTheBill():
        while True:
            billingID = Application.ReceiveUserInput("billingID", "Bills", "select")
            paymentCode = Application.ReceiveUserInput("paymentCode", "Bills", "select")
            billCollectedResult = db.Select("Bills", f'billingID=="{billingID}"')
            if not billCollectedResult:
                print("Billing ID not exists.")
                continue
            collectedPaymentCode = billCollectedResult[0].split()[1:][-1]
            if not paymentCode == collectedPaymentCode:
                print("Wrong payment code.")
                continue
            break
        billAmount = int(billCollectedResult[0].split()[2])
        while True:
            number = Application.ReceiveUserInput("number", "BankAccount", "select")
            collectedResult = db.Select(
                "BankAccount",
                f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
            )
            if not collectedResult:
                print("The entered card number is incorrect.")
                continue
            break
        currentBalance = int(collectedResult[0].split()[-1])
        updatedValues = collectedResult[0].split()[1:-1] + [
            str(currentBalance - billAmount)
        ]
        db.Update(
            "BankAccount",
            updatedValues,
            f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
        )
        db.Delete("Bills", f'billingID=="{billingID}"')

    @classmethod
    def AccountManagmentMenu(cls):
        while True:
            print("What do you want to do:")
            print("1. View current account information.")
            print("2. Open a new account.")
            print("3. Rename the alias of the current account.")
            print("0. Back to bank menu.")
            userInput = input()
            if userInput == "1":
                while True:
                    print("Enter your current account alias.")
                    alias = Application.ReceiveUserInput(
                        "alias", "BankAccount", "select"
                    )
                    collectedResult = db.Select("BankAccount", f'alias=="{alias}"')
                    if not collectedResult:
                        print("Alias not exists.")
                        continue
                    cls.DisplayInformation(
                        f'ownerNationalID=="{Application.ownerNationalID}" AND alias=="{alias}"'
                    )
                    break
            elif userInput == "2":
                cls.OpenAnAccount()

            elif userInput == "3":
                while True:
                    print("Enter your current account alias.")
                    alias = Application.ReceiveUserInput(
                        "alias", "BankAccount", "select"
                    )
                    collectedResult = db.Select(
                        "BankAccount",
                        f'alias=="{alias}" AND ownerNationalID=="{Application.ownerNationalID}"',
                    )
                    if not collectedResult:
                        print("Alias not exists.")
                        continue
                    cls.ChangeAlias(collectedResult[0])
                    break
            else:
                break

    @staticmethod
    def ChangeAlias(currentAccountInfo):
        print("Enter your new account alias.")
        newAlias = Application.ReceiveUserInput("alias", "BankAccount", "insert")
        currentAlias = currentAccountInfo.split()[3]
        updatedValues = (
            currentAccountInfo.split()[1:3]
            + [newAlias]
            + currentAccountInfo.split()[4:]
        )
        db.Update("BankAccount", updatedValues, f'alias=="{currentAlias}"')


db = Database()
app = Application()
