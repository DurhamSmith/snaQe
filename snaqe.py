#Snake Tutorial Python
import dwave
from pyqubo import Binary, solve_qubo
from dwave.system import DWaveSampler, EmbeddingComposite
from dimod import ExactSolver
from pyqubo import Binary
import networkx as nx
#import dwave_networkx as dnx
import math
import random
import pygame
import tkinter as tk
import dimod
from tkinter import messagebox
import pickle
import json
from dimod.serialization.json import DimodEncoder, DimodDecoder

GRID_SIZE = 3
NON_SNAKE_WEIGHTS=1
SNAKE_WEIGHTS=100
CHI = 3
LAMBDA = 10
MU = 2
GAMMA = 10

class cube(object):
    rows = 20
    w = 500
    def __init__(self,start,dirnx=1,dirny=0,color=(0,255,0)):
        self.pos = start
        self.dirnx = 1
        self.dirny = 0
        self.color = color


    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        dis = self.w // self.rows
        i = self.pos[0]
        j = self.pos[1]

        pygame.draw.rect(surface, self.color, (i*dis+1,j*dis+1, dis-2, dis-2))
        if eyes:
            centre = dis//2
            radius = 3
            circleMiddle = (i*dis+centre-radius,j*dis+8)
            circleMiddle2 = (i*dis + dis -radius*2, j*dis+8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)



class snake(object):
    body = []
    turns = {}
    def __init__(self, color, pos):
        self.color = color
        self.head = cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            keys = pygame.key.get_pressed()

            for key in keys:
                if keys[pygame.K_LEFT]:
                    self.dirnx = -1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_RIGHT]:
                    self.dirnx = 1
                    self.dirny = 0
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_UP]:
                    self.dirnx = 0
                    self.dirny = -1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

                elif keys[pygame.K_DOWN]:
                    self.dirnx = 0
                    self.dirny = 1
                    self.turns[self.head.pos[:]] = [self.dirnx, self.dirny]

        for i, c in enumerate(self.body):
            p = c.pos[:]
            if p in self.turns:
                turn = self.turns[p]
                c.move(turn[0],turn[1])
                if i == len(self.body)-1:
                    self.turns.pop(p)
            else:
                if c.dirnx == -1 and c.pos[0] <= 0: c.pos = (c.rows-1, c.pos[1])
                elif c.dirnx == 1 and c.pos[0] >= c.rows-1: c.pos = (0,c.pos[1])
                elif c.dirny == 1 and c.pos[1] >= c.rows-1: c.pos = (c.pos[0], 0)
                elif c.dirny == -1 and c.pos[1] <= 0: c.pos = (c.pos[0],c.rows-1)
                else: c.move(c.dirnx,c.dirny)


    def move_via_dwave():
        # 1: Embed Graph
        # 2: Create Qubo
        # 3: Pass Qubo to Dwave
        # 4: Unpack qubo to graph
        # 5:
        pass

    def get_snake_unconnected_graph(self):
        # G = nx.Graph()
        # for i in range(grid_size):
        #     for j in range(grid_size):
        #         G.add_node((i,j))
        G = nx.grid_2d_graph(GRID_SIZE, GRID_SIZE, periodic =False)
        nx.set_edge_attributes(G, NON_SNAKE_WEIGHTS, "weight" )
        return G

    def snake_to_graph(self):
        G = s.get_snake_unconnected_graph()
        prev_cube_pos = False
        for cube in self.body:
            print(f'snake body cube: {cube.pos}')
            if prev_cube_pos:
                G.add_edge(cube.pos, prev_cube_pos, weight=SNAKE_WEIGHTS)
            prev_cube_pos = cube.pos
        #nx.bipartite_layout(G,G.nodes())
        #nx.draw(G)
        #print(f'xs: {G.nodes()}')

        return G


    def graph_to_moves(self, path_graph):
        num_moves = len(path_graph.edges)
        moves = []
        head_pos = self.body[0].pos
        prev_head_poses = []
        prev_head_poses.append(head_pos)
        run_flag = True
        print(f'all edges: {path_graph.edges()}')
        for i in range(len(path_graph.edges)):
            for edges in path_graph.edges(head_pos):
                print(f'head_pos {head_pos}')
                print(f'edges: {edges}')
                for edge in edges:
                    print(f'loop edge: {edge}')
                    if edge not in prev_head_poses:
                        print("AS")
                        prev_head_poses.append(head_pos)
                        moves.append((head_pos[0]-edge[0], head_pos[1]-edge[1]))
                        head_pos = edge
                        break
        print(moves)

        # while run_flag:
        #     if len(path_graph.edges(head_pos)) == 1 and head_pos not in prev_head_poses:
        #         run_flag = False
        #     for edges in path_graph.edges(head_pos):
        #         for edge in edges:
        #             if edge not in prev_head_poses:
        #                 print(f'len:{len(path_graph.edges(head_pos))}  head: {head_pos} edge:{edge}')
        #                 moves = (head_pos[0]-edge[0], head_pos[1]-edge[1])
        #                 head_pos = edge

        #                 break
        # print(f'moves: {moves}')



    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1


    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0]-1,tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1,tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0],tail.pos[1]-1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0],tail.pos[1]+1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy


    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i ==0:
                c.draw(surface, True)
            else:
                c.draw(surface)


def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

#        pygame.draw.line(surface, (000,000,000), (x,0),(x,w))
 #       pygame.draw.line(surface, (255,000), (0,y),(w,y))


def redrawWindow(surface):
    global rows, width, s, snack
    surface.fill((255,255,255))
    s.draw(surface)
    snack.draw(surface)
    drawGrid(width,rows, surface)
    pygame.display.update()


def randomSnack(rows, item):

    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z:z.pos == (x,y), positions))) > 0:
            continue
        else:
            break

    return (x,y)

    def reset(self, pos):
        self.head = cube(pos)
        self.body = []
        self.body.append(self.head)
        self.turns = {}
        self.dirnx = 0
        self.dirny = 1


    def addCube(self):
        tail = self.body[-1]
        dx, dy = tail.dirnx, tail.dirny

        if dx == 1 and dy == 0:
            self.body.append(cube((tail.pos[0]-1,tail.pos[1])))
        elif dx == -1 and dy == 0:
            self.body.append(cube((tail.pos[0]+1,tail.pos[1])))
        elif dx == 0 and dy == 1:
            self.body.append(cube((tail.pos[0],tail.pos[1]-1)))
        elif dx == 0 and dy == -1:
            self.body.append(cube((tail.pos[0],tail.pos[1]+1)))

        self.body[-1].dirnx = dx
        self.body[-1].dirny = dy


    def draw(self, surface):
        for i, c in enumerate(self.body):
            if i ==0:
                c.draw(surface, True)
            else:
                c.draw(surface)


def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

#        pygame.draw.line(surface, (000,000,000), (x,0),(x,w))
 #       pygame.draw.line(surface, (255,000), (0,y),(w,y))


def redrawWindow(surface):
    global rows, width, s, snack
    surface.fill((255,255,255))
    s.draw(surface)
    snack.draw(surface)
    drawGrid(width,rows, surface)
    pygame.display.update()


def randomSnack(rows, item):

    positions = item.body

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if len(list(filter(lambda z:z.pos == (x,y), positions))) > 0:
            continue
        else:
            break

    return (x,y)


def message_box(subject, content):
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.withdraw()
    messagebox.showinfo(subject, content)
    try:
        root.destroy()
    except:
        pass


class PathSolver():
    def __init__(self, graph, snake, apple_pos):
        self.head = snake.body[0].pos
        self.snake = snake
        self.apple = apple_pos
        self.graph = graph.copy()
        self.vars = self.create_vars()
        self.get_qubo()
        self.run_dwave()
        self.get_shortest_path_graph()
        self.get_moves()

    def get_shortest_path_graph(self):
        graph = nx.grid_2d_graph(GRID_SIZE, GRID_SIZE, periodic =False)
        self.path_edges = []
        for edge in graph.edges():
            try:
                if self.sampleset.first.sample[f'{edge}']:
                    print(f'{edge} MADE IT')
                    self.path_edges.append(edge)
                #nx.set_edge_attributes(graph, f'{edge}', 
                
                #print(f"we made it: {edge}")
            except KeyError:
                print(edge)
                #print(f'No Key: {edge}')

    def get_moves(self):
        temp_head = self.head
        i = 0
        self.moves = []
        while(i< len(self.path_edges)):
            for path_edge in self.path_edges:
                if path_edge[0] == temp_head:
                    self.moves.append((path_edge[1][0] - temp_head[0], path_edge[1][1] - temp_head[1]))
                    temp_head = path_edge[1]
                    i+=1
        print(self.moves)

    def run_dwave(self):
        #sampler = DWaveSampler().sample_qubo(self.qubo)
        print(len(self.qubo))

 #       Dwavesolver = EmbeddingComposite(DWaveSampler())
#        sampleset = Dwavesolver.sample_qubo(self.qubo, num_reads=1000)
        self.sampleset = ExactSolver().sample_qubo(self.qubo)
        #print(f'SAMPLE: {self.sampleset.first}')
        for k,v in self.sampleset.first.sample.items():
            print(f'Key: {k}\t\t\t\t Val: {v}')
        
  #      Q.update(coupler_strengths)
        # Sample once on a D-Wave system and print the returned sample
        #response = DWaveSampler().sample_qubo(Q, num_reads=1)


        #print(sampleset)

    def get_qubo(self):
        H= self.one_body_terms() + self.two_body_terms() + self.get_justin_trubo()
        model = H.compile()
        #print(model)
        self.qubo, self.offset = model.to_qubo()
        #print(f'QUBO:\n {self.qubo}')
        

    def create_vars(self):
       vars ={}
       print('===========MAPPINGS==============')
       for i, edge in enumerate(self.graph.edges.data()):
           e=(edge[0],edge[1])
           print(f'edge: {e} \t data: {edge[2]}')
           label = f'({edge[0]}, {edge[1]})'
           vars[e] = Binary(label)
       return vars
    
    def two_body_terms(self):
        #twobody head terms
        #Checked @ 10:04
        H=0
        H1=0
        for head_edge_1 in self.head_edges:
            for head_edge_2 in self.head_edges:
                if head_edge_1 == head_edge_2:
                    H1 += LAMBDA*self.vars[head_edge_1]*self.vars[head_edge_2]
                else:
                    H1 += LAMBDA*self.vars[head_edge_1]*self.vars[head_edge_2]

        #apple twobody terms
        # Checked @ 10:06
        H2=0
        for apple_edge_1 in self.apple_edges:
            for apple_edge_2 in self.apple_edges:
                if apple_edge_1 == apple_edge_2:
                    H2 +=GAMMA*self.vars[apple_edge_1]*self.vars[apple_edge_2]
                else:
                    H2 += GAMMA*self.vars[apple_edge_1]*self.vars[apple_edge_2]


        #make sure graph is connected
        H3=0
        for edge in self.graph.edges():
            e=self.get_valid_key(edge)
            for nodal_edge in self.graph.edges(e[0]):
                n = self.get_valid_key(nodal_edge)
                if  e == n:
                    pass
                else:
                    #print(f'EDGE: {e} OTHER EDGE: {n} FORMULA: {-1*MU*self.vars[n]*self.vars[e]}')
                    H3 -= MU*self.vars[n]*self.vars[e]
            for nodal_edge in self.graph.edges(e[1]):
                n = self.get_valid_key(nodal_edge)
                if e == n:
                    pass
                else:
                    #print(f'EDGE: {e} OTHER EDGE: {n} FORMULA: {-1*MU*self.vars[n]*self.vars[e]}')
                    H3 -= MU*self.vars[n]*self.vars[e]


        #manby body terms
        #Checked at 10:37
        H4=0
        for edge_1 in self.graph.edges():
            e1 = self.get_valid_key(edge_1)
            if e1 in self.apple_edges or e1 in self.head_edges:
                pass
            else:
                for edge_2 in self.graph.edges():
                    e2 = self.get_valid_key(edge_2)

                    if e2 in self.apple_edges or e2 in self.head_edges or e2 in self.head_neck_edge:
                        pass
                    else:
                        #print(f'edge1: {e1} edge2 {e2} forumla {-2*CHI*self.vars[e1]*self.vars[e2]}')
                        H4 += -2*CHI*self.vars[e1]*self.vars[e2]
        #print(H4)
        H = H1+H2+H3+H4
        return H

    def get_justin_trubo(self):
        #Checked @ 10:46
        H=0
        for edge_1 in self.graph.edges():
            e1 = self.get_valid_key(edge_1)
            if e1 in self.apple_edges or e1 in self.head_edges or e1 == self.head_neck_edge:
                pass
            else:
                for edge_2 in self.graph.edges():
                    e2 = self.get_valid_key(edge_2)
                    if e2 in self.apple_edges or e2 in self.head_edges or e2 == self.head_neck_edge:
                        pass
                    else:
                        for edge_3 in self.graph.edges():
                            e3 = self.get_valid_key(edge_3)
                            if e3 in self.apple_edges or e3 in self.head_edges or e3 == self.head_neck_edge:
                                pass
                            else:
                                #print(f'Edge1: {e1}\tEdge2: {e2}\tEdge3: {e3}\tFormula: {CHI*self.vars[e1]*self.vars[e2]*self.vars[e3]}')
                                H += CHI*self.vars[e1]*self.vars[e2]*self.vars[e3]
        #print(H)
        return H



    def get_node(self, tup):
        if tup[0][0] == tup[1][0]:
            return tup[0][0]
        if tup[0][0] == tup[1][1]:
            return tup[0][0]
        if tup[0][1] == tup[1][0]:
            return tup[0][1]
        if tup[0][1] == tup[1][1]:
            return tup[0][1]


    def one_body_terms(self):
        #Distance traversted term
        H = 0
        H1 = 0
        #checked H1 @ 09:12
        for edge in self.graph.edges.data():
            dict_key = self.get_valid_key((edge[0],edge[1]))
            #print(edge[2]["weight"])
            H1 += edge[2]["weight"]*self.vars[dict_key]
        
        #Links around the head term
        #checked @ 09:37
        H2=0
        self.head_edges = []
        head_neck_edge = self.get_valid_key((self.head, self.snake.body[1].pos))
        self.head_neck_edge = head_neck_edge
        # print(f'head_neck_edge: {head_neck_edge}')
        for edge in self.graph.edges(self.head):
            head_edge = self.get_valid_key(edge)
            # print(f'head_edge: {head_edge}')
            if not self.get_valid_key(head_edge) == self.get_valid_key(head_neck_edge):
                H2 -= 2*LAMBDA*self.vars[head_edge]
                self.head_edges.append(head_edge)

                
        #Links around the apple term
        #Checked at 09:38
        H3=0
        self.apple_edges=[]
        for edge in self.graph.edges(self.apple):
            apple_edge = self.get_valid_key(edge)
            H3 -= 2*GAMMA*self.vars[apple_edge]
            self.apple_edges.append(apple_edge)

        #Links from 3body bulk term
        # checked @ 09:55
        H4=0
        for edge in self.graph.edges():
            e = self.get_valid_key(edge)
            if e not in self.head_edges and edge not in self.apple_edges and not e==head_neck_edge:
                H4 += 4*CHI*self.vars[self.get_valid_key(edge)]

        H= H1 + H2 + H3 + H4

        return H



    def get_valid_key(self, key):
        if key in self.vars:
            return key
        elif (key[1], key[0]) in self.vars:
            return (key[1], key[0])
        else:
            raise "Awer"





def main():
    global width, rows, s, snack, sampleset
    width = 500
    rows = 10
    #win = pygame.display.set_mode((width, width))
    s = snake((0,255,0), (1,1)) #snake starts at rtupple
    #snack = cube(randomSnack(rows, s), color=(255,0,0))
    snack = cube(randomSnack(3, s), color=(255,0,0))
    flag = True


    s.addCube()
    s.snake_to_graph()
    H=s.get_snake_unconnected_graph()
    H.add_node((10,10))
    H.add_node((11,10))
    H.add_node((11,11))
    H.add_edge((10,10),(11,10))
    H.add_edge((11,10),(11,11))
    print(f'HYPERS \t LAMBDA: {LAMBDA}\t CHI: {CHI}\t MU: {MU}\t GAMMA: {GAMMA}')
    ps=PathSolver(s.snake_to_graph(), s, (2, 2))

#    s.graph_to_moves(H)


    # clock = pygame.time.Clock()

    # while flag:
    #     pygame.time.delay(50)
    #     clock.tick(10)
    #     s.move()
    #     if s.body[0].pos == snack.pos:
    #         s.addCube()
    #         snack = cube(randomSnack(rows, s), color=(255,0,0))
    #         for block in s.body:
    #             print(block.pos)


    #     for x in range(len(s.body)):
    #         if s.body[x].pos in list(map(lambda z:z.pos,s.body[x+1:])):
    #             print('Score: ', len(s.body))
    #             message_box('You Lost!', 'Play again...')
    #             s.reset((10,10))
    #             break


    #     redrawWindow(win)


    # pass



main()
