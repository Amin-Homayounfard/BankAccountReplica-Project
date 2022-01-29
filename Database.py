from os import path
from re import sub, finditer, split, findall
from collections import namedtuple, defaultdict
from functools import reduce


class Database:
    schemaFilename = "schema.txt"

    def __init__(self) -> None:
        self.tables = defaultdict(list)
        try:
            self.ExtractTablesData()
        except FileNotFoundError:
            raise f"{Database.schemaFilename} Not Found."
        self.MakeDatabaseFiles()

    def ExtractTablesData(self):
        with open(Database.schemaFilename, "r") as schema:
            data = schema.read()
            tables = data.split("\n\n")
            for table in tables:
                fields = table.split("\n")
                tableName = fields[0]
                for field in fields[1:]:
                    parts = field.split()
                    fieldName = parts[0]
                    if len(parts) == 3:
                        isUnique = True
                        fieldType = parts[2]
                    elif len(parts) == 2:
                        isUnique = False
                        fieldType = parts[1]

                    self.tables[tableName].append(
                        namedtuple(
                            fieldName.capitalize(),
                            ["fieldName", "isUnique", "fieldType"],
                        )(fieldName, isUnique, fieldType)
                    )

    def MakeDatabaseFiles(self):
        for tableName, fields in self.tables.items():
            fileName = tableName + ".txt"
            fieldNames = []
            if not path.exists(fileName):
                for field in fields:
                    fieldNames.append(field.fieldName)
                with open(fileName, "a") as f:
                    f.write(f'id {" ".join(fieldNames)}\n')

    def CheckInsertConditions(self, fields, values, tableName):
        for i, field in enumerate(fields):
            fieldValue = values[i]
            if field.isUnique:
                with open(tableName + ".txt", "r") as f:
                    lines = f.read().splitlines()[1:]
                    for line in lines:
                        if line.split()[i + 1] == fieldValue:
                            print(f"{fieldValue} is already exist.")
                            return False
            if field.fieldType == "INTEGER" and not fieldValue.isdigit():
                print(f"{fieldValue} must be an integer.")
                return False
            elif "CHAR" in field.fieldType and not fieldValue.isalpha():
                print(f"{fieldValue} must be characters.")
                return False
            elif "CHAR" in field.fieldType and fieldValue.isalpha():
                legalCount = int(sub("[()]", "", field.fieldType.replace("CHAR", "")))
                if len(fieldValue) > legalCount:
                    print(f"{fieldValue}'s number of characters exceeded {legalCount}.")
                    return False
        return True

    def ModifyConditions(self, conditions):
        quotationMarkIndices = [m.start() for m in finditer('"', conditions)]
        conditions = list(conditions)
        for i, index in enumerate(quotationMarkIndices):
            if i % 2 == 0:
                conditions[index] = "("
            else:
                conditions[index] = ")"

        conditions = "".join(conditions)
        modifiedConditions = split(r"(?<=\))OR|(?<=\))AND", conditions)
        return modifiedConditions

    def FindCorrespondingData(self, tableName, conditions):
        filename = tableName + ".txt"
        conditions = conditions.replace(" ", "")
        modifiedConditions = self.ModifyConditions(conditions)
        collectedResults = []
        with open(filename, "r") as f:
            columns = f.readline().split()
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                replacements = dict()
                for condition in modifiedConditions:
                    condition = sub("[()]", "", condition)
                    fieldName, fieldValue = split(r"==|!=", condition)
                    toReadColumnIndex = columns.index(fieldName)
                    if (
                        line.split()[toReadColumnIndex] == fieldValue
                        and "==" in condition
                    ):
                        replacements[f'{fieldName}=="{fieldValue}"'] = "1"
                    elif (
                        line.split()[toReadColumnIndex] == fieldValue
                        and "!=" in condition
                    ):
                        replacements[f'{fieldName}!="{fieldValue}"'] = "0"
                    elif (
                        line.split()[toReadColumnIndex] != fieldValue
                        and "==" in condition
                    ):
                        replacements[f'{fieldName}=="{fieldValue}"'] = "0"
                    elif (
                        line.split()[toReadColumnIndex] != fieldValue
                        and "!=" in condition
                    ):
                        replacements[f'{fieldName}!="{fieldValue}"'] = "1"

                replacedConditions = reduce(
                    lambda x, y: x.replace(*y), replacements.items(), conditions
                )
                replacedConditions = replacedConditions.replace("AND", " and ").replace(
                    "OR", " or "
                )
                try:
                    if eval(replacedConditions):
                        collectedResults.append(line.strip())
                except Exception as error:
                    print(f"{error} error is happened.")
                    return
        return collectedResults

    def CheckFieldNamesValidity(self, validFields, conditions):
        conditions = conditions.replace(" ", "")
        modifiedConditions = self.ModifyConditions(conditions)
        fields = []
        for condition in modifiedConditions:
            condition = sub("[()]", "", condition)
            fieldName = split(r"==|!=", condition)[0]
            fields.append(fieldName)
        for field in fields:
            if not field in [field.fieldName for field in validFields]:
                print(f'There is no field with name "{field}"')
                return False
        return True

    def CheckInstructionValidity(self, instruction):
        insertStructure = "INSERT INTO <table_name> VALUES (<field1_value>,<field2_value>,<field3_value>);"
        selectStructure = 'SELECT FROM <table_name> WHERE <field_name>=="<field_value>" OR <field_name>=="<field_value>";'
        deleteStructure = 'DELETE FROM <table_name> WHERE <field_name>=="<field_value>" OR <field_name>=="<field_value>";'
        updateStructure = 'UPDATE <table_name> WHERE <field_name>=="<field_value>" OR <field_name>=="<field_value>" VALUES (<field1_value>,<field2_value>,<field3_value>);'
        if instruction[-1] != ";":
            print(f'Instruction must ends with ";".')
            return False
        instruction = instruction[:-1]
        instruction = instruction.lower().split()
        if instruction[0] == "insert":
            if not instruction[1] == "into":
                print(
                    f"Insert instruction must have the following structure:\n{insertStructure}"
                )
                return False
            if not instruction[-2] == "values":
                print(
                    f"Insert instruction must have the following structure:\n{insertStructure}"
                )
                return False
            fieldValues = instruction[-1]
            if not fieldValues.startswith("(") or not fieldValues.endswith(")"):
                print(f"Field values must be wraped in parentheses.")
                return False

        elif instruction[0] == "select":
            if not instruction[1] == "from":
                print(
                    f"Select instruction must have the following structure:\n{selectStructure}"
                )
                return False
            if not instruction[3] == "where":
                print(
                    f"Select instruction must have the following structure:\n{selectStructure}"
                )
                return False
            instruction = " ".join(instruction)
            conditionParts = instruction.split("where")[1]
            if not len(findall("\(", conditionParts)) == len(
                findall("\)", conditionParts)
            ):
                print("Condition section parentheses are unbalanced.")
                return False
            for part in conditionParts.split():
                part = sub("[()]", "", part)
                part = part.replace(" ", "")
                if "==" in part or "!=" in part:
                    condition = split(r"==|!=", part)
                    if not len(condition) == 2:
                        print(
                            f"Select instruction must have the following structure:\n{selectStructure}"
                        )
                        return False
                    fieldValue = condition[-1]
                    if not fieldValue.startswith('"') or not fieldValue.endswith('"'):
                        print("Each field value must be wraped in quotation marks.")
                        return False
                else:
                    if not part == "and" and not part == "or":
                        print("Only AND/OR can be used as logical expretion.")
                        return False

        elif instruction[0] == "delete":
            if not instruction[1] == "from":
                print(
                    f"Delete instruction must have the following structure:\n{deleteStructure}"
                )
                return False
            if not instruction[3] == "where":
                print(
                    f"Delete instruction must have the following structure:\n{deleteStructure}"
                )
                return False
            instruction = " ".join(instruction)
            conditionParts = instruction.split("where")[1]
            if not len(findall("\(", conditionParts)) == len(
                findall("\)", conditionParts)
            ):
                print("Condition section parentheses are unbalanced.")
                return False
            for part in conditionParts.split():
                part = sub("[()]", "", part)
                part = part.replace(" ", "")
                if "==" in part or "!=" in part:
                    condition = split(r"==|!=", part)
                    if not len(condition) == 2:
                        print(
                            f"Select instruction must have the following structure:\n{deleteStructure}"
                        )
                        return False
                    fieldValue = condition[-1]
                    if not fieldValue.startswith('"') or not fieldValue.endswith('"'):
                        print("Each field value must be wraped in quotation marks.")
                        return False
                else:
                    if not part == "and" and not part == "or":
                        print("Only AND/OR can be used as logical expretion.")
                        return False

        elif instruction[0] == "update":
            if not instruction[2] == "where":
                print(
                    f"Update instruction must have the following structure:\n{updateStructure}"
                )
                return False
            if not instruction[-2] == "values":
                print(
                    f"Update instruction must have the following structure:\n{updateStructure}"
                )
                return False
            instruction = " ".join(instruction)
            conditionParts, fieldValues = (
                split(r"where|values", instruction)[1],
                split(r"where|values", instruction)[2].replace(" ", ""),
            )
            if not len(findall("\(", conditionParts)) == len(
                findall("\)", conditionParts)
            ):
                print("Condition section parentheses are unbalanced.")
                return False
            for part in conditionParts.split():
                part = sub("[()]", "", part)
                if "==" in part or "!=" in part:
                    condition = split(r"==|!=", part)
                    if not len(condition) == 2:
                        print(
                            f"Select instruction must have the following structure:\n{updateStructure}"
                        )
                        return False
                    fieldValue = condition[-1]
                    if not fieldValue.startswith('"') or not fieldValue.endswith('"'):
                        print("Each field value must be wraped in quotation marks.")
                        return False
                else:
                    if not part == "and" and not part == "or":
                        print("Only AND/OR can be used as logical expretion.")
                        return False
            if not fieldValues.startswith("(") or not fieldValues.endswith(")"):
                print(f"Field values must be wraped in parentheses.")
                return False
        return True

    def FollowInstruction(self, instruction):
        instruction = instruction[:-1].split()
        if instruction[0].lower() == "insert":
            tableName = instruction[2]
            fieldValues = sub("[()]", "", instruction[-1]).split(",")
            self.Insert(tableName, fieldValues)
        elif instruction[0].lower() == "select":
            tableName = instruction[2]
            conditions = " ".join(instruction[4:])
            print(self.Select(tableName, conditions))
        elif instruction[0].lower() == "delete":
            tableName = instruction[2]
            conditions = " ".join(instruction[4:])
            self.Delete(tableName, conditions)
        elif instruction[0].lower() == "update":
            tableName = instruction[1]
            conditions = " ".join(instruction[3:-2])
            fieldValues = instruction[-1]
            self.Update(tableName, fieldValues, conditions)

    def Insert(self, tableName, values):
        filename = tableName + ".txt"
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckInsertConditions(fields, values, tableName):
                with open(filename, "r+") as f:
                    lineIndexToWrite = len(f.readlines())
                    id = lineIndexToWrite
                    f.seek(0, 2)
                    f.write(f'{id} {" ".join(values)}\n')
        else:
            print(f"There is no table with name {tableName}.")

    def Delete(self, tableName, conditions):
        filename = tableName + ".txt"
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckFieldNamesValidity(fields, conditions):
                collectedResults = self.FindCorrespondingData(tableName, conditions)
                with open(filename, "r+") as f:
                    firstLine = f.readline()
                    lines = f.readlines()
                    f.seek(0)
                    f.write(firstLine)
                    id = 1
                    for line in lines:
                        if not line.strip() in collectedResults:
                            lineWithoutID = " ".join(line.split()[1:]) + "\n"
                            f.write(f"{id} {lineWithoutID}")
                            id += 1
                    f.truncate()
        else:
            print(f"There is no table with name {tableName}.")

    def Select(self, tableName, conditions):
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckFieldNamesValidity(fields, conditions):
                collectedResults = self.FindCorrespondingData(tableName, conditions)
                return collectedResults
        else:
            print(f"There is no table with name {tableName}.")

    def Update(self, tableName, values, conditions):
        filename = tableName + ".txt"
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckFieldNamesValidity(
                fields, conditions
            ) and self.CheckInsertConditions(fields, values, tableName):
                collectedResults = self.FindCorrespondingData(tableName, conditions)
                with open(filename, "r+") as f:
                    firstLine = f.readline()
                    lines = f.readlines()
                    f.seek(0)
                    f.write(firstLine)
                    for id, line in enumerate(lines, 1):
                        if line.strip() in collectedResults:
                            f.write(f'{id} {" ".join(values)}\n')
                        else:
                            lineWithoutID = " ".join(line.split()[1:]) + "\n"
                            f.write(f"{id} {lineWithoutID}")
                    f.truncate()
        else:
            print(f"There is no table with name {tableName}.")


db = Database()
while True:
    instruction = input(">>> ")
    if instruction != "exit":
        if db.CheckInstructionValidity(instruction):
            db.FollowInstruction(instruction)
    else:
        break
