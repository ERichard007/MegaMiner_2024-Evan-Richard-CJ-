# This is where you build your AI for the Magomachy game.

from typing import List
from joueur.base_ai import BaseAI
import random

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>

class AI(BaseAI):
    """ The AI you add and improve code inside to play Magomachy. """

    @property
    def game(self) -> 'games.magomachy.game.Game':
        """games.magomachy.game.Game: The reference to the Game instance this AI is playing.
        """
        return self._game # don't directly touch this "private" variable pls

    @property
    def player(self) -> 'games.magomachy.player.Player':
        """games.magomachy.player.Player: The reference to the Player this AI controls in the Game.
        """
        return self._player # don't directly touch this "private" variable pls

    def get_name(self) -> str:
        """This is the name you send to the server so your AI will control the player named this string.

        Returns:
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "Magomachy Python Player" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self) -> None:
        """This is called once the game starts and your AI knows its player and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your start logic
        self.player.choose_wizard("map")
        # <<-- /Creer-Merge: start -->>

    def game_updated(self) -> None:
        """This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your game updated logic
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won: bool, reason: str) -> None:
        """This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why your AI won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>
    def action(self, wizard: 'games.magomachy.wizard.Wizard') -> int:
        """This is called whenever your wizard selects an action.

        Args:
            wizard (games.magomachy.wizard.Wizard): Wizard performs action.

        Returns:
            int: Three of the choices a Wizard can make as an action.
        """
        # <<-- Creer-Merge: Action -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for Action
        return -1
        # <<-- /Creer-Merge: Action -->>
    def move(self, wizard: 'games.magomachy.wizard.Wizard') -> int:
        """This is called whenever your wizard makes a move.

        Args:
            wizard (games.magomachy.wizard.Wizard): Wizard moves.

        Returns:
            int: Eight cardinal directions.
        """
        # <<-- Creer-Merge: Move -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for Move
        return -1
        # <<-- /Creer-Merge: Move -->>
    def run_turn(self) -> bool:

        self.turn_counter += 1
        self.record_opponent_move()

        def evaluate_state(wizard, opponent):
            score = wizard.health - opponent.health
            score += wizard.aether - opponent.aether

            if wizard.aether <= 0:
                return float('-inf')
            if opponent.aether <= 0:
                return float('inf')

            key_tiles = [tile for tile in self.game.tiles if tile.has_potion or tile.has_rune]
            rune_proximity_bonus = 0

            for tile in self.game.tiles:
                if tile.has_rune:
                    distance_to_rune = abs(wizard.tile.x - tile.x) + abs(wizard.tile.y - tile.y)
                    if distance_to_rune == 0:
                        rune_proximity_bonus += 10
                    elif distance_to_rune == 1:
                        rune_proximity_bonus += 5
                    elif distance_to_rune <= 2:
                        rune_proximity_bonus += 2

            score += rune_proximity_bonus

            if wizard.tile in key_tiles:
                score += 5
            if opponent.tile in key_tiles:
                score -= 5

            return score

        def calculate_damage(base_damage, attacker_attack, defender_defense):
            bonus = max(0, (attacker_attack - defender_defense) // 2)
            return base_damage + bonus

        def analyze_opponent_patterns():
            move_counts = {}
            for move in self.opponent_move_history:
                move_key = (move[0], tuple(move[1:]))
                if move_key not in move_counts:
                    move_counts[move_key] = 0
                move_counts[move_key] += 1
            most_common_moves = sorted(move_counts.items(), key=lambda x: x[1], reverse=True)
            return [move[0] for move in most_common_moves]

        def should_prune_move(move, wizard, opponent):
            action, *args = move
            if action == "move":
                tile = args[0]
                if not tile.is_pathable():
                    return True
                if tile.has_rune and tile == opponent.tile:
                    return False
            elif action == "cast":
                spell, target_tile = args
                if spell == "Teleport Rune" and target_tile == opponent.tile:
                    return False
                if spell.aether_cost > wizard.aether:
                    return True
            return False

        def find_best_moves(wizard, opponent, depth, maximizing_player, alpha=float('-inf'), beta=float('inf')):
            if depth == 0 or wizard.health <= 0 or opponent.health <= 0 or wizard.aether <= 0 or opponent.aether <= 0:
                return evaluate_state(wizard, opponent), None, None

            best_move = None
            best_secondary_move = None
            if maximizing_player:
                max_eval = float('-inf')
                for primary_move in sorted(get_possible_moves(wizard), key=move_priority, reverse=True):
                    if should_prune_move(primary_move, wizard, opponent):
                        continue
                    eval_after_primary = estimate_move_result(primary_move, wizard, opponent, maximizing_player)
                    if eval_after_primary == float('-inf'):
                        continue
                    for secondary_move in sorted(get_possible_moves(wizard), key=move_priority, reverse=True):
                        if should_prune_move(secondary_move, wizard, opponent):
                            continue
                        eval = estimate_move_result(secondary_move, wizard, opponent, maximizing_player) + eval_after_primary
                        if eval == float('-inf'):
                            continue
                        if eval > max_eval:
                            max_eval = eval
                            best_move = primary_move
                            best_secondary_move = secondary_move
                        alpha = max(alpha, eval)
                        if beta <= alpha:
                            break
                return max_eval, best_move, best_secondary_move
            else:
                min_eval = float('inf')
                for primary_move in sorted(get_possible_moves(opponent), key=move_priority, reverse=True):
                    if should_prune_move(primary_move, opponent, wizard):
                        continue
                    eval_after_primary = estimate_move_result(primary_move, opponent, wizard, maximizing_player)
                    if eval_after_primary == float('inf'):
                        continue
                    for secondary_move in sorted(get_possible_moves(opponent), key=move_priority, reverse=True):
                        if should_prune_move(secondary_move, opponent, wizard):
                            continue
                        eval = estimate_move_result(secondary_move, opponent, wizard, maximizing_player) + eval_after_primary
                        if eval == float('inf'):
                            continue
                        if eval < min_eval:
                            min_eval = eval
                            best_move = primary_move
                            best_secondary_move = secondary_move
                        beta = min(beta, eval)
                        if beta <= alpha:
                            break
                return min_eval, best_move, best_secondary_move

        def estimate_move_result(move, wizard, opponent, maximizing_player):
            action, *args = move
            if action == "move":
                return evaluate_state(wizard, opponent)
            elif action == "cast":
                spell, target_tile = args
                potential_damage = 0
                if spell == "Explosion Rune":
                    potential_damage = calculate_damage(4, wizard.attack, opponent.defense)
                elif spell == "Charge Rune":
                    potential_damage = calculate_damage(5, wizard.attack, opponent.defense)
                elif spell == "Fireball":
                    potential_damage = calculate_damage(3, wizard.attack, opponent.defense)
                elif spell == "Force Push":
                    potential_damage = calculate_damage(2, wizard.attack, opponent.defense)
                elif spell == "Heal":
                    potential_damage = -5
                elif spell == "Teleport Rune":
                    if target_tile == opponent.tile:
                        return float('inf')
                return evaluate_state(wizard, opponent) + potential_damage - spell.aether_cost
            elif action == "do_nothing":
                return evaluate_state(wizard, opponent)
            elif action == "pick_potion":
                return evaluate_state(wizard, opponent) + 10

        def get_possible_moves(wizard):
            moves = [("do_nothing",)]
            for tile in wizard.tile.get_neighbors():
                if tile.is_pathable():
                    moves.append(("move", tile))
            for spell in wizard.spells:
                for tile in self.game.tiles:
                    if wizard.can_cast(spell, tile):
                        moves.append(("cast", spell, tile))
            for potion in self.game.potions:
                if wizard.tile == potion.tile:
                    moves.append(("pick_potion", potion))
            return moves

        def move_priority(move):
            action, *args = move
            if action == "cast":
                spell, _ = args
                if spell == "Teleport Rune" and opponent_wizard.tile in [tile for tile in self.game.tiles if tile.has_teleport_rune]:
                    return 1000
                elif spell == "Explosion Rune":
                    return 100
                elif spell == "Charge Rune":
                    return 90
                elif spell == "Fireball":
                    return 80
                elif spell == "Heal":
                    return 50
            elif action == "move":
                return 10
            elif action == "pick_potion":
                return 20
            return 0

        def record_opponent_move():
            if self.turn_counter > 1:
                opponent = self.player.opponent.wizard
                if opponent and opponent.last_move:
                    self.opponent_move_history.append(opponent.last_move)

        def get_best_rune_placement(rune_type):
            scores = {}
            for tile in self.game.tiles:
                if tile.is_pathable():
                    score = 0
                    choke_points = [tile for tile in self.game.tiles if tile.is_choke_point]
                    if tile.has_potion or tile in choke_points:
                        score += 5
                    if tile == opponent_wizard.tile and rune_type == "Teleport":
                        score += 1000
                    scores[tile] = score
            return max(scores, key=scores.get)

        my_wizard = self.player.wizard
        opponent_wizard = self.player.opponent.wizard

        if not my_wizard:
            if self.player.turn_number == 1:
                self.player.choose_wizard("strategic")
            elif self.player.turn_number == 2:
                self.player.choose_wizard("aggressive")
            return True

        depth = 3 if my_wizard.health > 10 else 5

        state_evaluation = evaluate_state(my_wizard, opponent_wizard)
        if state_evaluation > 0:
            self.no_advantage_counter = 0
            self.advantage_turns += 1
        else:
            self.no_advantage_counter += 1

        if self.no_advantage_counter >= 5:
            opponent_patterns = analyze_opponent_patterns()

        _, best_move, best_secondary_move = find_best_moves(my_wizard, opponent_wizard, depth, True)

        if best_move:
            action, *args = best_move
            if action == "move":
                my_wizard.move(args[0])
            elif action == "cast":
                my_wizard.cast(args[0], args[1])
            elif action == "pick_potion":
                my_wizard.pick_potion(args[0])

        if best_secondary_move:
            action, *args = best_secondary_move
            if action == "move":
                my_wizard.move(args[0])
            elif action == "cast":
                my_wizard.cast(args[0], args[1])
            elif action == "pick_potion":
                my_wizard.pick_potion(args[0])

        return True
        # <<-- /Creer-Merge: runTurn -->>

    def find_path(self, start: 'games.magomachy.tile.Tile', goal: 'games.magomachy.tile.Tile') -> List['games.magomachy.tile.Tile']:
        """A very basic path finding algorithm (Breadth First Search) that when given a starting Tile, will return a valid path to the goal Tile.

        Args:
            start (games.magomachy.tile.Tile): The starting Tile to find a path from.
            goal (games.magomachy.tile.Tile): The goal (destination) Tile to find a path to.

        Returns:
            list[games.magomachy.tile.Tile]: A list of Tiles representing the path, the the first element being a valid adjacent Tile to the start, and the last element being the goal.
        """

        if start == goal:
            # no need to make a path to here...
            return []

        # queue of the tiles that will have their neighbors searched for 'goal'
        fringe = []

        # How we got to each tile that went into the fringe.
        came_from = {}

        # Enqueue start as the first tile to have its neighbors searched.
        fringe.append(start)

        # keep exploring neighbors of neighbors... until there are no more.
        while len(fringe) > 0:
            # the tile we are currently exploring.
            inspect = fringe.pop(0)

            # cycle through the tile's neighbors.
            for neighbor in inspect.get_neighbors():
                # if we found the goal, we have the path!
                if neighbor == goal:
                    # Follow the path backward to the start from the goal and
                    # # return it.
                    path = [goal]

                    # Starting at the tile we are currently at, insert them
                    # retracing our steps till we get to the starting tile
                    while inspect != start:
                        path.insert(0, inspect)
                        inspect = came_from[inspect.id]
                    return path
                # else we did not find the goal, so enqueue this tile's
                # neighbors to be inspected

                # if the tile exists, has not been explored or added to the
                # fringe yet, and it is pathable
                if neighbor and neighbor.id not in came_from and (
                    neighbor.is_pathable()
                ):
                    # add it to the tiles to be explored and add where it came
                    # from for path reconstruction.
                    fringe.append(neighbor)
                    came_from[neighbor.id] = inspect

        # if you're here, that means that there was not a path to get to where
        # you want to go; in that case, we'll just return an empty path.
        return []

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    # <<-- /Creer-Merge: functions -->>
