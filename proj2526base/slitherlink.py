#!/usr/bin/env python3
# slitherlink.py: Implementação do projeto de Inteligência Artificial 2025/2026.
# Grupo 39:
# 113868 Guilherme Marques
# 110126 António Correia

import sys
from search import (
    Problem,
    Node,
    depth_first_tree_search
)

class SlitherlinkState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = SlitherlinkState.state_id
        SlitherlinkState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id

class Board:
    def __init__(self, clues):
        self.clues = clues
        self.N = len(clues)
        self.M = len(clues[0])
        self.h_edges = [[-1 for _ in range(self.M)] for _ in range(self.N + 1)]
        self.v_edges = [[-1 for _ in range(self.M + 1)] for _ in range(self.N)]

    def get_cell_edges(self, row: int, col: int) -> list:
        return [
            ('h', row, col),       # Top
            ('v', row, col + 1),   # Right
            ('h', row + 1, col),   # Bottom
            ('v', row, col)        # Left
        ]

    def get_edge_val(self, t: str, r: int, c: int) -> int:
        return self.h_edges[r][c] if t == 'h' else self.v_edges[r][c]

    def set_edge_val(self, t: str, r: int, c: int, val: int):
        if t == 'h': self.h_edges[r][c] = val
        else: self.v_edges[r][c] = val

    def get_active_edges(self, row: int, col: int) -> int:
        return sum(1 for t, r, c in self.get_cell_edges(row, col) if self.get_edge_val(t, r, c) == 1)

    def get_unknown_edges(self, row: int, col: int) -> list:
        return [(t, r, c) for t, r, c in self.get_cell_edges(row, col) if self.get_edge_val(t, r, c) == -1]

    def get_edges_touching_vertex(self, vr: int, vc: int) -> list:
        edges = []
        if vc > 0: edges.append(('h', vr, vc - 1))
        if vc < self.M: edges.append(('h', vr, vc))
        if vr > 0: edges.append(('v', vr - 1, vc))
        if vr < self.N: edges.append(('v', vr, vc))
        return edges

    @staticmethod
    def get_other_vertex(edge, v):
        """ Devolve o vértice oposto de uma aresta. """
        t, r, c = edge
        v1 = (r, c)
        v2 = (r, c + 1) if t == 'h' else (r + 1, c)
        return v2 if v == v1 else v1

    def copy(self):
        new_board = Board(self.clues)
        new_board.h_edges = [row[:] for row in self.h_edges]
        new_board.v_edges = [row[:] for row in self.v_edges]
        return new_board

    @staticmethod
    def parse_instance():
        clues_temp = []
        for line in sys.stdin:
            value = line.split()
            if value: clues_temp.append(value)
        return Board(tuple(tuple(l) for l in clues_temp))

    def apply_logical_patterns(self):
        changed = False
        for r in range(self.N):
            for c in range(self.M):
                clue = self.clues[r][c]
                if clue == '.':
                    continue
                clue_val = int(clue)
                active = self.get_active_edges(r, c)
                unknowns = self.get_unknown_edges(r, c)
                if not unknowns:
                    continue
                if active == clue_val:
                    for t, er, ec in unknowns:
                        self.set_edge_val(t, er, ec, 0)
                    changed = True
                elif clue_val - active == len(unknowns):
                    for t, er, ec in unknowns:
                        self.set_edge_val(t, er, ec, 1)
                    changed = True

        # Regras dos vértices
        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                touching = self.get_edges_touching_vertex(vr, vc)
                active = sum(1 for t, r, c in touching if self.get_edge_val(t, r, c) == 1)
                inactive = sum(1 for t, r, c in touching if self.get_edge_val(t, r, c) == 0)
                unknowns = [e for e in touching if self.get_edge_val(*e) == -1]
                if not unknowns:
                    continue
                if active == 2 or inactive == len(touching) - 1:
                    for t, er, ec in unknowns:
                        self.set_edge_val(t, er, ec, 0)
                    changed = True
                elif active == 1 and len(unknowns) == 1:
                    for t, er, ec in unknowns:
                        self.set_edge_val(t, er, ec, 1)
                    changed = True
        return changed
    def propagate_constraints(self):
        while self.apply_logical_patterns():
            pass

    def has_premature_closed_loop(self) -> bool:
        """ A SOLUÇÃO DO TIMEOUT: Identifica qualquer ciclo na board inteira e valida-o de forma robusta. """
        active_edges = set()
        for r in range(self.N + 1):
            for c in range(self.M):
                if self.h_edges[r][c] == 1: active_edges.add(('h', r, c))
        for r in range(self.N):
            for c in range(self.M + 1):
                if self.v_edges[r][c] == 1: active_edges.add(('v', r, c))

        if not active_edges: return False

        unvisited = active_edges.copy()

        # O ciclo While assegura que verifica todas as linhas separadas no tabuleiro
        while unvisited:
            start_edge = unvisited.pop()
            visited_in_this_component = set([start_edge])
            
            t, r, c = start_edge
            v1 = (r, c)
            v2 = (r, c+1) if t == 'h' else (r+1, c)
            
            queue = [(v2, start_edge)]
            closed_loop = False

            while queue:
                curr_v, came_from = queue.pop(0)
                
                # Se batermos no ponto de início v1 por outro caminho, temos ciclo fechado
                if curr_v == v1:
                    closed_loop = True
                    break
                    
                touching = self.get_edges_touching_vertex(curr_v[0], curr_v[1])
                next_edges = [e for e in touching if self.get_edge_val(*e) == 1 and e != came_from]
                
                if next_edges:
                    next_e = next_edges[0]
                    visited_in_this_component.add(next_e)
                    unvisited.discard(next_e)
                    
                    n_v = self.get_other_vertex(next_e, curr_v)
                    queue.append((n_v, next_e))

            if closed_loop:
                # Se for um ciclo mas existirem outras linhas ativas no mapa -> Ciclo Prematuro (Falso)
                if len(visited_in_this_component) < len(active_edges):
                    return True
                # Se for o único ciclo mas deixámos números por satisfazer -> Fecho Incorreto (Falso)
                for row in range(self.N):
                    for col in range(self.M):
                        clue = self.clues[row][col]
                        if clue != '.' and self.get_active_edges(row, col) != int(clue):
                            return True
        return False

    def is_valid(self) -> bool:
        """ Poda mortes prematuras na árvore de procura CSP. """
        for r in range(self.N):
            for c in range(self.M):
                clue = self.clues[r][c]
                if clue != '.':
                    active = self.get_active_edges(r, c)
                    unknown = len(self.get_unknown_edges(r, c))
                    if active > int(clue) or (active + unknown) < int(clue):
                        return False
        
        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                touching = self.get_edges_touching_vertex(vr, vc)
                active = sum(1 for t, er, ec in touching if self.get_edge_val(t, er, ec) == 1)
                unknown = sum(1 for t, er, ec in touching if self.get_edge_val(t, er, ec) == -1)
                if active > 2: return False
                if active == 1 and unknown == 0: return False # Fio Solto Permanentemente Morto

        if self.has_premature_closed_loop():
            return False

        return True

    def check_single_loop(self) -> bool:
        if self.has_premature_closed_loop(): return False
        
        active_count = sum(1 for row in self.h_edges for val in row if val == 1) + \
                       sum(1 for row in self.v_edges for val in row if val == 1)
        return active_count > 0

    def print_solution(self):
        """ Saída Exata para o Gitlab """
        out_lines = []
        for r in range(self.N):
            row_str = []
            for c in range(self.M):
                top = max(0, self.h_edges[r][c])
                right = max(0, self.v_edges[r][c+1])
                bottom = max(0, self.h_edges[r+1][c])
                left = max(0, self.v_edges[r][c])
                row_str.append(f"{top}{right}{bottom}{left}")
            out_lines.append("\t".join(row_str))
        print("\n".join(out_lines))


class Slitherlink(Problem):
    def __init__(self, board: Board):
        board.propagate_constraints()
        super().__init__(SlitherlinkState(board))

    def actions(self, state: SlitherlinkState):
        """ Heurísticas rigorosas: Seleciona sempre a opção mais restritiva (MRV). """
        board = state.board
        if not board.is_valid():
            return []
        
        best_edge = None
        min_unknowns = 5
        
        # 1. Encontrar a Célula com MENOS arestas por descobrir (MRV)
        for r in range(board.N):
            for c in range(board.M):
                if board.clues[r][c] != '.':
                    unknowns = board.get_unknown_edges(r, c)
                    l = len(unknowns)
                    if 0 < l < min_unknowns:
                        min_unknowns = l
                        best_edge = unknowns[0]
                        if min_unknowns == 1: break
            if min_unknowns == 1: break
            
        # 2. Heurística Secundária: Tentar Estender Caminhos Já Existentes
        if not best_edge:
            for vr in range(board.N + 1):
                for vc in range(board.M + 1):
                    touching = board.get_edges_touching_vertex(vr, vc)
                    active = sum(1 for t, r, c in touching if board.get_edge_val(t, r, c) == 1)
                    if active == 1:
                        for t, r, c in touching:
                            if board.get_edge_val(t, r, c) == -1:
                                best_edge = (t, r, c)
                                break
                    if best_edge: break
                if best_edge: break

        # 3. Fallback: Qualquer aresta livre
        if not best_edge:
            for r in range(board.N + 1):
                for c in range(board.M):
                    if board.h_edges[r][c] == -1: best_edge = ('h', r, c); break
                if best_edge: break
            if not best_edge:
                for r in range(board.N):
                    for c in range(board.M + 1):
                        if board.v_edges[r][c] == -1: best_edge = ('v', r, c); break
                    if best_edge: break
                    
        # Força sempre a opção "1" (Tentar criar circuito) antes da "0" (Bloquear)
        if best_edge:
            return [(best_edge, 1), (best_edge, 0)]
            
        return []

    def result(self, state: SlitherlinkState, action):
        edge, val = action
        t, r, c = edge
        new_board = state.board.copy()
        
        new_board.set_edge_val(t, r, c, val)
        new_board.propagate_constraints() 
        
        return SlitherlinkState(new_board)

    def goal_test(self, state: SlitherlinkState):
        board = state.board
        if not board.is_valid(): 
            return False
        
        for vr in range(board.N + 1):
            for vc in range(board.M + 1):
                touching = board.get_edges_touching_vertex(vr, vc)
                active = sum(1 for t, er, ec in touching if board.get_edge_val(t, er, ec) == 1)
                if active != 0 and active != 2: return False
                    
        for r in range(board.N):
            for c in range(board.M):
                clue = board.clues[r][c]
                if clue != '.' and board.get_active_edges(r, c) != int(clue):
                    return False
                        
        return board.check_single_loop()

if __name__ == '__main__':
    board = Board.parse_instance()
    problem = Slitherlink(board)
    
    solucao_node = depth_first_tree_search(problem)
    
    if solucao_node:
        solucao_node.state.board.print_solution()