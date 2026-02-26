import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull
import tracemalloc
import time

class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    #точка с противоположными координатами
    def __neg__(self):
        return Point(-self.x, -self.y, -self.z)

#скалярное произвдение векторов
def dot_product(A, B):
    return A.x * B.x + A.y * B.y + A.z * B.z

#векторное произведение
def cross_product(A, B):
    return Point(A.y * B.z - A.z * B.y, A.z * B.x - A.x * B.z, A.x * B.y - A.y * B.x)

#ищем точку, которая гарантированно будет лежать внутри выпуклой оболочки
def find_centroid(points):
    n = len(points)
    centroid = Point(0, 0, 0)

    for point in points:
        centroid.x += point[0]
        centroid.y += point[1] 
        centroid.z += point[2]

    centroid.x = centroid.x / n
    centroid.y = centroid.y / n
    centroid.z = centroid.z / n
    return centroid

#возращаем массив из точек, каждая из которых является отображением
#точки из плоскости XY на параболоид z = x² + y²
def lift_to_paraboloid(points_2d):
    points_3d = []
    for point in points_2d:
        x = point.x
        y = point.y
        z = x * x + y * y
        points_3d.append([x, y, z])
    return points_3d

#Работаем с правой тройкой векторных осей: OX, OY, OZ
#Будем считать, что точки грани выпуклой оболочки 
#ориентированы против часовой стрелки, если при взгляде
#из вне многогранника, ограниченного оболочкой обход вершин происходит
#против часовой стрелки. Тогда заметим, что в таком случае, если
#смотреть со стороны оси OZ на проекции точек грани на плоскость XY, то
#точки будут ориентированы по часовой стрелке
def delaunay(points_2d):
    #Отображаем точки на параболоид
    points_3d = lift_to_paraboloid(points_2d)

    #Строим выпуклую оболочку точек в объёме
    hull_3d = ConvexHull(points_3d)

    #точка, которая гарантированно находится внутри выпуклой оболочки
    inside_point = find_centroid(points_3d)

    #Здесь храним нижние грани выпуклой оболочки
    delaunayTriangles = []

    #Здесь храним грани выпуклой оболочки
    hullFacets = hull_3d.simplices
    for facet in hullFacets:
        #Точки грани
        A = Point(points_3d[facet[0]][0],
        points_3d[facet[0]][1],
        points_3d[facet[0]][2]
        )

        B = Point(points_3d[facet[1]][0],
        points_3d[facet[1]][1],
        points_3d[facet[1]][2]
        )

        C = Point(points_3d[facet[2]][0],
        points_3d[facet[2]][1],
        points_3d[facet[2]][2]
        )
        
        #Вычисление нормали к грани
        AB = B - A
        AC = C - A
        normal = cross_product(AB, AC)

        #нужно понять, верно ли, что если смотреть на грань с внешней стороны оболочки,
        #то точки A, B, C перечислены в порядке обхода против часовой стрелки
        #если да, то ничего менять не нужно
        #если нет, то у вектора нормали нужно изменить направление на противоположное
        d = dot_product(A - inside_point, normal)
        if (d < 0):
            #меняем 
            normal = -normal

        # Если нормаль имеет отрицательную z-компоненту, то грань является 
        # нижней частью выпуклой оболочки, именно такие грани нам и нужно отобрать
        if (normal.z < 0):
            delaunayTriangles.append(facet)

    return delaunayTriangles

def plot_2d_visualization(points_2d, delaunay_triangles):
    fig, ax = plt.subplots(figsize=(12, 9))
    x = []
    y = []
    for p in points_2d:
        x.append(p.x)
    for p in points_2d:
        y.append(p.y)

    #изображение точек
    ax.scatter(x, y, c='red', s=50, zorder=3)
    
    #изображение рёбер всех треугольников
    for triangle in delaunay_triangles:
        vertices = [] #здесь храним вершины каждого треугольника блоками подряд
        for i in triangle:
            vertices.append(points_2d[i])
        
        #проход по 3 сторонам треугольника
        for i in range(3):
            begin = vertices[i]
            end = vertices[(i + 1) % 3]
            #plot - для рисования линий
            ax.plot([begin.x, end.x], [begin.y, end.y], 'b-', linewidth=2, zorder=2)
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    #одинаковый масштаб
    ax.set_aspect('equal')
    #сетка
    ax.grid(True, alpha=0.3)
    plt.show()

def main():
    with open('points.txt', 'r') as file:
        n = int(file.readline().strip())
        points_2d = []
        for i in range(n):
            x, y = map(float, file.readline().split())
            points_2d.append(Point(x, y, 0))
    
    #Триангуляция Делоне
    tracemalloc.start() 
    start_time = time.time()
    delaunay_triangles = delaunay(points_2d)
    end_time = time.time()
    execution_time = end_time - start_time

    current, peak = tracemalloc.get_traced_memory()

    tracemalloc.stop() 
    #в килобайтах
    print(peak / 1024) 
    
    print("время выполнения: " + str(round(execution_time, 5)) + " секунд")
    
    plot_2d_visualization(points_2d, delaunay_triangles)

if __name__ == "__main__":
    main()