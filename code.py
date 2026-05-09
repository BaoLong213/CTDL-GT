import math
import random

# ===== THAM SỐ =====
POP_SIZE = 50
MAX_GEN = 100
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.1

VEHICLE_CAPACITY = 100
SPEED = 1.0  # tốc độ xe

# ===== CẤU TRÚC =====
class KhachHang:
    def __init__(self, id, x, y, demand, ready, due, service=0):
        self.id = id
        self.x = x
        self.y = y
        self.demand = demand
        self.ready = ready      # thời gian sớm nhất
        self.due = due          # thời gian muộn nhất
        self.service = service  # thời gian phục vụ

class Depot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class TuyenXe:
    def __init__(self):
        self.customers = []
        self.load = 0
        self.cost = 0

class LoiGiai:
    def __init__(self):
        self.routes = []
        self.cost = 0
        self.so_xe = 0

# ===== KHOẢNG CÁCH =====
def dist(a, b):
    return math.sqrt((a.x - b.x)**2 + (a.y - b.y)**2)

# ===== KIỂM TRA TIME WINDOW =====
def kiem_tra_time(route, depot):
    time = 0
    prev = depot

    for c in route.customers:
        travel = dist(prev, c) / SPEED
        time += travel

        if time < c.ready:
            time = c.ready

        if time > c.due:
            return False  # vi phạm

        time += c.service
        prev = c

    # quay về depot
    time += dist(prev, depot) / SPEED

    return True

# ===== TÍNH CHI PHÍ =====
def tinh_chi_phi(route, depot):
    cost = 0
    prev = depot

    for c in route.customers:
        cost += dist(prev, c)
        prev = c

    cost += dist(prev, depot)
    return cost

# ===== ĐÁNH GIÁ =====
def danh_gia(solution, depot):
    total_cost = 0

    for route in solution.routes:
        route.cost = tinh_chi_phi(route, depot)
        total_cost += route.cost

    solution.cost = total_cost
    solution.so_xe = len(solution.routes)

# ===== KHỞI TẠO =====
def khoi_tao(customers, depot):
    population = []

    for _ in range(POP_SIZE):
        sol = LoiGiai()
        random.shuffle(customers)

        route = TuyenXe()

        for c in customers:
            if route.load + c.demand <= VEHICLE_CAPACITY:
                route.customers.append(c)
                route.load += c.demand
            else:
                if kiem_tra_time(route, depot):
                    sol.routes.append(route)
                route = TuyenXe()
                route.customers.append(c)
                route.load = c.demand

        if route.customers:
            sol.routes.append(route)

        danh_gia(sol, depot)
        population.append(sol)

    return population

# ===== LAI GHÉP =====
def lai_ghep(p1, p2, depot):
    child = LoiGiai()

    split = len(p1.routes) // 2
    child.routes = p1.routes[:split] + p2.routes[split:]

    danh_gia(child, depot)
    return child

# ===== ĐỘT BIẾN =====
def dot_bien(solution, depot):
    for route in solution.routes:
        if random.random() < MUTATION_RATE and len(route.customers) >= 2:
            i, j = random.sample(range(len(route.customers)), 2)
            route.customers[i], route.customers[j] = route.customers[j], route.customers[i]

    danh_gia(solution, depot)

# ===== PARETO =====
def dominates(a, b):
    return (a.cost <= b.cost and a.so_xe <= b.so_xe) and \
           (a.cost < b.cost or a.so_xe < b.so_xe)

def pareto(pop):
    front = []
    for p in pop:
        if not any(dominates(q, p) for q in pop):
            front.append(p)
    return front

# ===== MAIN =====
def run(customers, depot):
    population = khoi_tao(customers, depot)

    for _ in range(MAX_GEN):
        new_pop = []

        for _ in range(POP_SIZE):
            p1, p2 = random.sample(population, 2)

            if random.random() < CROSSOVER_RATE:
                child = lai_ghep(p1, p2, depot)
            else:
                child = p1

            dot_bien(child, depot)
            new_pop.append(child)

        population = new_pop

    return pareto(population)

# ===== TEST =====
if __name__ == "__main__":
    depot = Depot(0, 0)

    customers = [
        KhachHang(1, 10, 10, 10, 0, 100),
        KhachHang(2, 20, 20, 20, 10, 120),
        KhachHang(3, 15, 15, 15, 0, 100),
        KhachHang(4, 30, 30, 10, 20, 150),
        KhachHang(5, 25, 25, 20, 0, 200),
    ]

    ket_qua = run(customers, depot)

    print("\n=== KẾT QUẢ (CÓ TIME WINDOW + DEPOT) ===\n")

    for i, sol in enumerate(ket_qua):
        print(f"Giải pháp {i+1}:")
        print(f"  → Tổng chi phí: {sol.cost:.2f}")
        print(f"  → Số xe: {sol.so_xe}")

        for j, route in enumerate(sol.routes):
            ds = [c.id for c in route.customers]
            print(f"     Tuyến {j+1}: Depot -> {ds} -> Depot")

        print()