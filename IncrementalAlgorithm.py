import math
import time
import matplotlib.pyplot as plt
import tracemalloc

class Point:
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
def cross(a, b, c):
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)

#возвращает сумму квадратов координат. Это нужно для проверки
#принадлжености точки окружности
def sumSquares(a):
    return a.x * a.x + a.y * a.y

#определитель матрицы 3 на 3
#передаём матрицу как массив 3 на 3
def det3(a):
    return (a[0][0] * (a[1][1] * a[2][2] - a[2][1] * a[1][2]) - 
            a[1][0] * (a[0][1] * a[2][2] - a[2][1] * a[0][2]) +
            a[2][0] * (a[0][1] * a[1][2] - a[1][1] * a[0][2]))

#проверка на то, находится ли точка d внутри описанной окружности
#треугольника abc
def inCircle(a, b, c, d):
    det = 0.0
    aSq = sumSquares(a)
    bSq = sumSquares(b)
    cSq = sumSquares(c)
    dSq = sumSquares(d)
    
    arr1 = [[b.x, b.y, bSq], [c.x, c.y, cSq], [d.x, d.y, dSq]]
    det = -det3(arr1)
    
    arr2 = [[a.x, a.y, aSq], [c.x, c.y, cSq], [d.x, d.y, dSq]]
    det += det3(arr2)
    
    arr3 = [[a.x, a.y, aSq], [b.x, b.y, bSq], [d.x, d.y, dSq]]
    det -= det3(arr3)
    
    arr4 = [[a.x, a.y, aSq], [b.x, b.y, bSq], [c.x, c.y, cSq]]
    det += det3(arr4)
    
    return det > 0

class Edge:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    
    def __eq__(self, other):
        return (self.a == other.a and self.b == other.b) or (self.a == other.b and self.b == other.a)

def incremental_algorithm(points):
    if len(points) < 3:
        return []

    #хотим построить треугольник, который будет содержать в себе все остальные точки
    #идея ниже не сработала:

    min_x = points[0].x
    max_x = points[0].x
    min_y = points[0].y
    max_y = points[0].y
    
    for p in points:
        min_x = min(min_x, p.x)
        max_x = max(max_x, p.x)
        min_y = min(min_y, p.y)
        max_y = max(max_y, p.y)
    dx = max_x - min_x
    dy = max_y - min_y
    #построение супер-треугольника
    #будем строить равнобедренный треугольник
    #вершина
    p1 = Point(min_x + dx/2, max_y + dy)
    #теперь строим основание
    #вначале левую вершину
    #прямая через вершину прямоугольника (min_x, max_y) и вершину равнобедренного
    #треугольника (min_x + dx/2, max_y + dy) будет иметь уравнение y = (2*dy / dx) * x + max_y - (2*dy / dx) * min_x
    #найдем её пересечение с горизонтальной прямой y = min_y - dy
    #получим (((min_y - dy - (max_y) + (2*dy / dx) * min_x) * dx) / (2 * dy), min_y - dy)
    p2 = Point(((min_y - dy - (max_y) + (2*dy / dx) * min_x) * dx) / (2 * dy), min_y - dy)
    #теперь правую вершину
    #прямая через вершину прямоугольника (max_x, max_y) и вершину равнобедренного
    #треугольника (min_x + dx/2, max_y + dy) будет иметь уравнение 
    #y = (dy / (min_x + dx/2 - max_x)) * x + max_y - (max_x * dy / (min_x + dx/2 - max_x))
    #найдем её пересечение с горизонтальной прямой y = min_y - dy
    #получим ((min_y - dy - max_y + (max_x * dy / (min_x + dx/2 - max_x))) * (min_x + dx/2 - max_x) / dy, min_y - dy)
    p3 = Point((min_y - dy - max_y + (max_x * dy / (min_x + dx/2 - max_x))) * (min_x + dx/2 - max_x) / dy, min_y - dy)

    #квадрат основания равнобедренного треугольника:
    a = (p3.x - p2.x) ** 2 

    #квадрат боковой стороны равнобедренного треугольника:
    b = (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2

    #формула радиуса описанной окружности равнобедренного треугольника:
    R = a / ((4 * a - b) ** 0.5)

    #Возьмем треугольник, который содержит в себе все остальные вершины, причем 
    #вершины расположены далеко друг от друга. Для этого применим преобразование подобия
    #относительно центра описанной окружности
    #координаты центра в равнобедренном треугольнике:
    centreX = p1.x
    centreY = p1.y - R

    #используем формулу для преобразования подобия
    p1 = Point(centreX + 10 * (p1.x - centreX), centreY + 10 * (p1.y - centreY))
    p2 = Point(centreX + 10 * (p2.x - centreX), centreY + 10 * (p2.y - centreY))
    p3 = Point(centreX + 10 * (p3.x - centreX), centreY + 10 * (p3.y - centreY))

    triangulation = []
    new_triangulation = []

    #вначале добавляем супер-треугольник
    triangulation.append((p1, p2, p3))
    #будем последовательно добавлять точки
    for point in points:
        #после добавления точки триангуляция может перестать быть триангуляцией делоне, 
        #чтобы исправить будем искать треугольники, которые нарушают условие триангуляции делоне
        triangles_to_remove = []
        for triangle in triangulation:
            a, b, c = triangle
            #критерием нарушения триангуляции является попадание новой точки в описанную окружность какого-то треугольника  
            if (inCircle(a, b, c, point)):
                triangles_to_remove.append(triangle)
        
        #теперь важно понять, какие из рёбер треугольников нужно оставить, а какие удалить
        #нужно удалить те, которые разделяются между 2 треугольниками
        #а остальные оставить, будем их хранить в polygon
        polygon = []
        for triangle in triangles_to_remove:
            a, b, c = triangle
            edges = [Edge(a, b), Edge(b, c), Edge(c, a)]
            for edge in edges:
                shared = False
                for other_triangle in triangles_to_remove:
                    if (triangle != other_triangle):
                        oa, ob, oc = other_triangle
                        other_edges = [Edge(oa, ob), Edge(ob, oc), Edge(oc, oa)]
                        for other_edge in other_edges:
                            if (edge == other_edge):
                                shared = True
                                break 
                    else:
                        continue            
                if not shared:
                    polygon.append(edge)
        
        #избавляемся от удалённых треугольников
        new_triangulation = []
        for triangle in triangulation:
            if triangle not in triangles_to_remove:
                new_triangulation.append(triangle)

        triangulation = new_triangulation
        #вершины тех рёбер, которые относились лишь к одному удалённому треугольнику нужно
        #нужно соединить с только что добавленной точкой
        for edge in polygon:
            triangulation.append((edge.a, edge.b, point))
    
    #не берем вершины супер-треугольника
    new_triangulation = []
    for triangle in triangulation:
        if p1 not in triangle and p2 not in triangle and p3 not in triangle:
            new_triangulation.append(triangle)
    
    return new_triangulation

def draw(triangulation):
    fig, ax = plt.subplots(figsize=(12, 9))
    for triangle in triangulation:
        a, b, c = triangle
        # - значит линия
        plt.plot([a.x, b.x], [a.y, b.y], 'b-')
        plt.plot([b.x, c.x], [b.y, c.y], 'b-')
        plt.plot([c.x, a.x], [c.y, a.y], 'b-')

        #ro - красный и круглый
        plt.plot(a.x, a.y, 'ro')
        plt.plot(b.x, b.y, 'ro')
        plt.plot(c.x, c.y, 'ro')

    #одинаковый масштаб
    ax.set_aspect('equal')
    #сетка
    ax.grid(True, alpha=0.3)
    plt.show()

def main():
    with open('points.txt', 'r') as file:
        n = int(file.readline().strip())
        points = []
        for i in range(n):
            x, y = map(float, file.readline().split())
            points.append(Point(x, y))


    tracemalloc.start()        

    start_time = time.time()
    triangulation = incremental_algorithm(points)
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("время выполнения: " + str(round(execution_time, 5)) + " секунд")  

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop() 

    #в килобайтах
    print(peak / 1024)

    #Изображение
    draw(triangulation)

if __name__ == "__main__":
    main()