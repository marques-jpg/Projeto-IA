#!/usr/bin/env python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 39:
# 113868 Guilherme Marques
# 110126 António Correia

import sys
import random, copy
#from sys import stdin
from collections import defaultdict

import utils
from utils import *

from search import (
    Problem,
    Node,
    astar_search,
    breadth_first_tree_search,
    depth_first_tree_search,
    greedy_search,
    recursive_best_first_search,
    depth_first_graph_search,
)

class SlitherlinkState:
    def __init__(self, board, last_vertex=None):
        self.board = board
        self.last_vertex = last_vertex

    def __lt__(self, other):
        return False

class Board:
    def __init__(self, clues):
        self.clues = clues
        self.N = len(clues)
        self.M = len(clues[0])
        self.h_edges = [[0 for _ in range(self.M)] for _ in range(self.N + 1)]
        self.v_edges = [[0 for _ in range(self.M + 1)] for _ in range(self.N)]

    def get_cell_edges(self, row: int, col: int) -> list:
        return [
            ('h', row, col), ('h', row + 1, col),
            ('v', row, col), ('v', row, col + 1)
        ]

    def get_active_edges(self, row: int, col: int) -> int:
        count = 0
        for t, r, c in self.get_cell_edges(row, col):
            val = self.h_edges[r][c] if t == 'h' else self.v_edges[r][c]
            if val == 1: count += 1
        return count

    def copy(self):
        new_board = Board(self.clues)
        new_board.h_edges = [linha[:] for linha in self.h_edges]
        new_board.v_edges = [linha[:] for linha in self.v_edges]
        return new_board

    @staticmethod
    def parse_instance():
        clues_temp = []
        for line in sys.stdin:
            value = line.split()
            if value: clues_temp.append(value)
        return Board(tuple(tuple(l) for l in clues_temp))

    def display(self):
        for r in range(self.N + 1):
            h_line = ""
            for c in range(self.M):
                h_line += "."
                h_line += "---" if self.h_edges[r][c] == 1 else "   "
            h_line += "."
            print(h_line)
            
            if r < self.N:
                v_line = ""
                for c in range(self.M + 1):
                    v_line += "|" if self.v_edges[r][c] == 1 else " "
                    if c < self.M:
                        v_line += f" {self.clues[r][c]} "
                print(v_line)

class Slitherlink(Problem):
    def __init__(self, board: Board):
        super().__init__(SlitherlinkState(board))

    def actions(self, state: SlitherlinkState):
        board = state.board
        if state.last_vertex is None:
            r, c = self._find_best_starting_cell(board)
            return board.get_cell_edges(r, c)

        v_row, v_col = state.last_vertex
        candidates = self._get_edges_touching_vertex(board, v_row, v_col)
        
        valid_actions = []
        for action in candidates:
            t, r, c = action
            val = board.h_edges[r][c] if t == 'h' else board.v_edges[r][c]
            if val != 0: continue
            
            if self._is_consistent(board, action, state.last_vertex):
                valid_actions.append(action)
        return valid_actions

    def result(self, state: SlitherlinkState, action):
        new_board = state.board.copy()
        t, r, c = action
        if t == 'h': new_board.h_edges[r][c] = 1
        else: new_board.v_edges[r][c] = 1
        
        v_dest = self._get_destination(action, state.last_vertex)
        return SlitherlinkState(new_board, v_dest)

    def _get_destination(self, action, last_v):
        t, r, c = action
        if last_v is None: return (r, c)
        if t == 'h':
            return (r, c) if (r, c+1) == last_v else (r, c+1)
        return (r, c) if (r+1, c) == last_v else (r+1, c)

    def _find_best_starting_cell(self, board):
        for p in ['3', '2', '1']:
            for r in range(board.N):
                for c in range(board.M):
                    if board.clues[r][c] == p: return (r, c)
        return (0, 0)

    def _get_edges_touching_vertex(self, board, row, col):
        edges = []
        if col > 0: edges.append(('h', row, col - 1))
        if col < board.M: edges.append(('h', row, col))
        if row > 0: edges.append(('v', row - 1, col))
        if row < board.N: edges.append(('v', row, col))
        return edges

    def _is_consistent(self, board, action, last_v):
        t, r, c = action
        cells = []
        if t == 'h':
            if r > 0: cells.append((r - 1, c))
            if r < board.N: cells.append((r, c))
        else:
            if c > 0: cells.append((r, c - 1))
            if c < board.M: cells.append((r, c))

        for cr, cc in cells:
            clue = board.clues[cr][cc]
            if clue != '.':
                if board.get_active_edges(cr, cc) + 1 > int(clue):
                    return False

        v_dest = self._get_destination(action, last_v)
        if self._count_active_at_vertex(board, v_dest) >= 2:
            return False
            
        return True

    def _count_active_at_vertex(self, board, vertex):
        r, c = vertex
        count = 0
        for t, ar, ac in self._get_edges_touching_vertex(board, r, c):
            val = board.h_edges[ar][ac] if t == 'h' else board.v_edges[ar][ac]
            if val == 1: count += 1
        return count

    def goal_test(self, state: SlitherlinkState):
        board = state.board
        
        for r in range(board.N):
            for c in range(board.M):
                clue = board.clues[r][c]
                if clue != '.' and board.get_active_edges(r, c) != int(clue):
                    return False
        for r in range(board.N + 1):
            for c in range(board.M + 1):
                grau = self._count_active_at_vertex(board, (r, c))
                
                if grau != 0 and grau != 2:
                    return False
        return True

if __name__ == '__main__':
    board = Board.parse_instance()
    
    problem = Slitherlink(board)
    
    print("A procurar solução...")
    solucao_node = depth_first_tree_search(problem)
    
    if solucao_node:
        print("Sucesso! Solução encontrada.")
        final_board = solucao_node.state.board
        solucao_node.state.board.display()
    else:
        print("Não foi encontrada nenhuma solução.")