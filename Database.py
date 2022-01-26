from os import path
from re import sub
from collections import namedtuple, defaultdict


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

    def Insert(self, tableName, values):
        filename = tableName + ".txt"
        if tableName in self.tables:
            if self.CheckInsertConditions(fields, values, tableName):
                with open(filename, "a") as f:
                    f.write("id " + " ".join(values) + "\n")
        else:
            print(f"There is no table with name {tableName}.")


db = Database()

while True:
    instruction = list(input("$ ").split())
    if instruction[0] == "INSERT":
        tableName = instruction[2]
        values = sub("[()]", "", instruction[-1][:-1]).split(",")
        db.Insert(tableName, values)
