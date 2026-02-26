from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import glfw
import random
import math
from ConvexHull import delaunay

wireframe_mode = False

vertices = []
indices = []
colors = []
points_data = []
normals = []

#конфигурация
square_size = 250
points_count = 10 * square_size
window_width = 1024
window_height = 768

fov = 60
scene_position = [0.0, 0.0, 0.0]
rotation = [90.0, 0.0, 0.0]
move_speed = square_size * 0.01
rotate_speed = 2.5


#параметры освещения 
light_ambient = [0.3, 0.3, 0.3, 1.0]
light_diffuse = [0.7, 0.7, 0.7, 1.0]
light_specular = [0.1, 0.1, 0.1, 1.0]


class Point:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Point(-self.x, -self.y, -self.z)

def normalize_vector(v):
    length = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if length > 0:
        return [v[0] / length, v[1] / length, v[2] / length]
    return v

def cross_product(v1, v2):
    return [
        v1[1] * v2[2] - v1[2] * v2[1],
        v1[2] * v2[0] - v1[0] * v2[2],
        v1[0] * v2[1] - v1[1] * v2[0]
    ]

def update_projection():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = window_width / window_height

    gluPerspective(fov, aspect_ratio, 0.1, square_size)
    glMatrixMode(GL_MODELVIEW)

def generateTerrainDataGauss(points_count, size):
    #случайные точки на плоскости
    x = []
    for i in range(points_count):
        ranNum = random.uniform(0, size)
        x.append(ranNum) 

    y = []
    for i in range(points_count):
        ranNum = random.uniform(0, size)
        y.append(ranNum)

    #добавляем точки по границам
    boundary_points = size
    boundary_points_list = []
    
    #верхняя граница
    for i in range(boundary_points):
        boundary_points_list.append([random.uniform(0, size), size])
    
    #нижняя граница
    for i in range(boundary_points):
        boundary_points_list.append([random.uniform(0, size), 0.0])
    
    #левая граница
    for i in range(boundary_points):
        boundary_points_list.append([0.0, random.uniform(0, size)])
    
    #правая граница
    for i in range(boundary_points):
        boundary_points_list.append([size, random.uniform(0, size)])

    main_points = []
    for i in range(len(x)):
        point = [x[i], y[i]]
        main_points.append(point)

    allPoints = main_points + boundary_points_list

    #параметры основной горы
    centerX = size / 2 
    centerY = size / 2
    #высота основной горы
    maxHeight = 0.7 * size
    
    hills_count = 2
    hills = []
    for i in range(hills_count):
        while True:
            hill_x = random.uniform(0, size)
            hill_y = random.uniform(0, size)
            dist_to_center = ((hill_x - centerX) ** 2 + (hill_y - centerY) ** 2) ** 0.5
            
            if dist_to_center > size * 0.5 and dist_to_center < size * 0.6:
                break
        
        #высота холма
        hill_height = random.uniform(0.1, 0.2) * size
        #радиус влияния:
        hill_radius = random.uniform(0.1, 0.2) * size
        
        hills.append({
            'x': hill_x,
            'y': hill_y,
            'height': hill_height,
            'radius': hill_radius,
            'steepness': random.uniform(0.5, 1)
        })

    pointsWithHeight = []
    for point in allPoints:
        x = point[0]
        y = point[1]
        
        #высота от основной горы
        distFromCenter = ((x - centerX) ** 2 + (y - centerY) ** 2) ** 0.5
        z_main = maxHeight * math.exp(-0.5 * (distFromCenter / (size * 0.25)) ** 2) 
        
        #добавляем высоту от холмов
        z_hills = 0
        for hill in hills:
            dist_to_hill = ((x - hill['x']) ** 2 + (y - hill['y']) ** 2) ** 0.5
            if dist_to_hill < hill['radius']:
                #гауссова функция для холмика
                hill_contribution = hill['height'] * math.exp(-hill['steepness'] * (dist_to_hill / hill['radius']) ** 2)
                z_hills += hill_contribution
        
        #общая высота (основная гора + холмики)
        z = z_hills
        z += z_main

        if (point[0] == 0 or point[0] == size or point[1] == 0 or point[1] == size):
            z = 0
        
        pointsWithHeight.append([x, y, z])

    return pointsWithHeight

def generateOnlyHills(points_count, size):
    #случайные точки на плоскости
    x = []
    for i in range(points_count):
        ranNum = random.uniform(0, size)
        x.append(ranNum) 

    y = []
    for i in range(points_count):
        ranNum = random.uniform(0, size)
        y.append(ranNum)

    #добавляем точки по границам
    boundary_points = size
    boundary_points_list = []
    
    #верхняя граница
    for i in range(boundary_points):
        boundary_points_list.append([random.uniform(0, size), size])
    
    #нижняя граница
    for i in range(boundary_points):
        boundary_points_list.append([random.uniform(0, size), 0.0])
    
    #левая граница
    for i in range(boundary_points):
        boundary_points_list.append([0.0, random.uniform(0, size)])
    
    #правая граница
    for i in range(boundary_points):
        boundary_points_list.append([size, random.uniform(0, size)])

    main_points = []
    for i in range(len(x)):
        point = [x[i], y[i]]
        main_points.append(point)

    allPoints = main_points + boundary_points_list

    hills_count = size
    hills = []
    for i in range(hills_count):
        hill_x = random.uniform(0, size)
        hill_y = random.uniform(0, size)

        #высота холма
        hill_height = random.uniform(1, 5)
        #радиус влияния:
        hill_radius = random.uniform(5, 10)
        
        hills.append({
            'x': hill_x,
            'y': hill_y,
            'height': hill_height,
            'radius': hill_radius,
            'steepness': random.uniform(0.05, 0.01)  #коэффициент перед x^2 в формуле Гаусса
        })

    pointsWithHeight = []
    for point in allPoints:
        x = point[0]
        y = point[1]
        
        #добавляем высоту от холмов
        z_hills = 0
        for hill in hills:
            dist_to_hill = ((x - hill['x']) ** 2 + (y - hill['y']) ** 2) ** 0.5
            if dist_to_hill < hill['radius']:
                hill_contribution = hill['height'] * math.exp(-hill['steepness'] * (dist_to_hill / hill['radius']) ** 2)
                z_hills += hill_contribution
        
        z = z_hills

        if (point[0] == 0 or point[0] == size or point[1] == 0 or point[1] == size):
            z = 0
        
        pointsWithHeight.append([x, y, z])

    return pointsWithHeight

    

def calculate_normals(vertices, indices):
    vertex_count = len(vertices)
    normals = [[0.0, 0.0, 0.0] for _ in range(vertex_count)]
    
    #нормали для каждого треугольника
    for i in range(0, len(indices), 3):
        idx1, idx2, idx3 = indices[i], indices[i + 1], indices[i + 2]
        
        v1 = vertices[idx1 * 3: 3 * idx1 + 3]
        v2 = vertices[idx2 * 3: 3 * idx2 + 3]
        v3 = vertices[idx3 * 3: 3 * idx3 + 3]
        
        #векторы сторон треугольника
        vec1 = [v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]]
        vec2 = [v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]]
        
        #нормаль к треугольнику
        normal = cross_product(vec1, vec2)
        normal = normalize_vector(normal)
        
        #исправляем нормаль, если z < 0
        if normal[2] < 0:
            normal = [-normal[0], -normal[1], -normal[2]]
        
        #добавляем нормаль к каждой вершине треугольника
        for idx in [idx1, idx2, idx3]:
            normals[idx][0] += normal[0]
            normals[idx][1] += normal[1]
            normals[idx][2] += normal[2]
    
    #нормализуем итоговые нормали для каждой вершины
    for i in range(vertex_count):
        normals[i] = normalize_vector(normals[i])
        #гарантируем, что z >= 0
        if normals[i][2] < 0:
            normals[i] = [-normals[i][0], -normals[i][1], -normals[i][2]]

    flat_normals = []
    for normal in normals:
        flat_normals.extend(normal)
    
    return flat_normals

def prepare_triangle_data(points_count, square_size):
    #points = generateTerrainDataGauss(points_count, square_size)
    points = generateOnlyHills(points_count, square_size)
    points_2d = []
    for p in points:
        points_2d.append(Point(p[0], p[1]))

    tri = delaunay(points_2d)

    all_vertices = []
    triangle_indices = []
    vertex_colors = []
    
    for p in points:
        all_vertices.append(p[0])
        all_vertices.append(p[1])
        all_vertices.append(p[2])
    
    for t in tri:
        triangle_indices.append(t[0])
        triangle_indices.append(t[1])
        triangle_indices.append(t[2])

    for p in points:
        ran = random.uniform(0, 20) * 0.01
        r = 0.31 + ran
        g = 0.5 + ran
        b = 0.13 + ran
        vertex_colors.append(r)
        vertex_colors.append(g)
        vertex_colors.append(b)

    #вычисление нормалей
    vertex_normals = calculate_normals(all_vertices, triangle_indices)

    return all_vertices, triangle_indices, vertex_colors, points, vertex_normals

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.3, 0.3, 0.3, 1.0])
    
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

def draw_terrain():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    
    glRotatef(-rotation[0], 1, 0, 0)
    glRotatef(-rotation[2], 0, 0, 1)
    glTranslatef(scene_position[0], scene_position[1], scene_position[2])
    
    if wireframe_mode:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glLineWidth(1.0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)
    
    if not wireframe_mode:
        glEnable(GL_LIGHTING)
        glEnable(GL_COLOR_MATERIAL)

    #треугольники
    glBegin(GL_TRIANGLES)
    for i in range(0, len(indices), 3):
        idx1, idx2, idx3 = indices[i] * 3, indices[i + 1] * 3, indices[i + 2] * 3
        n_idx1, n_idx2, n_idx3 = indices[i], indices[i + 1], indices[i + 2]
        
        #первая вершина
        glNormal3f(normals[n_idx1*3], normals[n_idx1*3 + 1], normals[n_idx1*3 + 2])
        glColor3f(colors[idx1], colors[idx1 + 1], colors[idx1 + 2])
        glVertex3f(vertices[idx1], vertices[idx1 + 1], vertices[idx1 + 2])

        #вторая вершина
        glNormal3f(normals[n_idx2*3], normals[n_idx2*3 + 1], normals[n_idx2*3 + 2])
        glColor3f(colors[idx2], colors[idx2 + 1], colors[idx2 + 2])
        glVertex3f(vertices[idx2], vertices[idx2 + 1], vertices[idx2 + 2])

        #третья вершина
        glNormal3f(normals[n_idx3*3], normals[n_idx3*3 + 1], normals[n_idx3*3 + 2])
        glColor3f(colors[idx3], colors[idx3 + 1], colors[idx3 + 2])
        glVertex3f(vertices[idx3], vertices[idx3 + 1], vertices[idx3 + 2])
        
    glEnd()

    glPointSize(1.0)
    glColor3f(0.0, 0.0, 0.0)
    glBegin(GL_POINTS)
    for i in range(0, len(vertices), 3):
        glVertex3f(vertices[i], vertices[i + 1], vertices[i + 2])
    glEnd()

def process_movement():
    global scene_position, rotation
    
    ugol = (-rotation[2] / 180) * math.pi
    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        scene_position[0] -= math.sin(ugol) * move_speed
        scene_position[1] -= math.cos(ugol) * move_speed

    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        scene_position[0] += math.sin(ugol) * move_speed
        scene_position[1] += math.cos(ugol) * move_speed


    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        scene_position[0] -= math.sin(ugol - (math.pi / 2)) * move_speed
        scene_position[1] -= math.cos(ugol - (math.pi / 2)) * move_speed
        
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        scene_position[0] -= math.sin(ugol + (math.pi / 2)) * move_speed
        scene_position[1] -= math.cos(ugol + (math.pi / 2)) * move_speed
    
    #SPACE
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        scene_position[2] += move_speed

    #SHIFT
    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
        scene_position[2] -= move_speed

    #повороты:
    #влево-вправо 
    if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
        rotation[2] += rotate_speed
    if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
        rotation[2] -= rotate_speed
    
    #вверх-вниз
    if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
        rotation[0] -= rotate_speed
        if (rotation[0] < 0):
            rotation[0] = 0
    if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
        rotation[0] += rotate_speed
        if (rotation[0] > 180):
            rotation[0] = 180

def key_callback(window, key, scancode, action, mods):
    global wireframe_mode, scene_position, rotation
    
    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_C:
            wireframe_mode = not wireframe_mode

def window_resize_callback(window, width, height):
    global window_width, window_height
    window_width = width
    window_height = height
    glViewport(0, 0, width, height)
    update_projection()

def main():
    global window_width, window_height, window
    global vertices, indices, colors, points_data, normals
    
    if not glfw.init():
        return
    
    window = glfw.create_window(window_width, window_height, "Гор", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    
    glClearColor(0.7, 0.85, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    setup_lighting()
    
    update_projection()
    
    vertices, indices, colors, points_data, normals = prepare_triangle_data(points_count, square_size)
    
    glfw.set_key_callback(window, key_callback)
    glfw.set_window_size_callback(window, window_resize_callback)


    while not glfw.window_should_close(window):
        process_movement()
        draw_terrain()
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    main()
