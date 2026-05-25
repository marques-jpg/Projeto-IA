#!/usr/bin/env python3
# slitherlink.py: Implementação do projeto de Inteligência Artificial 2025/2026.
# Grupo 39:
# 113868 Guilherme Marques
# 110126 António Correia

import sys
from collections import deque
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
        self.clue_vals = [
            [(-1 if clues[r][c] == '.' else int(clues[r][c])) for c in range(self.M)]
            for r in range(self.N)
        ]

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
        self._valid_cache = None
        self._loop_cache = None
        self._cell_active = [[0 for _ in range(self.M)] for _ in range(self.N)]
        self._cell_unknown = [[0 for _ in range(self.M)] for _ in range(self.N)]
        self._vertex_active = [[0 for _ in range(self.M + 1)] for _ in range(self.N + 1)]
        self._vertex_unknown = [[0 for _ in range(self.M + 1)] for _ in range(self.N + 1)]
        self._total_active_edges = 0
        self._total_unknown_edges = 0
        self._init_counts()

    def _init_counts(self):
        for r in range(self.N + 1):
            for c in range(self.M):
                val = self.h_edges[r][c]
                if val == 1:
                    self._total_active_edges += 1
                    self._vertex_active[r][c] += 1
                    self._vertex_active[r][c + 1] += 1
                elif val == -1:
                    self._total_unknown_edges += 1
                    self._vertex_unknown[r][c] += 1
                    self._vertex_unknown[r][c + 1] += 1
                if r > 0:
                    if val == 1:
                        self._cell_active[r - 1][c] += 1
                    elif val == -1:
                        self._cell_unknown[r - 1][c] += 1
                if r < self.N:
                    if val == 1:
                        self._cell_active[r][c] += 1
                    elif val == -1:
                        self._cell_unknown[r][c] += 1

        for r in range(self.N):
            for c in range(self.M + 1):
                val = self.v_edges[r][c]
                if val == 1:
                    self._total_active_edges += 1
                    self._vertex_active[r][c] += 1
                    self._vertex_active[r + 1][c] += 1
                elif val == -1:
                    self._total_unknown_edges += 1
                    self._vertex_unknown[r][c] += 1
                    self._vertex_unknown[r + 1][c] += 1
                if c > 0:
                    if val == 1:
                        self._cell_active[r][c - 1] += 1
                    elif val == -1:
                        self._cell_unknown[r][c - 1] += 1
                if c < self.M:
                    if val == 1:
                        self._cell_active[r][c] += 1
                    elif val == -1:
                        self._cell_unknown[r][c] += 1

    def _update_counts_for_edge(self, t: str, r: int, c: int, old: int, new: int):
        if old == new:
            return

        def apply_delta(delta: int, val: int):
            if val == 1:
                return delta, 0
            if val == -1:
                return 0, delta
            return 0, 0

        active_delta, unknown_delta = apply_delta(-1, old)
        active_add, unknown_add = apply_delta(1, new)
        active_delta += active_add
        unknown_delta += unknown_add
        if old == 1:
            self._total_active_edges -= 1
        elif old == -1:
            self._total_unknown_edges -= 1
        if new == 1:
            self._total_active_edges += 1
        elif new == -1:
            self._total_unknown_edges += 1

        if t == 'h':
            self._vertex_active[r][c] += active_delta
            self._vertex_active[r][c + 1] += active_delta
            self._vertex_unknown[r][c] += unknown_delta
            self._vertex_unknown[r][c + 1] += unknown_delta
            if r > 0:
                self._cell_active[r - 1][c] += active_delta
                self._cell_unknown[r - 1][c] += unknown_delta
            if r < self.N:
                self._cell_active[r][c] += active_delta
                self._cell_unknown[r][c] += unknown_delta
        else:
            self._vertex_active[r][c] += active_delta
            self._vertex_active[r + 1][c] += active_delta
            self._vertex_unknown[r][c] += unknown_delta
            self._vertex_unknown[r + 1][c] += unknown_delta
            if c > 0:
                self._cell_active[r][c - 1] += active_delta
                self._cell_unknown[r][c - 1] += unknown_delta
            if c < self.M:
                self._cell_active[r][c] += active_delta
                self._cell_unknown[r][c] += unknown_delta

    def get_cell_edges(self, row: int, col: int) -> list:
        return self._cell_edges[row][col]

    def get_edge_val(self, t: str, r: int, c: int) -> int:
        return self.h_edges[r][c] if t == 'h' else self.v_edges[r][c]

    def set_edge_val(self, t: str, r: int, c: int, val: int, track: bool = True):
        old = self.get_edge_val(t, r, c)
        if old == val:
            return
        self._valid_cache = None
        self._loop_cache = None
        self._update_counts_for_edge(t, r, c, old, val)
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
            current = self.get_edge_val(t, r, c)
            self._update_counts_for_edge(t, r, c, current, old)
            if t == 'h': self.h_edges[r][c] = old
            else: self.v_edges[r][c] = old
        self._valid_cache = None
        self._loop_cache = None

    def commit_trail(self):
        self._marks.pop()

    def get_active_edges(self, row: int, col: int) -> int:
        return self._cell_active[row][col]

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
        h_edges = self.h_edges
        v_edges = self.v_edges
        cell_edges = self._cell_edges
        vertex_edges = self._vertex_edges
        cell_active = self._cell_active
        cell_unknown = self._cell_unknown
        vertex_active = self._vertex_active
        vertex_unknown = self._vertex_unknown
        set_edge_val = self.set_edge_val
        for r in range(self.N):
            for c in range(self.M):
                clue_val = self.clue_vals[r][c]
                if clue_val < 0:
                    continue
                active = cell_active[r][c]
                unknowns = []
                for t, er, ec in cell_edges[r][c]:
                    edge_val = h_edges[er][ec] if t == 'h' else v_edges[er][ec]
                    if edge_val == 1:
                        continue
                    elif edge_val == -1:
                        unknowns.append((t, er, ec))
                if not unknowns:
                    continue
                if active == clue_val:
                    for t, er, ec in unknowns:
                        set_edge_val(t, er, ec, 0)
                    changed = True
                elif clue_val - active == len(unknowns):
                    for t, er, ec in unknowns:
                        set_edge_val(t, er, ec, 1)
                    changed = True

        # Regras dos vértices
        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                touching = vertex_edges[vr][vc]
                active = vertex_active[vr][vc]
                inactive = len(touching) - vertex_unknown[vr][vc] - active
                unknowns = []
                for t, r, c in touching:
                    edge_val = h_edges[r][c] if t == 'h' else v_edges[r][c]
                    if edge_val == -1:
                        unknowns.append((t, r, c))
                if not unknowns:
                    continue
                if active == 2 or inactive == len(touching) - 1:
                    for t, er, ec in unknowns:
                        set_edge_val(t, er, ec, 0)
                    changed = True
                elif active == 1 and len(unknowns) == 1:
                    for t, er, ec in unknowns:
                        set_edge_val(t, er, ec, 1)
                    changed = True

        for r in range(self.N):
            for c in range(self.M):
                clue_val = self.clue_vals[r][c]
                if clue_val >= 0:
                    active = cell_active[r][c]
                    unknown = cell_unknown[r][c]
                    if active > clue_val or (active + unknown) < clue_val:
                        return None

        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                active = vertex_active[vr][vc]
                unknown = vertex_unknown[vr][vc]
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
        if self._loop_cache is not None:
            return self._loop_cache
        """ A SOLUÇÃO DO TIMEOUT: Identifica qualquer ciclo na board inteira e valida-o de forma robusta. """
        active_edges = set()
        for r in range(self.N + 1):
            for c in range(self.M):
                if self.h_edges[r][c] == 1: active_edges.add(('h', r, c))
        for r in range(self.N):
            for c in range(self.M + 1):
                if self.v_edges[r][c] == 1: active_edges.add(('v', r, c))

        if not active_edges:
            self._loop_cache = False
            return False

        unvisited = active_edges.copy()

        # O ciclo While assegura que verifica todas as linhas separadas no tabuleiro
        while unvisited:
            start_edge = unvisited.pop()
            visited_in_this_component = set([start_edge])
            
            t, r, c = start_edge
            v1 = (r, c)
            v2 = (r, c+1) if t == 'h' else (r+1, c)
            
            queue = deque([(v2, start_edge)])
            closed_loop = False

            while queue:
                curr_v, came_from = queue.pop()
                
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
                    self._loop_cache = True
                    return True
                # Se for o único ciclo mas deixámos números por satisfazer -> Fecho Incorreto (Falso)
                for row in range(self.N):
                    for col in range(self.M):
                        clue_val = self.clue_vals[row][col]
                        if clue_val >= 0 and self.get_active_edges(row, col) != clue_val:
                            self._loop_cache = True
                            return True
        self._loop_cache = False
        return False

    def is_valid(self) -> bool:
        if self._valid_cache is not None:
            return self._valid_cache
        """ Poda mortes prematuras na árvore de procura CSP. """
        h_edges = self.h_edges
        v_edges = self.v_edges
        cell_edges = self._cell_edges
        vertex_edges = self._vertex_edges
        cell_active = self._cell_active
        cell_unknown = self._cell_unknown
        vertex_active = self._vertex_active
        vertex_unknown = self._vertex_unknown
        for r in range(self.N):
            for c in range(self.M):
                clue_val = self.clue_vals[r][c]
                if clue_val >= 0:
                    active = cell_active[r][c]
                    unknown = cell_unknown[r][c]
                    if active > clue_val or (active + unknown) < clue_val:
                        self._valid_cache = False
                        return False
        
        for vr in range(self.N + 1):
            for vc in range(self.M + 1):
                touching = vertex_edges[vr][vc]
                active = vertex_active[vr][vc]
                unknown = vertex_unknown[vr][vc]
                if active > 2:
                    self._valid_cache = False
                    return False
                if active == 1 and unknown == 0:
                    self._valid_cache = False
                    return False # Fio Solto Permanentemente Morto
                if active == 1 and unknown == 1:
                    open_edge = None
                    for edge in touching:
                        if self.get_edge_val(*edge) == -1:
                            open_edge = edge
                            break
                    if open_edge is None:
                        self._valid_cache = False
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
                        self._valid_cache = False
                        return False

        if self.has_premature_closed_loop():
            self._valid_cache = False
            return False

        self._valid_cache = True
        return True

    def check_single_loop(self, skip_premature_check: bool = False) -> bool:
        if not skip_premature_check and self.has_premature_closed_loop(): return False
        return self._total_active_edges > 0

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

        cell_active = board._cell_active
        cell_unknown = board._cell_unknown
        vertex_active = board._vertex_active
        vertex_unknown = board._vertex_unknown

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
                clue_val = board.clue_vals[cr][cc]
                if clue_val < 0:
                    continue
                active = cell_active[cr][cc]
                unknown = cell_unknown[cr][cc]
                remaining = clue_val - active

                # Prefer tighter numbered cells and cells close to completion.
                score += 20 + (4 - unknown) * 4
                score += max(0, 4 - abs(clue_val - active))
                if remaining == unknown:
                    score += 12
                if remaining == 1:
                    score += 10

            for vr, vc in edge_vertices(edge):
                active = vertex_active[vr][vc]
                unknown = vertex_unknown[vr][vc]

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

        if board._total_unknown_edges > 0:
            return False

        for vr in range(board.N + 1):
            for vc in range(board.M + 1):
                active = board._vertex_active[vr][vc]
                if active != 0 and active != 2:
                    return False
                    
        for r in range(board.N):
            for c in range(board.M):
                clue_val = board.clue_vals[r][c]
                if clue_val >= 0 and board._cell_active[r][c] != clue_val:
                    return False
                        
        return board.check_single_loop(skip_premature_check=True)

if __name__ == '__main__':
    board = Board.parse_instance()
    problem = Slitherlink(board)
    
    solucao_node = depth_first_tree_search(problem)
    
    if solucao_node:
        solucao_node.state.board.print_solution()