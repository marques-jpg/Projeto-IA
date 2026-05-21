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
    def __init__(self, clues, h_edges=None, v_edges=None, trail=None, marks=None):
        self.clues = clues
        self.N = len(clues)
        self.M = len(clues[0])

        if h_edges is not None:
            self.h_edges = h_edges
        else:
            self.h_edges = [[-1 for _ in range(self.M)] for _ in range(self.N + 1)]

        if v_edges is not None:
            self.v_edges = v_edges
        else:
            self.v_edges = [[-1 for _ in range(self.M + 1)] for _ in range(self.N)]

        self._cell_edges = [
            [
                (('h', r, c), ('v', r, c + 1), ('h', r + 1, c), ('v', r, c))
                for c in range(self.M)
            ]
            for r in range(self.N)
        ]
        self._vertex_edges = [
            [
                tuple(
                    edge for edge in (
                        ('h', vr, vc - 1) if vc > 0 else None,
                        ('h', vr, vc) if vc < self.M else None,
                        ('v', vr - 1, vc) if vr > 0 else None,
                        ('v', vr, vc) if vr < self.N else None,
                    )
                    if edge is not None
                )
                for vc in range(self.M + 1)
            ]
            for vr in range(self.N + 1)
        ]

        self._trail = list(trail) if trail is not None else []
        self._marks = list(marks) if marks is not None else []

    def get_cell_edges(self, row: int, col: int) -> list:
        return self._cell_edges[row][col]

    def get_edge_val(self, t: str, r: int, c: int) -> int:
        return self.h_edges[r][c] if t == 'h' else self.v_edges[r][c]

    def set_edge_val(self, t: str, r: int, c: int, val: int, track: bool = True):
        old = self.get_edge_val(t, r, c)
        if old == val:
            return
        if track:
            self._trail.append((t, r, c, old))
        if t == 'h': self.h_edges[r][c] = val
        else: self.v_edges[r][c] = val

    def assign_edge(self, t: str, r: int, c: int, val: int) -> bool:
        current = self.get_edge_val(t, r, c)
        if current == val:
            return True
        if current != -1:
            return False
        self.set_edge_val(t, r, c, val)
        return True

    def push_trail(self):
        self._marks.append(len(self._trail))

    def rollback_trail(self):
        mark = self._marks.pop()
        while len(self._trail) > mark:
            t, r, c, old = self._trail.pop()
            if t == 'h': self.h_edges[r][c] = old
            else: self.v_edges[r][c] = old

    def commit_trail(self):
        self._marks.pop()

    def get_active_edges(self, row: int, col: int) -> int:
        active = 0
        for t, r, c in self.get_cell_edges(row, col):
            if self.get_edge_val(t, r, c) == 1:
                active += 1
        return active

    def get_unknown_edges(self, row: int, col: int) -> list:
        unknowns = []
        for t, r, c in self.get_cell_edges(row, col):
            if self.get_edge_val(t, r, c) == -1:
                unknowns.append((t, r, c))
        return unknowns

    def get_edges_touching_vertex(self, vr: int, vc: int) -> list:
        return self._vertex_edges[vr][vc]

    @staticmethod
    def get_other_vertex(edge, v):
        """ Devolve o vértice oposto de uma aresta. """
        t, r, c = edge
        v1 = (r, c)
        v2 = (r, c + 1) if t == 'h' else (r + 1, c)
        return v2 if v == v1 else v1

    def copy(self):
        h_copy = [row[:] for row in self.h_edges]
        v_copy = [row[:] for row in self.v_edges]
        return Board(self.clues, h_edges=h_copy, v_edges=v_copy)

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
                active = 0
                unknowns = []
                for t, er, ec in self.get_cell_edges(r, c):
                    edge_val = self.get_edge_val(t, er, ec)
                    if edge_val == 1:
                        active += 1
                    elif edge_val == -1:
                        unknowns.append((t, er, ec))
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
                active = 0
                inactive = 0
                unknowns = []
                for t, r, c in touching:
                    edge_val = self.get_edge_val(t, r, c)
                    if edge_val == 1:
                        active += 1
                    elif edge_val == 0:
                        inactive += 1
                    else:
                        unknowns.append((t, r, c))
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

        for r in range(self.N):
            for c in range(self.M):
                clue = self.clues[r][c]
                if clue != '.':
                    active = 0
                    unknown = 0
                    for t, er, ec in self.get_cell_edges(r, c):
                        edge_val = self.get_edge_val(t, er, ec)
                        if edge_val == 1:
                            active += 1
                        elif edge_val == -1:
                            unknown += 1
                    if active > int(clue) or (active + unknown) < int(clue):
                        return None

        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                touching = self.get_edges_touching_vertex(vr, vc)
                active = 0
                unknown = 0
                for t, r, c in touching:
                    edge_val = self.get_edge_val(t, r, c)
                    if edge_val == 1:
                        active += 1
                    elif edge_val == -1:
                        unknown += 1
                if active > 2:
                    return None
                if active == 1 and unknown == 0:
                    return None

        return changed
    def propagate_constraints(self):
        while True:
            changed = self.apply_logical_patterns()
            if changed is None:
                return False
            if not changed:
                return True

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
                    active = 0
                    unknown = 0
                    for t, er, ec in self.get_cell_edges(r, c):
                        edge_val = self.get_edge_val(t, er, ec)
                        if edge_val == 1:
                            active += 1
                        elif edge_val == -1:
                            unknown += 1
                    if active > int(clue) or (active + unknown) < int(clue):
                        return False
        
        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                touching = self.get_edges_touching_vertex(vr, vc)
                active = 0
                unknown = 0
                for t, er, ec in touching:
                    edge_val = self.get_edge_val(t, er, ec)
                    if edge_val == 1:
                        active += 1
                    elif edge_val == -1:
                        unknown += 1
                if active > 2: return False
                if active == 1 and unknown == 0: return False # Fio Solto Permanentemente Morto
                if active == 1 and unknown == 1:
                    open_edge = None
                    for edge in touching:
                        if self.get_edge_val(*edge) == -1:
                            open_edge = edge
                            break
                    if open_edge is None:
                        return False
                    other_vr, other_vc = self.get_other_vertex(open_edge, (vr, vc))
                    other_touching = self.get_edges_touching_vertex(other_vr, other_vc)
                    other_active = 0
                    other_unknown = 0
                    for t, er, ec in other_touching:
                        edge_val = self.get_edge_val(t, er, ec)
                        if edge_val == 1:
                            other_active += 1
                        elif edge_val == -1:
                            other_unknown += 1
                    if other_active == 2 and other_unknown == 0:
                        return False

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

    def _trail_dfs(self, board: Board):
        state = SlitherlinkState(board)
        if self.goal_test(state):
            return state

        actions = self.actions(state)
        if not actions:
            return None

        for edge, val in actions:
            t, r, c = edge
            if board.get_edge_val(t, r, c) not in (-1, val):
                continue

            board.push_trail()
            board.set_edge_val(t, r, c, val, track=True)
            ok = board.propagate_constraints()

            if ok:
                result_state = self._trail_dfs(board)
                if result_state is not None:
                    board.commit_trail()
                    return result_state

            board.rollback_trail()

        return None

    def custom_depth_first_tree_search(self):
        solved_state = self._trail_dfs(self.initial.board)
        if solved_state is None:
            return None
        return Node(solved_state)

    def actions(self, state: SlitherlinkState):
        board = state.board
        if not board.is_valid():
            return []

        def edge_cells(edge):
            t, r, c = edge
            cells = []
            if t == 'h':
                if r > 0:
                    cells.append((r - 1, c))
                if r < board.N:
                    cells.append((r, c))
            else:
                if c > 0:
                    cells.append((r, c - 1))
                if c < board.M:
                    cells.append((r, c))
            return cells

        def edge_vertices(edge):
            t, r, c = edge
            if t == 'h':
                return [(r, c), (r, c + 1)]
            return [(r, c), (r + 1, c)]

        def edge_score(edge):
            score = 0

            for cr, cc in edge_cells(edge):
                clue = board.clues[cr][cc]
                if clue == '.':
                    continue

                clue_val = int(clue)
                active = board.get_active_edges(cr, cc)
                unknown = len(board.get_unknown_edges(cr, cc))
                remaining = clue_val - active

                # Prefer tighter numbered cells and cells close to completion.
                score += 20 + (4 - unknown) * 4
                score += max(0, 4 - abs(clue_val - active))
                if remaining == unknown:
                    score += 12
                if remaining == 1:
                    score += 10

            for vr, vc in edge_vertices(edge):
                touching = board.get_edges_touching_vertex(vr, vc)
                active = sum(1 for t, er, ec in touching if board.get_edge_val(t, er, ec) == 1)
                unknown = sum(1 for t, er, ec in touching if board.get_edge_val(t, er, ec) == -1)

                # Prefer extending open endpoints, especially near-dead-end corridors.
                if active == 1:
                    score += 18
                    score += max(0, 4 - unknown) * 3
                    if unknown == 1:
                        score += 12
                elif active == 0 and unknown <= 2:
                    score += 2 + (2 - unknown)

            return score

        candidates = []
        for r in range(board.N + 1):
            for c in range(board.M):
                if board.h_edges[r][c] == -1:
                    edge = ('h', r, c)
                    candidates.append((edge_score(edge), edge))
        for r in range(board.N):
            for c in range(board.M + 1):
                if board.v_edges[r][c] == -1:
                    edge = ('v', r, c)
                    candidates.append((edge_score(edge), edge))

        if not candidates:
            return []

        best_edge = max(candidates, key=lambda item: (item[0], item[1]))[1]
        return [(best_edge, 1), (best_edge, 0)]

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