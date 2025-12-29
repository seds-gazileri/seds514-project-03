from tabulate import tabulate

table = [["Celestial Body", "Equator", 1234],["Sun",696000,1989100000],["Earth",6371,5973.6], ["Moon",1737,73.5],["Mars",3390,641.85], ["Venus", 1234, 56789]]

print(tabulate(table, headers="firstrow"))

# tabulate(table)