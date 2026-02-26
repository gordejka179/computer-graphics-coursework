import matplotlib.pyplot as plt
import math
import time
import tracemalloc

class Point:
    def __init__(self, _x=0.0, _y=0.0):
        self.x = _x
        self.y = _y
    
    def __sub__(self, p):
        return Point(self.x - p.x, self.y - p.y)

#векторное произведение
def cross(a, b):
    return a.x * b.y - a.y * b.x

#знак для векторного произведения
def sgn(a):
    if (a > 0):
        return 1
    else:
        if (a < 0):
            return -1
        else:
            return 0

inf_p = Point(1e15, 1e15)

class QuadEdge:
    def __init__(self):
        self.used = False
        self.start = Point()
        self.rot = None
        self.onext = None
    
    def rev(self):
        return self.rot.rot
    
    def lnext(self):
        return self.rot.rev().onext.rot
    
    def oprev(self):
        return self.rot.onext.rot
    
    def dest(self):
        return self.rev().start

def make_edge(from_point, to_point):
    startEnd = QuadEdge()
    rightLeft = QuadEdge()
    endStart = QuadEdge()
    leftRight = QuadEdge()
    
    startEnd.start = from_point
    rightLeft.start = to_point
    endStart.start = inf_p
    leftRight.start = inf_p
    
    startEnd.rot = endStart
    rightLeft.rot = leftRight
    endStart.rot = rightLeft
    leftRight.rot = startEnd
    
    startEnd.onext = startEnd
    rightLeft.onext = rightLeft
    endStart.onext = leftRight
    leftRight.onext = endStart
    
    return startEnd

def swap_nexts(a, b):
    t = a.onext
    a.onext = b.onext
    b.onext = t

#предполагается, что у a и b общая вершина
# ВАЖНО эту функцию можно применить только в 2 случаях:
# 1) если первый параметр a - это вектор, который был только что создан, т е у него еще нет
#ничего кроме начала и конца.
#Если случай такой, то:
#после вызова splice, при применении onext к вектору a получится b.onext 
#(имеется в виду, что b.onext ещё до применения splice)
#также после вызова splice при применении onext к вектору b получится вектор a
#также нужно swap(a->onext->rot->onext, b->onext->rot->onext), чтобы onext при применении
#к двойственным рёбрам работал корректно
# 2) функцию можно применить для удаления ребра и ребро уже может быть соединено с другими
#Больше эту функцию НЕЛЬЗЯ применять к другим случаям
def splice(a, b):
    swap_nexts(a.onext.rot, b.onext.rot)
    swap_nexts(a, b)

def delete_edge(e):
    #убираем прямое ребро
    splice(e, e.oprev())
    #и противоположное к нему ребро
    splice(e.rev(), e.rev().oprev())

#конец вектора a к началу вектора b
def connect(a, b):
    e = make_edge(a.dest(), b.start)
    splice(e, a.lnext())
    splice(e.rev(), b)
    return e

#Если точка слева от ребра,то True
#иначе False
def left(p, e):
    return cross((e.start - p), (e.dest() - p)) > 0

#Если точка справа от ребра,то True
#иначе False
def right(p, e):
    return cross(e.start - p, e.dest() - p) < 0

#определитель матрицы 3 на 3
#передаём матрицу как массив 3 на 3
def det3(a):
    return (a[0][0] * (a[1][1] * a[2][2] - a[2][1] * a[1][2]) - 
            a[1][0] * (a[0][1] * a[2][2] - a[2][1] * a[0][2]) +
            a[2][0] * (a[0][1] * a[1][2] - a[1][1] * a[0][2]))

#возвращает сумму квадратов координат. Это нужно для проверки
#принадлжености точки окружности
def sumSquares(a):
    return a.x * a.x + a.y * a.y

#проверка на то, находится ли точка d внутри описанной окружности
#треугольника abc
def in_circle(a, b, c, d):
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

#первый элемент пары - это ребро, направленное против часовой стрелки
#и оно исходит из самой левой точки выпуклой оболочки
#идя по нему мы обойдем всю оболочку, полученную слиянием 2-ух исходных
#для второго элемента пары всё то же самое, но оно направлено по часовой стрелке
#и исходит из самой правой точки оболочки
def build_tr(l, r, p):
    if r - l + 1 == 2:
        #Создаём одно ребро между двумя точками
        #Возвращаем пару: (A→B, B→A)
        #Это минимальная триангуляция - одно ребро
        res = make_edge(p[l], p[r])
        return (res, res.rev())
    
    if r - l + 1 == 3:
        a = make_edge(p[l], p[l + 1])
        b = make_edge(p[l + 1], p[r])
        splice(a.rev(), b)
        sg = sgn(cross(p[l + 1] - p[l], p[r] - p[l]))
        
        if sg == 0:
            #точки коллинеарны
            return (a, b.rev())
        
        c = connect(b, a)
        
        if sg == 1:
            #При обходе p[l] → p[l+1] → p[r] движение против часовой стрелки
            return (a, b.rev())
        else:
            #При обходе p[l] → p[l+1] → p[r] движение по часовой стрелке
            return (c.rev(), c)
    
    mid = (l + r) // 2
    ldo, ldi, rdo, rdi = None, None, None, None
    #ldi - левое внутреннее ребро (Left Delaunay Inside)
    #rdi - правое внутреннее ребро (Right Delaunay Inside)
    #ldo -  Левое внешнее ребро Делоне
    #rdo - Правое внешнее ребро Делоне
    
    pair = build_tr(l, mid, p)
    ldo = pair[0]
    ldi = pair[1]
    
    pair = build_tr(mid + 1, r, p)
    rdi = pair[0]
    rdo = pair[1]
    
    #поиск отрезка, по которому можно соединить 2 выпуклые оболочки, то есть такого отрезка, который
    #также будет являться частью выпуклой оболочки объединённого множества точек методом 2 указателей
    while True:
        if left(rdi.start, ldi):
            ldi = ldi.lnext()
            continue
        if right(ldi.start, rdi):
            rdi = rdi.rev().onext
            continue
        break
    
    #базовое ребро, оно же касательное
    lowerEdge = connect(rdi.rev(), ldi)
    
    #это случай, когда точка, в которой касательная касается правой выпуклой оболочки, одновременно является ещё и самой правой
    #точкой в этой выпуклой оболочке
    #в таком случае нужно заменить rdo, иначе при обходе так и останемся в выпуклой оболочке правой части
    #а мы хотим в одну объединиться
    if (rdi.start.x == rdo.start.x) and (rdi.start.y == rdo.start.y):
        rdo = lowerEdge
    
    #это случай, когда точка, в которой касательная касается левой выпуклой оболочки, одновременно является ещё и самой левой
    #точкой в этой выпуклой оболочке
    #в таком случае нужно заменить ldo, иначе при обходе так и останемся в выпуклой оболочке левой части
    #а мы хотим в одну объединиться
    if (ldi.start.x == ldo.start.x) and (ldi.start.y == ldo.start.y):
        ldo = lowerEdge.rev()
    
    #будем делать подъём, пока не достигнем верхнего касательного ребра
    while True:
        lcand = lowerEdge.rev().onext
        rcand = lowerEdge.oprev()
        
        #проверим, справа ли от базового ребра находится точка, с которой потенциально можем соединиться
        #для правого кандидата:
        v_rcand = right(rcand.dest(), lowerEdge)
        #для левого:
        v_lcand = right(lcand.dest(), lowerEdge)
        
        if not v_lcand and not v_rcand:
            #Если оба кандидата слева, тогда мы достигли верхнего касательного ребра
            #между выпуклыми оболочками
            break
        
        if v_lcand:
            while in_circle(lowerEdge.dest(), lowerEdge.start, lcand.dest(), lcand.onext.dest()):
                t = lcand.onext
                delete_edge(lcand)
                lcand = t
        
        if v_rcand:
            while in_circle(lowerEdge.dest(), lowerEdge.start, rcand.dest(), rcand.oprev().dest()):
                t = rcand.oprev()
                delete_edge(rcand)
                rcand = t
        
        if not v_lcand or (v_rcand and in_circle(lcand.dest(), lcand.start, rcand.start, rcand.dest())):
            lowerEdge = connect(rcand, lowerEdge.rev())
        else:
            lowerEdge = connect(lowerEdge.rev(), lcand.rev())
    
    return (ldo, rdo)

#обходим треугольник против часовой стрелки и добавляем противоположные ребра
#добавляем именно противоположные ребра, чтобы с помощью lnext обойти треугольники, 
#которые относятся к этим рёбрам
def tour(edges, points, e):
    curr = e
    curr.used = True
    points.append(curr.start)
    edges.append(curr.rev())
    curr = curr.lnext()
    
    while curr != e:
        curr.used = True
        points.append(curr.start)
        edges.append(curr.rev())
        curr = curr.lnext()

#Сортируем точки по возрастанию x координаты, а в случае равенства
#по возрастанию y координаты
def comparePoints(a, b):
    return (a.x < b.x) or ((a.x == b.x) and (a.y < b.y))

def delaunay(p):
    ans = []
    #сортируем точки
    p.sort(key=lambda point: (point.x, point.y))
    res = build_tr(0, len(p) - 1, p)
    #берём ребро из выпуклой оболочки, чтобы оно было направлено по часовой стрелке
    e = res[0].rev()
    edges = [e]
    points = []
    #в начале пометим посещёнными все рёбра выпуклой оболочки, направленные по часовой стрелке.
    #Без этого действия, если какой-то из последующих обходов попадет в это ребро,
    #то lnext обработает его не так, как ожидалось
    tour(edges, points, e)
    points.clear()
    count = 0
    
    while count < len(edges):
        e = edges[count]
        count += 1
        if not e.used:
            tour(edges, points, e)
    
    for i in range(0, len(points), 3):
        ans.append((points[i], points[i + 1], points[i + 2]))
    
    return ans

def visualize_delaunay(points, triangles):
    fig, ax = plt.subplots(figsize=(12, 10))

    x = []
    for p in points:
        x.append(p.x)

    y = []
    for p in points:
        y.append(p.y)

    ax.scatter(x, y, color='red', s=50, zorder=5)
        
    for triangle in triangles:
        a, b, c = triangle
        points_cycle = [a, b, c, a]
        tri_x = []
        tri_y = []
        for point in points_cycle:
            tri_x.append(point.x)
            tri_y.append(point.y)   
        ax.plot(tri_x, tri_y, 'b-')
    
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

    start_time = time.time()
    tracemalloc.start()
    triangles = delaunay(points)
    end_time = time.time()
    execution_time = end_time - start_time

    current, peak = tracemalloc.get_traced_memory()
    #в килобайтах
    print(peak / 1024)
    tracemalloc.stop() 
    print("время выполнения: " + str(round(execution_time, 5)) + " секунд")

    visualize_delaunay(points, triangles)

if __name__ == "__main__":
    main()
