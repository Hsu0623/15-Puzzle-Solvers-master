import heapq

class PuzzleSolver:
    def __init__(self, strategy):
        """
        :param strategy: Strategy
        """
        self._strategy = strategy

    def print_performance(self):
        print(f'{self._strategy} - Expanded Nodes: {self._strategy.num_expanded_nodes}')

    def print_solution(self):
        print('Solution:')
        for p in self._strategy.solution:
            print(p)

    def run(self):
        self._strategy.do_algorithm()


class Strategy:
    num_expanded_nodes = 0
    solution = None

    def do_algorithm(self):
        raise NotImplemented


class BreadthFirst(Strategy):
    def __init__(self, initial_puzzle):
        """
        :param initial_puzzle: Puzzle
        """
        self.start = initial_puzzle

    def __str__(self):
        return 'Breadth First'

    def do_algorithm(self):
        queue = [[self.start]]
        expanded = []
        num_expanded_nodes = 0
        path = None

        while queue:
            path = queue[0]
            queue.pop(0)  # dequeue (FIFO)
            end_node = path[-1]

            if end_node.position in expanded:
                continue

            for move in end_node.get_moves():
                if move.position in expanded:
                    continue
                queue.append(path + [move])  # add new path at the end of the queue

            expanded.append(end_node.position)
            num_expanded_nodes += 1

            if end_node.position == end_node.PUZZLE_END_POSITION:
                break

        self.num_expanded_nodes = num_expanded_nodes
        self.solution = path


class AStar(Strategy):
    def __init__(self, initial_puzzle):
        """
        :param initial_puzzle: Puzzle
        """
        self.start = initial_puzzle

    def __str__(self):
        return 'A*'

    @staticmethod
    def _calculate_new_heuristic(move, end_node):
        return move.heuristic_manhattan_distance() - end_node.heuristic_manhattan_distance()
        #return move.heuristic_misplaced() - end_node.heuristic_misplaced()
    
    def do_algorithm(self):
        queue = []
        heapq.heappush(queue, [self.start.heuristic_manhattan_distance(),self.start])
        #queue = [[self.start.heuristic_misplaced(), self.start]]
        #queue = [[self.start.heuristic_manhattan_distance(), self.start]]
        expanded = []
        num_expanded_nodes = 0
        path = None

        while queue:
            i = 0
            #print(queue)
            """
            for j in range(1, len(queue)):
                if queue[i][0] > queue[j][0]:  # minimum
                    i = j
            """
            #path = queue[i]
            #queue = queue[:i] + queue[i + 1:]
            path = heapq.heappop(queue)
            end_node = path[-1]
            
            #print(end_node)
            if end_node.position == end_node.PUZZLE_END_POSITION:
                break
            if end_node.position in expanded:
                continue

            for move in end_node.get_moves():
                if move.position in expanded:
                    continue
                new_path = [path[0]+self._calculate_new_heuristic(move,end_node)] + path[1:] + [move]
                heapq.heappush(queue,new_path)
                #new_path = [path[0] + self._calculate_new_heuristic(move, end_node)] + path[1:] + [move] 
                #print(new_path)
                #queue.append(new_path)
                expanded.append(end_node.position)

            num_expanded_nodes += 1

        self.num_expanded_nodes = num_expanded_nodes
        self.solution = path[1:]


class Puzzle:
    def __init__(self, position):
        """
        :param position: a list of lists representing the puzzle matrix
        """
        self.position = position
        self.PUZZLE_NUM_ROWS = len(position)
        self.PUZZLE_NUM_COLUMNS = len(position[0])
        self.PUZZLE_END_POSITION = self._generate_end_position()
    
    def __lt__(self, other):
        return self.PUZZLE_NUM_COLUMNS <= other.PUZZLE_NUM_COLUMNS
    
    def __str__(self):
        """
        Print in console as a matrix
        """
        puzzle_string = '???' * 13 + '\n'
        for i in range(self.PUZZLE_NUM_ROWS):
            for j in range(self.PUZZLE_NUM_COLUMNS):
                puzzle_string += '???{0: >2}'.format(str(self.position[i][j]))
                if j == self.PUZZLE_NUM_COLUMNS - 1:
                    puzzle_string += '???\n'

        puzzle_string += '???' * 13 + '\n'
        return puzzle_string

    def _generate_end_position(self):
        """
        Example end position in 4x4 puzzle
        [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15]]
        """
        end_position = []
        new_row = []

        for i in range(self.PUZZLE_NUM_ROWS * self.PUZZLE_NUM_COLUMNS):
            new_row.append(i)
            if len(new_row) == self.PUZZLE_NUM_COLUMNS:
                end_position.append(new_row)
                new_row = []

        return end_position

    def _swap(self, x1, y1, x2, y2):
        """
        Swap the positions between two elements
        """
        puzzle_copy = [list(row) for row in self.position]  # copy the puzzle
        puzzle_copy[x1][y1], puzzle_copy[x2][y2] = puzzle_copy[x2][y2], puzzle_copy[x1][y1]

        return puzzle_copy

    def _get_coordinates(self, tile, position=None):
        """
        Returns the i, j coordinates for a given tile
        """
        if not position:
            position = self.position

        for i in range(self.PUZZLE_NUM_ROWS):
            for j in range(self.PUZZLE_NUM_COLUMNS):
                if position[i][j] == tile:
                    return i, j

        return RuntimeError('Invalid tile value')

    def get_moves(self):
        """
        Returns a list of all the possible moves
        """
        moves = []
        i, j = self._get_coordinates(0)  # blank space

        if i > 0:
            moves.append(Puzzle(self._swap(i, j, i - 1, j)))  # move up

        if j < self.PUZZLE_NUM_COLUMNS - 1:
            moves.append(Puzzle(self._swap(i, j, i, j + 1)))  # move right

        if j > 0:
            moves.append(Puzzle(self._swap(i, j, i, j - 1)))  # move left

        if i < self.PUZZLE_NUM_ROWS - 1:
            moves.append(Puzzle(self._swap(i, j, i + 1, j)))  # move down

        return moves

    def heuristic_misplaced(self):
        """
        Counts the number of misplaced tiles
        """
        misplaced = 0

        for i in range(self.PUZZLE_NUM_ROWS):
            for j in range(self.PUZZLE_NUM_COLUMNS):
                if self.position[i][j] != self.PUZZLE_END_POSITION[i][j]:
                    misplaced += 1

        return misplaced

    def heuristic_manhattan_distance(self):
        """
        Counts how much is a tile misplaced from the original position
        """
        distance = 0

        for i in range(self.PUZZLE_NUM_ROWS):
            for j in range(self.PUZZLE_NUM_COLUMNS):
                i1, j1 = self._get_coordinates(self.position[i][j], self.PUZZLE_END_POSITION)
                distance += abs(i - i1) + abs(j - j1)

        return distance


if __name__ == '__main__':
    puzzle = Puzzle([[4, 1, 2, 5], [3, 6, 7, 0], [8, 9, 11, 10], [12, 13, 14, 15]])
    """
    for strategy in [BreadthFirst, AStar]:
        p = PuzzleSolver(strategy(puzzle))
        p.run()
        p.print_performance()
        p.print_solution()
    """
    strategy = AStar
    p = PuzzleSolver(strategy(puzzle))
    p.run()
    p.print_performance()
    p.print_solution()