# Calculate metrics about a given chess position
# in an attempt learn something about the position.

from collections import defaultdict
import math
import random

from lczero.backends import Weights, Backend, GameState


w = Weights()
b = Backend(weights=w)


def get_entropy(probs):
    """Calculates information theoretical entropy"""
    norm = sum(probs)
    try:
        return -sum(math.log2(p) * p for p in probs) / norm + math.log2(norm)
    except Exception:
        print(probs)
        raise


def evaluate(backend, game_state):
    output, = backend.evaluate(game_state.as_input(backend))
    moves = dict(zip(game_state.moves(), output.p_softmax(*game_state.policy_indices())))
    return output.q(), moves


def get_move(moves):
    #moves = {k: v for k, v in moves.items() if v >= 0.1}
    return random.choices(list(moves.keys()), weights=moves.values(), k=1)[0]


class Stats():
    def __init__(self):
        self.eval = 0.
        self.trend = 0.
        self.entropy = 0.
        self.count = 0
        self.moves = defaultdict(float)

    def update(self, prev_eval, cur_eval, moves):
        self.eval += cur_eval
        self.trend += cur_eval - prev_eval
        self.entropy += get_entropy(moves.values())
        self.count += 1
        for m, p in moves.items():
            self.moves[m] += p

    def __repr__(self) -> str:
        moves = sorted(self.moves, key=lambda x: self.moves[x], reverse=True)[:6]
        return ("Eval mean: {:.3f}\n".format(self.eval / self.count) +
                "Eval trend: {:.3f}\n".format(self.trend / self.count) +
                "Move entropy: {:.2f}\n".format(self.entropy / self.count) +
                "Plan entropy: {:.2f}\n".format(get_entropy(self.moves.values())) +
                "Main plans: {}".format(moves))


def stats_rollouts(fen=None, moves=None, rollouts=1, depth=1):
    if moves is None:
        moves = []
    g = GameState(fen, moves)
    root_eval, root_moves = evaluate(b, g)

    stats = [Stats(), Stats()]
    # initialize stats with root moves
    stats[0].update(root_eval, root_eval, {k: rollouts * v for k, v in root_moves.items()})

    for i in range(rollouts):
        move_stack = moves.copy()
        prev_eval = -root_eval
        move_stack.append(get_move(root_moves))

        for j in range(1, depth + 1):
            g = GameState(fen=fen, moves=move_stack)
            if not g.moves():
                break
            cur_eval, cur_moves = evaluate(b, g)
            stats[j % 2].update(prev_eval, cur_eval, cur_moves)
            move_stack.append(get_move(cur_moves))
            prev_eval = -cur_eval

    return stats


if __name__ == '__main__':
    for i, moves in enumerate(([], ['e2e4'], ['d2d4'], ['c2c4'])):
        print("\nPosition {}:\nOpening moves: {}".format(i + 1, " ".join(moves)))
        for j, stats in enumerate(stats_rollouts(None, moves, 100, 10)):
            print("Perspective: Side{} to move".format("" if j == 0 else " not"))
            print(stats)
