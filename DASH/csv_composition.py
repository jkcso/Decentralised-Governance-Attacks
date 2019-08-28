import csv

a = {'one': 95, 'two': 1800, 'three': 8987123}

print("")

a.update({'trial': 2,
          'new': 4})

a['Maximum Coin Supply'] = 1


def create_csv(csv_filename):
    with open(csv_filename + '.csv', 'w') as f:
        w = csv.DictWriter(f, a.keys())
        w.writeheader()
        w.writerow(a)


create_csv('test')
