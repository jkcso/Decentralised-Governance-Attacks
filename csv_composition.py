import csv

a = {'one': 95, 'two': 1800, 'three': 8987123}

print("")

a["apple"] = 1

with open('test.csv', 'w') as f:
    w = csv.DictWriter(f, a.keys())
    w.writeheader()
    w.writerow(a)
