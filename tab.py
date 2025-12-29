from tabulate import tabulate

# table = [["Celestial Body", "Equator", 1234],["Sun",696000,1989100000],["Earth",6371,5973.6], ["Moon",1737,73.5],["Mars",3390,641.85], ["Venus", 1234, 56789]]

# print(tabulate(table, headers="firstrow"))

# # tabulate(table)

data = {
    "name": ["Alice", "Bob", "Carol"],
    "age": [30, 25, 35]
}

# INVALID: firstrow makes no sense here
result = tabulate(data, headers="firstrow")

print(result)
















