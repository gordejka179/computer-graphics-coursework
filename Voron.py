import matplotlib.pyplot as plt
from scipy.spatial import Voronoi
import time
import tracemalloc

def Voronoi_and_Delaunay(points):
    new_points = []
    for p in points:
        new_point = [p[0], p[1]]
        new_points.append(new_point)
    points = new_points
    vor = Voronoi(points)
    edges = []
    
    #Строим рёбра Делоне из диаграммы Вороного
    #Две точки соединяются ребром, если их ячейки Вороного имеют общее ребро
    for ridge in vor.ridge_points:
        point1, point2 = ridge
        edges.append((point1, point2))
    
    return {
        'points': points,
        'edges': edges
    }

def plot_results(delaunay):
    points = delaunay['points']
    edges = delaunay['edges']
    #fig - вся фигура
    #ax - область для рисования графиков
    #figsize - размер fig
    fig, ax = plt.subplots(figsize=(12, 9))
    x = []
    y = []
    for p in points:
        x.append(p[0])
        y.append(p[1])

    #точки:
    ax.scatter(x, y, c='red', s=50, zorder=5)
    
    #рёбра:
    for edge in edges:
        point1 = points[edge[0]]
        point2 = points[edge[1]]
        ax.plot([point1[0], point2[0]], [point1[1], point2[1]], 
                'g-', linewidth=2, alpha=0.7)
    
    ax.set_title('Триангуляция Делоне')

    #одинаковый масштаб
    ax.set_aspect('equal')
    #сетка
    ax.grid(True, alpha=0.3)
    plt.show()


def main():
    points = []
    with open('points.txt', 'r') as file:
        n = int(file.readline().strip()) 
        for i in range(n):
            x, y = map(float, file.readline().split())
            points.append([x, y])

    tracemalloc.start() 
    start_time = time.time()
    delaunay = Voronoi_and_Delaunay(points)
    end_time = time.time()
    execution_time = end_time - start_time

    current, peak = tracemalloc.get_traced_memory()

    # в килобайтах
    print(peak / 1024)
    tracemalloc.stop()
    print("время выполнения: " + str(round(execution_time, 5)) + " секунд")

    plot_results(delaunay)

if __name__ == "__main__":
    main()