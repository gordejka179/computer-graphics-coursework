import random


def generate_points_file(filename, n_points):
    points = set()
    while len(points) < n_points:
        x = random.randint(-1000, 1000)
        y = random.randint(-1000, 1000)
        points.add(str(x) + " " + str(y))
    
    with open(filename, 'w') as file:
        file.write(str(n_points) + "\n")
        file.write("\n".join(points))
        
generate_points_file('points.txt', 1000000)