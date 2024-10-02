import numpy as np
import matplotlib.pyplot as plt
#import csv
import matplotlib.animation as animation
GRID_X, GRID_Y = 50, 50 # Kích thước của 1 lớp học
NUM_INDIVIDUALS = 100 # Sô lượng sinh viên
NUM_RFID_READERS = 50  # Số lượng đầu đọc RFID
NUM_ITERATION = 50  # Số vòng lặp
RFID_RADIUS = 3.69 # Bán kính vùng phủ sóng của đầu đọc
DIM = 2
ALPHA = 0.7
UPDATE_INTERVAL = 500
MOVE_PERCENTAGE_MIN = 0.01  # Tỷ lệ di chuyển tối thiểu
MOVE_PERCENTAGE_MAX = 0.02  # Tỷ lệ di chuyển tối đa

# Hàm để kiểm tra khoảng cách giữa hai điểm
def is_valid_distance(new_point, points, min_distance):
    for point in points:
        if np.linalg.norm(new_point - point) < min_distance:
            return False
    return True
def calculate_inertia_weight(w_max, w_min, iter, iter_max):
    """
    Tính giá trị w theo công thức w = w_max - ((w_max - w_min) / iter_max) * iter
    
    Parameters:
    - w_max: Trọng số lớn nhất (w_max)
    - w_min: Trọng số nhỏ nhất (w_min)
    - iter: Số vòng lặp hiện tại
    - iter_max: Số vòng lặp tối đa

    Returns:
    - w: Trọng số w ở vòng lặp hiện tại
    """
    w = w_max - ((w_max - w_min) / iter_max) * iter
    return w
def calculate_covered_students(students, readers, rfid_radius = 3.69):
    """
    Tính số sinh viên được bao phủ bởi ít nhất một đầu đọc RFID.
    
    Parameters:
    - students: Danh sách các đối tượng sinh viên (vị trí của sinh viên)
    - readers: Danh sách các đối tượng đầu đọc (vị trí của đầu đọc)
    - rfid_radius: Bán kính bao phủ của mỗi đầu đọc RFID
    
    Returns:
    - Số lượng sinh viên được bao phủ
    """
    covered_students = 0
    
    for student in students:
        student_covered = False  # Giả định ban đầu sinh viên không được bao phủ
        
        for reader in readers:
            distance = np.linalg.norm(student.position - reader.position)
            
            # Kiểm tra xem sinh viên có nằm trong vùng bán kính của đầu đọc nào không
            if distance <= rfid_radius:
                student_covered = True
                break  # Dừng kiểm tra nếu sinh viên đã được bao phủ bởi ít nhất một đầu đọc
        
        if student_covered:
            covered_students += 1
    
    return covered_students
def calculate_overlap_points(students, readers, RFID_RADIUS=3.69):
    """
    Tính số điểm trùng lặp (số sinh viên được bao phủ bởi nhiều hơn một đầu đọc).

    Parameters:
    - students: Danh sách các đối tượng sinh viên
    - readers: Danh sách các đối tượng đầu đọc RFID
    - RFID_RADIUS: Bán kính vùng phủ sóng của mỗi đầu đọc

    Returns:
    - Số lượng điểm trùng lặp
    """
    overlap_count = 0  # Đếm số lượng sinh viên nằm trong vùng trùng lặp

    for student in students:
        covered_by = 0  # Đếm số đầu đọc bao phủ sinh viên này
        student_pos = student.position

        for reader in readers:
            reader_pos = reader.position
            distance = np.linalg.norm(student_pos - reader_pos)

            if distance <= RFID_RADIUS:
                covered_by += 1  # Sinh viên này được bao phủ bởi đầu đọc này

        if covered_by > 1:
            overlap_count += 1  # Sinh viên này nằm trong vùng trùng lặp

    return overlap_count
def BieuDoReader(READERS, STUDENTS):
    fig, ax = plt.subplots()
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_xlim(0, GRID_X)
    ax.set_ylim(0, GRID_Y)
    ax.set_aspect('equal', 'box')

    # Tối ưu hóa bằng thuật toán PSO
    sspso = SSPSO(NUM_RFID_READERS, DIM, NUM_ITERATION)
    READERS = sspso.readers  # Khởi tạo readers từ SSPSO

    # Trích xuất vị trí sinh viên và đầu đọc RFID
    student_positions = np.array([student.position for student in STUDENTS])
    reader_positions = np.array([reader.position for reader in READERS])

    ax.scatter(student_positions[:, 0], student_positions[:, 1], color='blue', label='Students', s=10)
    scatter_rfid = ax.scatter(reader_positions[:, 0], reader_positions[:, 1], color='red', label='RFID Readers', marker='^')

    # Tạo các hình tròn biểu diễn vùng phủ sóng của các đầu đọc RFID
    circles = [plt.Circle((x, y), RFID_RADIUS, color='red', fill=True, alpha=0.2, linestyle='--') for x, y in reader_positions]
    for circle in circles:
        ax.add_artist(circle)

    # Text hiển thị số sinh viên trong vùng bán kính
    count_text = ax.text(0.02, 1.05, 'Students in range: 0', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    # Hàm cập nhật vị trí của các reader
    def update_reader(frame):
        reader_positions = sspso.optimize(STUDENTS)  # Chạy từng vòng lặp tối ưu cho mỗi frame
        # Cập nhật vị trí của các đầu đọc RFID
        scatter_rfid.set_offsets(reader_positions)
        count_in_range = 0
        for student in student_positions:
            if any(np.linalg.norm(student - reader.position) <= RFID_RADIUS for reader in READERS):
                count_in_range += 1

        # Cập nhật vị trí của các hình tròn vùng phủ sóng
        for i, circle in enumerate(circles):
            circle.center = reader_positions[i]

        coverage_ratio = calculate_covered_students(READERS, STUDENTS)
        print(f"Iteration {frame}: Coverage Ratio = {coverage_ratio * 100:.2f}% ({coverage_ratio:.4f})")
        if coverage_ratio == 1.0:
            print(f"All tags are covered at iteration. Stopping the optimization.")
            return
        count_text.set_text(f'Students in range: {count_in_range}')
        print(f"Iteration {frame}: {count_in_range} students in range")
        return scatter_rfid, *circles
    # Animation cho quá trình cập nhật vị trí của reader
    ani_reader = animation.FuncAnimation(fig, update_reader, frames=NUM_ITERATION, interval=UPDATE_INTERVAL, blit=False, repeat=False)

    # Animation cho quá trình cập nhật vị trí của student
    #ani_student = animation.FuncAnimation(fig, update_student, frames=999999, interval=UPDATE_INTERVAL, blit=False, repeat=False)

    plt.show()
def BieuDoStudents(READERS, STUDENTS):
    fig, ax = plt.subplots()
    ax.set_xlabel('X Coordinate')
    ax.set_ylabel('Y Coordinate')
    ax.set_xlim(0, GRID_X)
    ax.set_ylim(0, GRID_Y)
    ax.set_aspect('equal', 'box')
    student_positions = np.array([student.position for student in STUDENTS])
    reader_positions = np.array([reader.position for reader in READERS])
    scatter_student = ax.scatter(student_positions[:, 0], student_positions[:, 1], color='blue', label='Students', s=10)
    ax.scatter(reader_positions[:, 0], reader_positions[:, 1], color='red', label='RFID Readers', marker='^')
    # Tạo các hình tròn biểu diễn vùng phủ sóng của các đầu đọc RFID
    circles = [plt.Circle((x, y), RFID_RADIUS, color='red', fill=True, alpha=0.2, linestyle='--') for x, y in reader_positions]
    for circle in circles:
        ax.add_artist(circle)
     # Text hiển thị số sinh viên trong vùng bán kính
    count_text = ax.text(0.02, 1.05, 'Students in range: 0', transform=ax.transAxes, fontsize=12, verticalalignment='top')
    # Hàm cập nhật vị trí của các student
    def update_student(frame):
        for student in STUDENTS:
            student.update_position()
        student_positions = np.array([student.position for student in STUDENTS])
        student_positions = np.atleast_2d(student_positions)

        # Cập nhật màu sắc của sinh viên dựa trên vị trí
        colors = []
        count_in_range = 0
        for student in student_positions:
            if any(np.linalg.norm(student - reader.position) <= RFID_RADIUS for reader in READERS):
                colors.append('green')  # Đổi thành màu xanh lục nếu trong vùng phủ sóng
                count_in_range += 1
            else:
                colors.append('blue')  # Giữ màu xanh dương nếu ngoài vùng phủ sóng

        scatter_student.set_offsets(student_positions)
        scatter_student.set_color(colors)  # Cập nhật màu sắc của sinh viên

        # Cập nhật số sinh viên trong vùng bán kính
        count_text.set_text(f'Students in range: {count_in_range}')
        print(f"Iteration {frame}: {count_in_range} students in range")

        return scatter_student
    # Animation cho quá trình cập nhật vị trí của student
    animation.FuncAnimation(fig, update_student, frames=999999, interval=UPDATE_INTERVAL, blit=False, repeat=False)
    plt.show()
class Students:
    def __init__(self, dim):
        self.position = np.random.rand(dim) * [GRID_X, GRID_Y]
        self.id = np.random.randint(2001210000, 2001220000)
       

    def update_position(self):
        move_distance = np.random.uniform(MOVE_PERCENTAGE_MIN * GRID_X, MOVE_PERCENTAGE_MAX * GRID_X)
        angle = np.random.rand() * 2 * np.pi  # Tạo góc ngẫu nhiên
        self.position += move_distance * np.array([np.cos(angle), np.sin(angle)])
        self.position = np.clip(self.position, [0, 0], [GRID_X, GRID_Y])

class Readers:
    def __init__(self, dim):
        self.position = np.random.rand(dim) * [GRID_X, GRID_Y]
        self.velocity = np.random.rand(dim) * [0, 0.1]
        self.best_position = self.position.copy()
        self.best_value = 0

    def update_velocity(self, global_best_position, w, c1=1.5, c2=1.5):
        r1 = np.random.rand(len(self.position))
        r2 = np.random.rand(len(self.position))
        
        # Lấy vị trí tốt nhất toàn cục và vị trí hiện tại của từng hạt
        cognitive_component = c1 * r1 * (self.best_position - self.position)
        social_component = c2 * r2 * (global_best_position - self.position)
        
        # Cập nhật vận tốc
        self.velocity = w * self.velocity + cognitive_component + social_component

    def update_position(self):
        self.position += self.velocity


def fitness(students_covered, total_students, overlap_points):
    """
    Tính toán fitness của một particle dựa trên số học sinh bao phủ, số reader sử dụng, và diện tích trùng lặp.
    
    Parameters:
    - students_covered: Số học sinh được bao phủ bởi các đầu đọc
    - total_students: Tổng số học sinh trong vùng
    - total_readers: Tổng số đầu đọc có thể đặt trong vùng
    - overlap_points: Số điểm trùng lặp (số học sinh bị nhiều đầu đọc bao phủ)
    
    Returns:
    - Giá trị fitness của particle
    """
    # X = c / T: Tỷ lệ số item được bao phủ
    X = students_covered / total_students
    # Y = (N - n) / N: Tỷ lệ giảm của số đầu đọc được sử dụng
    #Y = (total_readers - readers_used) / total_readers
    # Z = (T - e) / T: Tỷ lệ giảm của số điểm bị bao phủ bởi nhiều đầu đọc
    Z = (total_students - overlap_points) / total_students
    # Hàm fitness: 0.6 * X + 0.2 * Y + 0.2 * Z
    fitness_value = 0.6 * X  + 0.2 * Z
    return fitness_value

class SSPSO:
    def __init__(self, num_particles, dim, max_iter, alpha=0.5, w_max=0.9, w_min=0.4):
        self.num_particles = num_particles
        self.dim = dim
        self.alpha = alpha
        self.max_iter = max_iter
        self.readers = [Readers(dim) for _ in range(num_particles)]
        self.global_best_position = np.random.uniform(-1, 1, dim)
        self.global_best_value = float('inf')
        self.w_max = w_max  # Giá trị w_max
        self.w_min = w_min  # Giá trị w_min

    def optimize(self, STUDENTS):
        for iter in range(self.max_iter):
            # Tính toán hệ số quán tính (w)
            w = calculate_inertia_weight(self.w_max, self.w_min, iter, self.max_iter)
            for particle in self.readers:
                # Đánh giá hàm mục tiêu dựa trên độ phủ và trùng lặp
                fitness_value = fitness(calculate_covered_students(self.readers, STUDENTS), len(STUDENTS), calculate_overlap_points(self.readers, STUDENTS))
                
                # Cập nhật vị trí tốt nhất của từng hạt
                if fitness_value > particle.best_value:  # Tối đa hóa
                    particle.best_position = particle.position.copy()
                    particle.best_value = fitness_value

                # Cập nhật vị trí tốt nhất của toàn bộ quần thể
                if fitness_value > self.global_best_value:  # Tối đa hóa
                    self.global_best_position = particle.position.copy()
                    self.global_best_value = fitness_value
            
            # Cập nhật vận tốc và vị trí của mỗi hạt
            for particle in self.readers:
                particle.update_velocity(self.global_best_position, w)
                particle.update_position()
        
        return self.readers
        
            


readers =  [Readers(DIM) for _ in range(NUM_RFID_READERS)]
students = [Students(DIM) for _ in range(NUM_INDIVIDUALS)]
BieuDoReader(readers, students)
BieuDoStudents(readers, students)



