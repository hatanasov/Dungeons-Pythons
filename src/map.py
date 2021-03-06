from src.cells.wall import Wall
from src.cells.empty_cell import EmptyCell
from src.cells.spawn import Spawn
from src.cells.gateway import Gateway
from src.treasure import Treasure
from src.hero import Hero
from src.enemy import Enemy

from src.mixins.walkable import WalkableMixin
from src.decorators import accepts, validate_move

from os import linesep
from operator import attrgetter


class Map:
    def _cell_factory(self, sym, row, col):
        cls = self.__class_lookup.get(sym)

        if cls is None:
            raise ValueError(f'Unrecognized symbol: {sym}')

        obj = cls(row=row, col=col)

        if sym == Treasure.sym:
            treasure = Treasure(row=row, col=col)
            obj.trigger_enter_event(treasure)
            self.treasures.add(treasure)
        elif sym == Enemy.sym:
            enemy = Enemy(row=row, col=col, health=None, mana=None, damage=None)
            obj.trigger_enter_event(enemy)
            self.enemies.add(enemy)
        elif sym == Spawn.sym:
            self.spawnpoints.append(obj)

        return obj

    def __init__(self, lines):
        self.__class_lookup = {
                '.': EmptyCell,
                'T': EmptyCell,
                'E': EmptyCell,
                '#': Wall,
                'S': Spawn,
                'G': Gateway,
                }

        self.spawnpoints = []
        self.hero = None
        self.treasures = set()
        self.enemies = set()

        len_rows = len(lines)

        self.grid = [
            [
                self._cell_factory(sym, row, col)
                for col, sym in zip(range(len(lines[row])), line)
            ] for row, line in zip(range(len_rows), lines)
        ]

        self.spawnpoints = iter(self.spawnpoints)

    @classmethod
    def load(cls, fname):
        with open(fname) as f:
            return cls([x.strip() for x in f])

    def __str__(self):
        return linesep.join([
            ''.join(map(attrgetter('sym'), row)) for row in self.grid
        ])

    def print_map(self):
        print(self)

    @accepts(Hero)
    def spawn(self, hero):
        self.hero = hero

        try:
            spawn = next(self.spawnpoints)
            row, col = spawn.row, spawn.col
            self.grid[row][col] = new_cell = EmptyCell(row=row, col=col)
            new_cell.trigger_enter_event(self.hero)
            self.hero.row, self.hero.col = row, col

            return True
        except StopIteration:
            return False

    @validate_move
    def move_hero(self, target_row, target_col):
        from_row, from_col = self.hero.row, self.hero.col

        self.hero.row, self.hero.col = target_row, target_col
        self.grid[from_row][from_col].trigger_leave_event()
        self.grid[target_row][target_col].trigger_enter_event(self.hero)

        return True
