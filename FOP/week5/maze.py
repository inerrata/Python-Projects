class Maze():
    # visualization characters
    block = "\uFF03"
    empty = "\u3000"
    path = "\uFF0A"

    def __init__(self, start, transitions):
        """ A maze has two objects that you need to use to solve the assignment"""
        self.start = start
        self.transitions = transitions

        # This is for visualization purposes and you do not need for the assignment
        width = max(self.transitions, key=lambda x: x[0])[0]
        height = max(self.transitions, key=lambda x: x[1])[1]
        self.maze = [[Maze.block] * (width + 3), [Maze.block] * (width + 3)]
        for j in range(height + 1):
            row = [Maze.block, Maze.block]
            for i in range(width + 1):
                row.insert(-1, Maze.empty if (i, j) in self.transitions else Maze.block)
            self.maze.insert(-1, row)

    def __repr__(self):
        """ The representation of the maze """
        return '\n'.join([''.join(row) for row in self.maze])

    def show(self, route):
        """ Shows the representation of the maze including the route """
        maze = self.maze.copy()
        for pos in route:
            maze[pos[1] + 1][pos[0] + 1] = Maze.path if "codegrade" in __file__ else f"\033[31m{Maze.path}\033[0m"
        print('\n'.join([''.join(row) for row in maze]))

# Your functions here

def find_route(maze: Maze, end: tuple[int, int]):

    start = maze.start
    visited = set()
    route = find_route_rec(maze, start, end, visited)

    # If there is no route, give error
    if route is None:
        print("Warning: no route can be found!")
        return []

    return route


def find_route_rec(maze: Maze, current: tuple[int, int], end: tuple[int, int], visited: set = None):

    # If current position is end, return it
    if current == end:
        return [current]

    # Mark as visited
    visited.add(current)

    # Look at adjacent
    for neighbor in maze.transitions.get(current, []):
        if neighbor not in visited:
            result = find_route_rec(maze, neighbor, end, visited)
            if result is not None:
                return [current] + result

    return None

# Maze 1
maze1_start = (0, 0)
maze1_transitions = {
    (0, 0): [(1, 0)],
    (1, 0): [(2, 0), (1, 1)],
    (2, 0): [],
    (1, 1): [(1, 2)],
    (1, 2): [(2, 2)],
    (2, 2): []
}
if __name__ == "__main__":
    # Script code here
    maze = Maze(maze1_start, maze1_transitions)
    end_cell = (2, 2)

    route = find_route(maze, end_cell)
    maze.show(route)
