from fileinput import filename
from os import path
from collections import namedtuple, defaultdict


class Database:
    def __init__(self) -> None:
        self.tables = defaultdict(list)
        try:
            self.ExtractTablesData()
        except FileNotFoundError:
            print("schema.txt Not Found.")
        self.MakeDatabaseFiles()

    def ExtractTablesData(self):
        with open("schema.txt", "r") as schema:
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
                print("test")
                for field in fields:
                    fieldNames.append(field.fieldName)
                with open(fileName, "a") as f:
                    f.write("id " + " ".join(fieldNames))


db = Database()
