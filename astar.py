from queue import PriorityQueue
import pygame
import math

WIDTH = 800

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
CYAN = (64, 224, 208)

WINDOW = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* maze solver")

class Node:

	def __init__(self, row, col, width, totalRows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.totalRows = totalRows

	def getPosition(self):
		return self.row, self.col

	def isClosed(self):
		return self.color == RED

	def isOpen(self):
		return self.color == GREEN

	def isStart(self):
		return self.color == ORANGE

	def isBarrier(self):
		return self.color == BLACK

	def isEnd(self):
		return self.color == CYAN

	def reset(self):
		self.color = WHITE

	def makeClosed(self):
		self.color = RED

	def makeOpen(self):
		self.color = GREEN

	def makeBarrier(self):
		self.color = BLACK

	def makeStart(self):
		self.color = ORANGE

	def makeEnd(self):
		self.color = CYAN

	def makePath(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def updateNeighbors(self, grid):
		self.neighbors = []
		if self.row < self.totalRows - 1 and not grid[self.row + 1][self.col].isBarrier():
			self.neighbors.append(grid[self.row + 1][self.col])
		if self.row > 0 and not grid[self.row - 1][self.col].isBarrier():
			self.neighbors.append(grid[self.row - 1][self.col])
		if self.col < self.totalRows - 1 and not grid[self.row][self.col + 1].isBarrier():
			self.neighbors.append(grid[self.row][self.col + 1])
		if self.col > 0 and not grid[self.row][self.col - 1].isBarrier():
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False

def heuristic(point1, point2):
	x1, y1 = point1
	x2, y2 = point2
	return abs(x1 - x2) + abs(y1 - y2)

def makeGrid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			node = Node(i, j, gap, rows)
			grid[i].append(node)
	return grid

def drawGrid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i*gap))
		pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))

def draw(win, grid, rows, width):
	win.fill(WHITE)
	for row in grid:
		for node in row:
			node.draw(win)
	drawGrid(win, rows, width)
	pygame.display.update()


def getMousePosition(pos, rows, width):
	gap = width // rows
	y, x = pos
	row = y // gap
	col = x // gap
	return row, col

def reconstructPath(father, current, draw):
	while current in father:
		current = father[current]
		current.makePath()
		draw()

def solveMaze(draw, grid, start, end):
	count = 0
	Q = PriorityQueue()
	Q.put((0, count, start))
	father = {}
	gScore = {node: float("inf") for row in grid for node in row}
	gScore[start] = 0
	fScore = {node: float("inf") for row in grid for node in row}
	fScore[start] = heuristic(start.getPosition(), end.getPosition())
	QHash = {start}
	while not Q.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
		current = Q.get()[2]
		QHash.remove(current)
		if current == end:
			reconstructPath(father, end, draw)
			end.makeEnd()
			return True
		for neighbor in current.neighbors:
			tempGScore = gScore[current] + 1
			if tempGScore < gScore[neighbor]:
				father[neighbor] = current
				gScore[neighbor] = tempGScore
				fScore[neighbor] = tempGScore + heuristic(neighbor.getPosition(), end.getPosition())
				if neighbor not in QHash:
					count += 1
					Q.put((fScore[neighbor], count, neighbor))
					QHash.add(neighbor)
					neighbor.makeOpen()
		draw()
		if current != start:
			current.makeClosed()
	return False

def main(win, width):
	ROWS = 50
	grid = makeGrid(ROWS, width)
	start = None
	end = None
	run = True
	started = False
	while run:
		draw(win, grid, ROWS, width)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
			if pygame.mouse.get_pressed()[0]:
				pos = pygame.mouse.get_pos()
				row, col = getMousePosition(pos, ROWS, width)
				node = grid[row][col]
				if not start:
					start = node
					start.makeStart()
				elif not end and node != start:
					end = node
					end.makeEnd()
				elif node != end and node != start:
					node.makeBarrier()
			elif pygame.mouse.get_pressed()[2]:
				pos = pygame.mouse.get_pos()
				row, col = getMousePosition(pos, ROWS, width)
				node = grid[row][col]
				node.reset()
				if node == start:
					start = None
				elif node == end:
					end = None

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE and start and end:
					for row in grid:
						for node in row:
							node.updateNeighbors(grid)

					solveMaze(lambda: draw(win, grid, ROWS, width), grid, start, end)
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = makeGrid(ROWS, width)

	pygame.quit()

main(WINDOW, WIDTH)