from random import (randint)
from typing import (List, Tuple, Set, Dict, Any)
from utils.utils import reshape_data
from collections import namedtuple

MATRIX_SIZE = 500


# 个体对象，染色体和适应度
class Gene(object):
    def __init__(self, fitness: float = 0, chromosome = None):
        self.fitness = fitness
        self.chromosome: list = chromosome

    def __eq__(self, other):
        if isinstance(other, Gene):
            return other.fitness == self.fitness and other.chromosome == self.chromosome
        return False

    def __hash__(self):
        return hash("".join(map(lambda x: str(x), self.chromosome)))

    def __str__(self):
        return "{} => {}".format(self.chromosome, self.fitness)


# 存储解码结果
class GeneEvaluation:
    def __init__(self):
        self.fulfill_time = 0
        self.machine_work_time = [0 for _ in range(MATRIX_SIZE)]
        self.process_ids = [0 for _ in range(MATRIX_SIZE)]
        self.end_time = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
        self.start_time = [[0 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]


# 遗传算法实现
class GA:
    def __init__(self, population_number = 50, times = 10, cross_probability = 0.95,
                 mutation_probability = 0.05, workpiece_number = 0, machine_number = 0):
        self.population_number = population_number  # 种群数量
        self.times = times  # 遗传代数
        self.cross_probability = cross_probability  # 交叉概率
        self.mutation_probability = mutation_probability  # 突变概率

        self.workpiece_number = workpiece_number  # 工件数量
        self.machine_number = machine_number  # 机器数量
        self.process_number: int = 0  # 工序数量
        self.chromosome_size: int = 0  # 染色体长度

        self.machine_matrix = [[-1 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
        self.time_matrix = [[-1 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]
        self.process_matrix = [[-1 for _ in range(MATRIX_SIZE)] for _ in range(MATRIX_SIZE)]

        self.genes: Set[Gene] = set()

    # 评估染色体
    def evaluate_gene(self, g: Gene) -> GeneEvaluation:
        evaluation = GeneEvaluation()
        # print(g.chromosome)
        for workpiece_id in g.chromosome:
            process_id = evaluation.process_ids[workpiece_id]
            machine_id = self.machine_matrix[workpiece_id][process_id]
            time = self.time_matrix[workpiece_id][process_id]
            evaluation.process_ids[workpiece_id] += 1
            evaluation.start_time[workpiece_id][process_id] = evaluation.machine_work_time[machine_id] \
                if process_id == 0 else max(evaluation.end_time[workpiece_id][process_id - 1],
                                            evaluation.machine_work_time[machine_id])
            evaluation.machine_work_time[machine_id] = evaluation.start_time[workpiece_id][process_id] + time
            evaluation.end_time[workpiece_id][process_id] = evaluation.machine_work_time[machine_id]
            evaluation.fulfill_time = max(evaluation.fulfill_time, evaluation.machine_work_time[machine_id])
        return evaluation

    # 计算适应度
    def calculate_fitness(self, g: Gene) -> float:
        return 1 / self.evaluate_gene(g).fulfill_time

    # 个体交叉
    def gene_cross(self, g1: Gene, g2: Gene) -> tuple:
        chromosome_size = self.chromosome_size

        def gene_generate(father: Gene, mother: Gene) -> Gene:
            index_list = list(range(chromosome_size))
            p1 = index_list.pop(randint(0, len(index_list) - 1))
            p2 = index_list.pop(randint(0, len(index_list) - 1))
            start = min(p1, p2)
            end = max(p1, p2)
            prototype = father.chromosome[start: end + 1]
            t = mother.chromosome[0:]
            for v1 in prototype:
                for i in range(len(t)):
                    if v1 == t[i]:
                        t.pop(i)
                        break
            child = Gene()
            child.chromosome = t[0: start] + prototype + t[start:]
            child.fitness = self.calculate_fitness(child)
            return child

        return gene_generate(g1, g2), gene_generate(g2, g1)

    # 突变
    def gene_mutation(self, g: Gene, n = 2) -> None:
        index_list = [i for i in range(self.chromosome_size)]
        for i in range(n):
            a = index_list.pop(randint(0, len(index_list) - 1))
            b = index_list.pop(randint(0, len(index_list) - 1))
            g.chromosome[a], g.chromosome[b] = g.chromosome[b], g.chromosome[a]

        g.fitness = self.calculate_fitness(g)

    # 初始化种群 [0, 1, 2, 1, 2, 0, 0, 1] => 12
    def init_population(self):
        for _ in range(self.population_number):
            g = Gene()
            size = self.workpiece_number * self.machine_number
            # print(self.workpiece_number, self.machine_number)
            index_list = list(range(size))
            chromosome = [-1 for _ in range(size)]
            for j in range(self.workpiece_number):
                for k in range(self.machine_number):
                    index = randint(0, len(index_list) - 1)
                    val = index_list.pop(index)
                    if self.process_matrix[j][k] != -1:
                        chromosome[val] = j
            g.chromosome = list(filter(lambda x: x != -1, chromosome))
            # print("chromosome:", g.chromosome)
            g.fitness = self.calculate_fitness(g)
            self.genes.add(g)

    # 选择个体，锦标赛法
    def select_gene(self, n: int = 3):

        if len(self.genes) <= 3:
            best_gene = Gene(0)
            for g in self.genes:
                if g.fitness > best_gene.fitness:
                    best_gene = g
            return best_gene

        index_list = list(range(len(self.genes)))
        index_set = {index_list.pop(randint(0, len(index_list) - 1)) for _ in range(n)}
        best_gene = Gene(0)
        i = 0
        for gene in self.genes:
            if i in index_set:
                if best_gene.fitness < gene.fitness:
                    best_gene = gene
            i += 1
        return best_gene

    # 遗传算法
    def exec(self, parameter: List[List[Tuple]]) -> GeneEvaluation:
        # print(parameter)
        workpiece_size = len(parameter)
        for i in range(workpiece_size):
            self.chromosome_size += len(parameter[i])
            self.process_number = max(self.process_number, len(parameter[i]))
            for j in range(len(parameter[i])):
                self.machine_matrix[i][j] = parameter[i][j][0]
                self.time_matrix[i][j] = parameter[i][j][1]

        for i in range(workpiece_size):
            for j in range(self.process_number):
                if self.machine_matrix[i][j] != -1:
                    self.process_matrix[i][self.machine_matrix[i][j]] = j

        self.init_population()

        for _ in range(self.times):
            probability = randint(1, 100) / 100
            if probability < self.mutation_probability:
                index = randint(0, len(self.genes))
                i = 0
                for gene in self.genes:
                    if i == index:
                        self.gene_mutation(gene)
                        break
                    i += 1
            else:
                g1, g2 = self.select_gene(), self.select_gene()
                children = self.gene_cross(g1, g2)
                self.genes.update({*children})

        best_gene = Gene(0)
        for gene in self.genes:
            if best_gene.fitness < gene.fitness:
                best_gene = gene

        return self.evaluate_gene(best_gene)


ResultData = namedtuple("ResultData", ["fulfill_time", "row_data", "json_data"])


# 输出结果
def schedule(data) -> ResultData:
    print(data)
    reshape = reshape_data(data)
    parameter = reshape.result
    print(parameter)
    n = len(reshape.workpiece)
    m = len(reshape.machine)  # number from 0
    print(m)
    ga = GA(workpiece_number = n, machine_number = m)
    result = ga.exec(parameter)
    p = ga.process_number
    machine_matrix = ga.machine_matrix
    row_data = []
    for i in range(n):
        for j in range(p):
            if machine_matrix[i][j] != -1:
                temp = {
                    "workpiece": reshape.workpiece[i],
                    "process": reshape.process[i][j],
                    "machine": reshape.machine[machine_matrix[i][j]],
                    "startTime": result.start_time[i][j],
                    "endTime": result.end_time[i][j]
                }
                # print(i, j, machine_matrix[i][j], result.start_time[i][j], result.end_time[i][j])
                row_data.append(temp)

    json_data = {}
    for i in range(n):
        for j in range(p):
            if machine_matrix[i][j] != -1:
                temp = {
                    "workpiece": reshape.workpiece[i],
                    "process": reshape.process[i][j],
                    "startTime": result.start_time[i][j],
                    "endTime": result.end_time[i][j]
                }
                m = reshape.machine[machine_matrix[i][j]]
                if m not in json_data:
                    json_data[m] = [temp]
                else:
                    json_data[m].append(temp)
    return ResultData(result.fulfill_time, row_data, json_data)


if __name__ == "__main__":
    d = [{'workpiece': '#W-89-10', 'process': '#P-1349-31', 'machine': '#M-8763-12', 'time': 10, 'order': 0},
         {'workpiece': '#W-89-10', 'process': '#P-6261-32', 'machine': '#M-2304-14', 'time': 21, 'order': 1},
         {'workpiece': '#W-89-10', 'process': '#P-6917-33', 'machine': '#M-6360-16', 'time': 12, 'order': 2},
         {'workpiece': '#W-5863-13', 'process': '#P-2772-34', 'machine': '#M-6557-17', 'time': 21, 'order': 0},
         {'workpiece': '#W-5863-13', 'process': '#P-468-35', 'machine': '#M-8763-12', 'time': 21, 'order': 1},
         {'workpiece': '#W-5829-8', 'process': '#P-3959-28', 'machine': '#M-2304-14', 'time': 5, 'order': 2},
         {'workpiece': '#W-5829-8', 'process': '#P-5852-27', 'machine': '#M-671-13', 'time': 11, 'order': 1},
         {'workpiece': '#W-5829-8', 'process': '#P-7792-26', 'machine': '#M-8763-12', 'time': 10, 'order': 0},
         {'workpiece': '#W-554-9', 'process': '#P-6810-29', 'machine': '#M-671-13', 'time': 5, 'order': 0}]
    print(schedule(d).row_data)
