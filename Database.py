from os import path
from re import sub, finditer, split
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
                    f.write("id " + " ".join(fieldNames) + "\n")

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
                if eval(replacedConditions):
                    collectedResults.append(line.strip())
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

    def Insert(self, tableName, values):
        filename = tableName + ".txt"
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckInsertConditions(fields, values, tableName):
                with open(filename, "a") as f:
                    f.write("id " + " ".join(values) + "\n")
        else:
            print(f"There is no table with name {tableName}.")

    def Delete(self, tableName, conditions):
        filename = tableName + ".txt"
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckFieldNamesValidity(fields, conditions):
                collectedResults = self.FindCorrespondingData(tableName, conditions)
                with open(filename, "r+") as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        if not line.strip() in collectedResults:
                            f.write(line)
                    f.truncate()
        else:
            print(f"There is no table with name {tableName}.")

    def Select(self, tableName, conditions):
        if tableName in self.tables:
            fields = self.tables[tableName]
            if self.CheckFieldNamesValidity(fields, conditions):
                collectedResults = self.FindCorrespondingData(conditions)
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
                collectedResults = self.FindCorrespondingData(conditions)
                with open(filename, "r+") as f:
                    lines = f.readlines()
                    f.seek(0)
                    for line in lines:
                        if line.strip() in collectedResults:
                            f.write("id " + " ".join(values) + "\n")
                        else:
                            f.write(line)
                    f.truncate()
        else:
            print(f"There is no table with name {tableName}.")


db = Database()
while True:
    instruction = list(input("$ ").split())
    if instruction[0] == "INSERT":
        tableName = instruction[2]
        values = sub("[()]", "", instruction[-1][:-1]).split(",")
        db.Insert(tableName, values)
