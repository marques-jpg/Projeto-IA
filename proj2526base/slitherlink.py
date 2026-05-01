#!/usr/bin/env python3
# slitherlink.py: Template para implementação do projeto de Inteligência Artificial 2025/2026.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes sugeridas, podem acrescentar outras que considerem pertinentes.

# Grupo 39:
# 113868 Guilherme Marques
# 110126 António Correia

import random, copy
from sys import stdin
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
)


class SlitherlinkState:
    state_id = 0


    def __init__(self, board):
        self.board = board
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1
    
    def __lt__(self, other):
        return self.id < other.id

    # TODO: outros metodos da classe

class Board:
    """Representação interna de um tabuleiro de Slitherlink."""
    def __init__(self, clue):
        self.clue = clue
        N = len(clue)
        M = len(clue[0])

        self.h_edges = [[0 for _ in range(M)] for _ in range(N+1)]
        self.v_edges = [[0 for _ in range(M+1)] for _ in range(N)]

    def adjacent_cell(self, cell:tuple) -> list:
        """Devolve uma lista das células que fazem
        fronteira com a célula enviada no argumento"""
        #TODO
        pass

    def get_cell_edges(self, row:int, column:int) -> list:
        """Devolve os arestas da célula enviada no argumento"""
        #TODO
        pass

    def get_active_edges(self, row:int, column:int) -> list:
        """Devolve o número de arestas ativas"""
        #TODO
        pass


    @staticmethod
    def parse_instance():
        import sys
        clues_temp = []
        for line in sys.stdin:
            value = line.split()
            if value:
                clues_temp.append(value)
        clues_tuple = tuple(tuple(line) for line in clues_temp)
        return Board(clues_tuple)

    # TODO: outros metodos da classe

class Slitherlink(Problem):
    def __init__(self, board: Board, gui=None):
        """O construtor especifica o estado inicial."""
        # TODO
        pass


    def actions(self, state: SlitherlinkState):
        """Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento."""
        # TODO
        pass


    def result(self, state: SlitherlinkState, action):
        """Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de
        self.actions(state)."""
        # TODO
        pass

    def goal_test(self, state: SlitherlinkState):
        """Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro
        estão preenchidas de acordo com as regras do problema."""
        # TODO
        pass

    def h(self, node: Node):
        """Função heuristica utilizada para a procura A*."""
        # TODO
        pass

    


if __name__ == '__main__':
    meu_board = Board.parse_instance()
    
    print("--- Clues Read ---")
    for linha in meu_board.clue:
        print(linha)
        
    print("\n--- Internal Dimensions ---")
    print(f"Clues Matrixs   : {len(meu_board.clue)} lines x {len(meu_board.clue[0])} columns")
    print(f"h_edges Matrix  : {len(meu_board.h_edges)} lines x {len(meu_board.h_edges[0])} columns")
    print(f"v_edges Matrix  : {len(meu_board.v_edges)} lines x {len(meu_board.v_edges[0])} columns")







