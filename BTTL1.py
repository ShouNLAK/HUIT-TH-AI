import time
import random
from heapq import heappush, heappop

def get_target_pos_1d(final_state, n):
    return {val: (i // n, i % n) for i, val in enumerate(final_state)}

def manhattan_1d(state, target_pos, n):
    dist = 0
    for i, val in enumerate(state):
        if val != 0:
            cx, cy = i // n, i % n
            tx, ty = target_pos[val]
            dist += abs(cx - tx) + abs(cy - ty)
    return dist

def is_solvable(state, n):
    inv_count = sum(1 for i in range(len(state)) for j in range(i + 1, len(state)) 
                    if state[i] != 0 and state[j] != 0 and state[i] > state[j])
    if n % 2 != 0:
        return inv_count % 2 == 0
    else:
        blank_row_from_bottom = n - (state.index(0) // n)
        return (inv_count % 2 != 0) if (blank_row_from_bottom % 2 == 0) else (inv_count % 2 == 0)

def make_solvable_state(n, final_state):
    state = list(final_state)
    random.shuffle(state)
    if not is_solvable(state, n):
        i1, i2 = [i for i, v in enumerate(state) if v != 0][:2]
        state[i1], state[i2] = state[i2], state[i1]
    return state

def print_grid(state, n):
    for i in range(0, n * n, n):
        row = state[i:i+n]
        print(" | ".join(f"{x:2}" if x != 0 else "  " for x in row))
    print("-" * (n * 5))

def solve_npuzzle(n):
    final_state = list(range(1, n * n)) + [0]
    final_tuple = tuple(final_state)
    
    initial_state = make_solvable_state(n, final_state)
    initial_tuple = tuple(initial_state)
    
    print("\n--- Initial State ---")
    print_grid(initial_state, n)
    print("Solving...\n")
    
    start_time = time.time()
    target_pos = get_target_pos_1d(final_tuple, n)
    empty_idx = initial_state.index(0)
    h_initial = manhattan_1d(initial_tuple, target_pos, n)
    
    pq = [(h_initial, 0, empty_idx, initial_tuple)]
    g_scores = {initial_tuple: 0}
    came_from = {initial_tuple: None}

    while pq:
        f, g, current_empty, current_state = heappop(pq)

        if current_state == final_tuple:
            path = []
            curr = current_state
            while curr:
                path.append(curr)
                curr = came_from[curr]
            path = path[::-1]
            
            print(f"Solved in {time.time() - start_time:.4f}s")
            print(f"Moves Required: {g} | States Explored: {len(g_scores)}\n")
            
            show = input("Display steps? (y/n): ").strip().lower()
            if show == 'y':
                for step, p_state in enumerate(path):
                    print(f"Step {step}:")
                    print_grid(p_state, n)
            return

        if g > g_scores.get(current_state, float('inf')):
            continue

        row, col = current_empty // n, current_empty % n
        neighbors = []
        if row > 0: neighbors.append(current_empty - n)
        if row < n - 1: neighbors.append(current_empty + n)
        if col > 0: neighbors.append(current_empty - 1)
        if col < n - 1: neighbors.append(current_empty + 1)

        for n_idx in neighbors:
            new_state = list(current_state)
            new_state[current_empty], new_state[n_idx] = new_state[n_idx], new_state[current_empty]
            new_state_tuple = tuple(new_state)
            
            tentative_g = g + 1
            if tentative_g < g_scores.get(new_state_tuple, float('inf')):
                g_scores[new_state_tuple] = tentative_g
                h = manhattan_1d(new_state_tuple, target_pos, n)
                came_from[new_state_tuple] = current_state
                heappush(pq, (tentative_g + h, tentative_g, n_idx, new_state_tuple))

if __name__ == "__main__":
    while True:
        try:
            n = int(input("Enter grid size n (2-4 recommended): "))
            if n > 0: break
        except ValueError:
            pass
    solve_npuzzle(n)