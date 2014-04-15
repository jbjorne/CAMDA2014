import csv, sqlite3
import re
import os, sys

dataPath = os.path.expanduser("~/data/CAMDA2014/ICGC/Breast_Invasive_Carcinoma-TCGA-US/")

def defineColumns(header, columnTypes, defaultType="text"):
    columns = []
    for i in range(len(header)):
        if i in columnTypes:
            columns += columnTypes[i]
        else:
            matched = False
            for key in columnTypes:
                if key is not int and key.match(header[i]):
                    columns.append((header[i], columnTypes[key]))
                    matched = True
                    break
            if not matched:
                columns.append((header[i], defaultType))
    return columns

def defineTable(name, columns):
    return "create table " + tableName + "(" + ",".join([x[0] + " " + x[1] for x in columns]) + ")"

def defineInsert(name, columns):
    return "insert into " + tableName + "(" + ",".join([x[0] for x in columns]) + ")" + " values (" + ",".join(["?"]*len(columns)) + ")"

con = sqlite3.connect(dataPath + "BRCA-US.sqlite")
data = csv.reader(open(dataPath + "clinical.BRCA-US.tsv"), delimiter='\t')
header = data.next()

tableName = "clinical"
columns = defineColumns(header, {re.compile(".*_age.*"):"int", re.compile(".*_time.*"):"int", re.compile(".*_interval.*"):"int"})
con.execute("DROP TABLE IF EXISTS " + tableName + ";")
con.execute(defineTable(tableName, columns))
insert = defineInsert(tableName, columns)
#print insert
con.executemany(insert, data)

con.commit()
con.close()

#con.execute("create table person(firstname, lastname)")
#con.executemany("insert into person(firstname, lastname) values (?, ?)", persons)
