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
        try:
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
        except KeyboardInterrupt:
            self.MainMenu()

    @staticmethod
    def BankingServiceMenu():
        try:
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
        except KeyboardInterrupt:
            Application.BankingServiceMenu()

    def IntegerCondition(string, *useless):
        if not string.isdigit() and not string[1:].isdigit():
            print("Input must be an integer.")
            return False
        if not int(string) >= 0:
            print("Input must be non-negative.")
            return False
        return True

    def UniquenessCondition(fieldValue, fieldName, tableName):
        if db.Select(tableName, f'{fieldName}=="{fieldValue}"'):
            print(f"Input must be unique, {fieldValue} is already exists.")
            return False
        return True

    def CharCondition(fieldValue, fieldName, tableName):
        for field in db.tables[tableName]:
            if field.fieldName == fieldName:
                field = field
                break
        legalCount = int(sub("[()]", "", field.fieldType.replace("CHAR", "")))
        if len(fieldValue) > legalCount:
            print(f"{fieldValue}'s number of characters exceeded {legalCount}.")
            return False

        if not len(fieldValue.split()) == 1:
            print(f"illegal input.")
            return False
        return True

    def YesNoCondition(string, *useless):
        if string not in ["1", "2"]:
            return False
        return True

    def ReceiveUserInput(messsage, fieldName, tableName, *conditions):
        while True:
            print(messsage)
            userInput = input()
            for condition in conditions:
                if not condition(userInput, fieldName, tableName):
                    break
            else:
                return userInput
            continue

    @classmethod
    def SignUp(cls):
        name = cls.ReceiveUserInput(
            "Enter your full name:",
            "name",
            "User",
            cls.CharCondition,
        )
        nationalID = cls.ReceiveUserInput(
            "Enter your national ID:",
            "nationalID",
            "User",
            cls.UniquenessCondition,
            cls.IntegerCondition,
        )
        password = cls.ReceiveUserInput(
            "Enter your password:",
            "password",
            "User",
            cls.UniquenessCondition,
            cls.CharCondition,
        )
        phoneNumber = cls.ReceiveUserInput(
            "Enter your phone number:",
            "phoneNumber",
            "User",
            cls.UniquenessCondition,
            cls.IntegerCondition,
        )
        email = cls.ReceiveUserInput(
            "Enter your email:",
            "email",
            "User",
            cls.UniquenessCondition,
            cls.CharCondition,
        )
        joinedAt = str(date.today())
        db.Insert("User", [name, nationalID, password, phoneNumber, email, joinedAt])

    @classmethod
    def SignIn(cls):
        while True:
            nationalID = cls.ReceiveUserInput(
                "Enter your national ID:", "nationalID", "User", cls.IntegerCondition
            )
            collectedResult = db.Select("User", f'nationalID=="{nationalID}"')
            if not collectedResult:
                print("National ID not exists.")
                continue
            password = cls.ReceiveUserInput(
                "Enter your password:", "password", "User", cls.CharCondition
            )
            collectedPassword = collectedResult[0].split()[3]
            if not password == collectedPassword:
                print("Wrong password!")
                continue
            break
        Application.ownerNationalID = nationalID
        cls.BankingServiceMenu()


class BankSystem:

    installmentDuration = 10

    @staticmethod
    def OpenAnAccount():
        accountType = Application.ReceiveUserInput(
            "Enter your account type:",
            "type",
            "BankAccount",
            Application.CharCondition,
        )
        number = "".join(str(randint(1, 9)) for _ in range(10))
        alias = Application.ReceiveUserInput(
            "Enter your account alias:",
            "alias",
            "BankAccount",
            Application.UniquenessCondition,
            Application.CharCondition,
        )
        password = Application.ReceiveUserInput(
            "Enter your account password:",
            "password",
            "BankAccount",
            Application.CharCondition,
        )
        balance = Application.ReceiveUserInput(
            "Enter the amount of money you want in your bank account:",
            "balance",
            "BankAccount",
            Application.IntegerCondition,
        )
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
        print(f"Your bank card code is: {number}")

    @staticmethod
    def DisplayInformation(condition=None):
        if condition is None:
            accountsCollectedResult = db.Select(
                "BankAccount", f'ownerNationalID=="{Application.ownerNationalID}"'
            )
        else:
            accountsCollectedResult = db.Select("BankAccount", condition)
        for i, account in enumerate(accountsCollectedResult, 1):
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
            userInput = Application.ReceiveUserInput(
                "What method do you prefer to determine the source card?\n1. By alias\n2. By card number",
                "",
                "",
                Application.YesNoCondition,
            )
            if userInput == "1":
                sourceAlias = Application.ReceiveUserInput(
                    "Enter your account alias.",
                    "alias",
                    "BankAccount",
                    Application.CharCondition,
                )
                sourceCollectedResult = db.Select(
                    "BankAccount",
                    f'alias=="{sourceAlias}" AND ownerNationalID=="{Application.ownerNationalID}"',
                )
            elif userInput == "2":
                sourceNumber = Application.ReceiveUserInput(
                    "Enter your account number.",
                    "number",
                    "BankAccount",
                    Application.IntegerCondition,
                )
                sourceCollectedResult = db.Select(
                    "BankAccount",
                    f'number=="{sourceNumber}" AND ownerNationalID=="{Application.ownerNationalID}"',
                )
            if not sourceCollectedResult:
                print("Account number/alias not exists.")
                continue
            sourceNumber = sourceCollectedResult[0].split()[2]
            password = Application.ReceiveUserInput(
                "Enter your account password.",
                "password",
                "BankAccount",
                Application.CharCondition,
            )
            collectedPassword = sourceCollectedResult[0].split()[4]
            if not password == collectedPassword:
                print("Wrong password!")
                continue
            break
        while True:
            userInput = Application.ReceiveUserInput(
                "What method do you prefer to determine the destination card?\n1. Select the destination card number from the most frequently used numbers.\n2. Enter the new destination number.",
                "",
                "",
                Application.YesNoCondition,
            )
            if userInput == "1":
                print("Choose the number of one of the most used accounts below.")
                frequentlyUsedCollectedResult = db.Select(
                    "FrequentlyUsedAccounts",
                    f'ownerNationalID=="{Application.ownerNationalID}"',
                )
                frequentlyUsedAccounts = []
                for i, result in enumerate(frequentlyUsedCollectedResult, 1):
                    frequentlyUsedAccounts.append(result.split()[2])
                    print(f"{i}: {result.split()[2]}")
                if len(frequentlyUsedAccounts) == 0:
                    print("You have no frequently used accounts.")
                    continue
                userResponse = input()
                if not userResponse in frequentlyUsedAccounts:
                    print("Your selection is not listed.")
                    continue
                destinationNumber = userResponse
            elif userInput == "2":
                destinationNumber = Application.ReceiveUserInput(
                    "Enter destination card number.",
                    "number",
                    "BankAccount",
                    Application.IntegerCondition,
                )
            destinationCollectedResult = db.Select(
                "BankAccount", f'number=="{destinationNumber}"'
            )
            if not destinationCollectedResult:
                print("Destination number not exists.")
                continue
            if destinationCollectedResult == sourceCollectedResult:
                print("Can't transfer to same number.")
                continue
            moneyAmount = Application.ReceiveUserInput(
                "Enter the amount you want to transfer.",
                "amount",
                "Transactions",
                Application.IntegerCondition,
            )
            happenedAt = str(date.today())
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
            destinationCurrentBalance = int(
                destinationCollectedResult[0][1:].split()[-1]
            )
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
        while True:
            destinationNumber = Application.ReceiveUserInput(
                "Enter the destination account number to which you want to deposit the remaining money:",
                "number",
                "BankAccount",
                Application.IntegerCondition,
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
            destinationUpdatedValues = destinationCollectedResult[0][1:].split()[
                :-1
            ] + [str(destinationCurrentBalance + int(moneyAmount))]
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
            n = Application.ReceiveUserInput(
                "How many numbers you want to mark as frequently used?",
                "",
                "",
                Application.IntegerCondition,
            )
            print("Enter numbers that you want to mark as frequently used.")
            for _ in range(int(n)):
                numbers.append(
                    Application.ReceiveUserInput(
                        "Enter the account number:",
                        "number",
                        "BankAccount",
                        Application.IntegerCondition,
                    )
                )
            for number in numbers:
                collectedResult = db.Select(
                    "BankAccount",
                    f'number=="{number}"',
                )
                if not collectedResult:
                    print("The entered number not exists.")
                    break
                collectedResults.append(collectedResult[0])
            else:
                break
            continue
        for number, collectedResult in zip(numbers, collectedResults):
            alias = collectedResult.split()[3]
            db.Insert(
                "FrequentlyUsedAccounts", [alias, number, Application.ownerNationalID]
            )

    @staticmethod
    def CloseAccount():
        while True:
            sourceNumber = Application.ReceiveUserInput(
                "Enter your account number:",
                "number",
                "BankAccount",
                Application.IntegerCondition,
            )
            password = Application.ReceiveUserInput(
                "Enter your account password:",
                "password",
                "BankAccount",
                Application.CharCondition,
            )
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
        sourceCurrentBalance = int(sourceCollectedResult[0][1:].split()[-1])
        if sourceCurrentBalance > 0:
            BankSystem.TransferRemainingMoney(sourceNumber, str(sourceCurrentBalance))
        db.Delete("BankAccount", f'number=="{sourceNumber}"')

    @classmethod
    def LoanRequest(cls):
        moneyAmount = int(
            Application.ReceiveUserInput(
                "How much money do you ask for?", "", "", Application.IntegerCondition
            )
        )
        periods = int(
            Application.ReceiveUserInput(
                "How many periods do you intend to pay?",
                "",
                "",
                Application.IntegerCondition,
            )
        )
        while True:
            userInput = Application.ReceiveUserInput(
                "What method do you prefer to determine the source card?\n1. By card number\n2. By alias",
                "",
                "",
                Application.YesNoCondition,
            )
            if userInput == "1":
                number = Application.ReceiveUserInput(
                    "Enter your account number:",
                    "number",
                    "BankAccount",
                    Application.IntegerCondition,
                )
                collectedResult = db.Select(
                    "BankAccount",
                    f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
                )
            elif userInput == "2":
                alias = Application.ReceiveUserInput(
                    "Enter your account alias:",
                    "alias",
                    "BankAccount",
                    Application.CharCondition,
                )
                collectedResult = db.Select(
                    "BankAccount",
                    f'alias=="{alias}" AND ownerNationalID=="{Application.ownerNationalID}"',
                )
            if not collectedResult:
                print("The entered card number/alias is incorrect.")
                continue
            break
        number = collectedResult[0].split()[2]
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
        finalInstallmentAmount = moneyAmount - (eachLoanInstallmentAmount * periods)
        t = Timer(
            cls.installmentDuration,
            cls.LoanInstallmentPayment,
            args=[
                eachLoanInstallmentAmount,
                number,
                periods - 1,
                finalInstallmentAmount,
            ],
        )
        t.start()

    @classmethod
    def LoanInstallmentPayment(cls, installmentAmount, number, periods, finalAmount):
        if periods != 1:
            t = Timer(
                cls.installmentDuration,
                cls.LoanInstallmentPayment,
                args=[installmentAmount, number, periods - 1, finalAmount],
            )
            t.start()
        else:
            t = Timer(
                cls.installmentDuration,
                cls.LoanInstallmentPayment,
                args=[
                    installmentAmount + finalAmount,
                    number,
                    periods - 1,
                    finalAmount,
                ],
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
            billingID = Application.ReceiveUserInput(
                "Enter the billing ID:",
                "billingID",
                "Bills",
                Application.IntegerCondition,
            )
            paymentCode = Application.ReceiveUserInput(
                "Enter the payment code:",
                "paymentCode",
                "Bills",
                Application.IntegerCondition,
            )
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
            number = Application.ReceiveUserInput(
                "Enter the account number with which you want to pay the bill:",
                "number",
                "BankAccount",
                Application.IntegerCondition,
            )
            collectedResult = db.Select(
                "BankAccount",
                f'number=="{number}" AND ownerNationalID=="{Application.ownerNationalID}"',
            )
            if not collectedResult:
                print("The entered card number is incorrect.")
                continue
            currentBalance = int(collectedResult[0].split()[-1])
            if not currentBalance >= billAmount:
                print("Not enough money.")
                continue
            break
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
                    alias = Application.ReceiveUserInput(
                        "Enter your current account alias.",
                        "alias",
                        "BankAccount",
                        Application.CharCondition,
                    )
                    collectedResult = db.Select(
                        "BankAccount",
                        f'alias=="{alias}" AND ownerNationalID=="{Application.ownerNationalID}"',
                    )
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
                    alias = Application.ReceiveUserInput(
                        "Enter your current account alias.",
                        "alias",
                        "BankAccount",
                        Application.CharCondition,
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
        newAlias = Application.ReceiveUserInput(
            "Enter your new account alias.",
            "alias",
            "BankAccount",
            Application.CharCondition,
            Application.UniquenessCondition,
        )
        currentAlias = currentAccountInfo.split()[3]
        updatedValues = (
            currentAccountInfo.split()[1:3]
            + [newAlias]
            + currentAccountInfo.split()[4:]
        )
        db.Update("BankAccount", updatedValues, f'alias=="{currentAlias}"')


db = Database()
app = Application()
