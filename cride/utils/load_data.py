import csv

def import_data_circles():
    dir_csv = './circles.csv'

    with open(dir_csv, 'rb') as f:
        reader = csv.reader(f, delimiter=';')
        import pdb
        for row in reader:
            pdb.set_trace()
            print(row)



import_data_circles();
