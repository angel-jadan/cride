import csv
from cride.circles.models import Circle

def import_data_circles():
    dir_csv = "./circles.csv"

    with open(dir_csv, newline='') as f:
        read_file = csv.DictReader(f)
        for row in read_file:
            circle = Circle(
                name=row['name'],
                slug_name=row['slug_name'],
                is_public=True if row['is_public'] == '1' else False,
                verified=True if row['name'] == '1' else False,
                members_limit=row['members_limit']
            )
            circle.save()
        
    f.close()
    print( "Carga inicial de Circulos completado.") 

import_data_circles()
