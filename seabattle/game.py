# coding: utf-8

from __future__ import unicode_literals

import random
import re

from transliterate import translit

EMPTY = 0
SHIP = 1
HIT = 2
BLOCKED = 3
MISS = 4


class Messages:
    HIT = 'hit'
    KILL = 'kill'
    MISS = 'miss'


class BaseGame(object):
    position_patterns = [re.compile('^([a-zа-я]+)(\d+)$', re.UNICODE),  # a1
                         re.compile('^([a-zа-я]+)\s+(\w+)$', re.UNICODE),  # a 1; a один
                         re.compile('^(\w+)\s+(\w+)$', re.UNICODE),  # a 1; a один; 7 10
                         re.compile('^(\w+)$', re.UNICODE)  # 1; один
                         ]

    str_letters = ['а', 'б', 'в', 'г', 'д', 'е', 'ж', 'з', 'и', 'к']
    str_numbers = ['один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять']

    letters_mapping = {'the': 'з',
                       'за': 'з',
                       'уже': 'ж'}

    default_ships = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]

    def __init__(self):
        self.size = 0
        self.ships = None
        self.field = []
        self.enemy_field = []

        self.ships_count = 0
        self.enemy_ships_count = 0

        self.last_shot_position = None
        self.last_enemy_shot_position = None
        self.numbers = None

    def start_new_game(self, size=10, field=None, ships=None, numbers=None):
        assert(len(field) == size ** 2 if field is not None else True)
        self.size = size
        self.numbers = numbers if numbers is not None else False

        if ships is None:
            self.ships = self.default_ships
        else:
            self.ships = ships

        if field is None:
            self.generate_field()
        else:
            self.field = field

        self.enemy_field = [EMPTY] * self.size ** 2

        self.ships_count = self.enemy_ships_count = len(self.ships)

        self.last_shot_position = None
        self.last_enemy_shot_position = None

    def generate_field(self):
        raise NotImplementedError()

    def base_print_field(self, field):
        mapping = [' ', '0', 'x', 'b', '.']

        print '---'
        for y in range(self.size):
            print '|%s|' % ''.join(mapping[x] for x in field[y * self.size: y * self.size + self.size])
        print '---'

    def print_field(self):
        return self.base_print_field(self.field)

    def print_enemy_field(self):
        return self.base_print_field(self.enemy_field)

    def handle_enemy_shot(self, position):
        index = self.calc_index(position)

        if self.field[index] == SHIP:
            self.field[index] = HIT

            if self.is_dead_ship(index):
                self.ships_count -= 1
                return Messages.KILL
            else:
                return Messages.HIT
        else:
            return Messages.MISS

    def is_dead_ship(self, last_index):
        x, y = self.calc_position(last_index)
        x -= 1
        y -= 1

        def _line_is_dead(line, index):
            def _tail_is_dead(tail):
                for i in tail:
                    if i == HIT:
                        continue
                    elif i == SHIP:
                        return False
                    else:
                        return True
                return True

            return _tail_is_dead(line[index:]) and _tail_is_dead(line[index::-1])

        return (
            _line_is_dead(self.field[x::self.size], y) and
            _line_is_dead(self.field[y * self.size:(y + 1) * self.size], x)
        )

    def is_end_game(self):
        return self.is_victory() or self.is_defeat()

    def is_victory(self):
        return self.enemy_ships_count < 1

    def is_defeat(self):
        return self.ships_count < 1

    def do_shot(self):
        raise NotImplementedError()

    def repeat(self):
        return self.convert_from_position(self.last_shot_position, numbers=True)

    def handle_enemy_reply(self, message):
        if self.last_shot_position is None:
            return

        index = self.calc_index(self.last_shot_position)

        if message in [Messages.HIT, Messages.KILL]:
            self.enemy_field[index] = SHIP

            if message == Messages.KILL:
                self.enemy_ships_count -= 1

        elif message == Messages.MISS:
            self.enemy_field[index] = MISS

    def calc_index(self, position):
        x, y = position

        if x > self.size or y > self.size:
            raise ValueError('Wrong position: %s %s' % (x, y))

        return (y - 1) * self.size + x - 1

    def calc_position(self, index):
        y = index / self.size + 1
        x = index % self.size + 1

        return x, y

    def convert_to_position(self, position):
        position = position.lower()
        for pattern in self.position_patterns:
            match = pattern.match(position)

            if match is not None:
                break
        else:
            raise ValueError('Can\'t parse entire position: %s' % position)

        bits = match.groups()

        if len(bits) == 1:
            bits = ('а', bits[0])

        def _try_letter(bit):
            # проверяем особые случаи неправильного распознования STT
            bit = self.letters_mapping.get(bit, bit)

            # преобразуем в кириллицу
            bit = translit(bit, 'ru')

            try:
                return self.str_letters.index(bit) + 1
            except ValueError:
                raise

        def _try_number(bit):
            if bit.isdigit():
                return int(bit)
            else:
                try:
                    return self.str_numbers.index(bit) + 1
                except ValueError:
                    raise

        x = bits[0].strip()
        try:
            x = _try_letter(x)
        except ValueError:
            try:
                x = _try_number(x)
            except ValueError:
                raise ValueError('Can\'t parse X point: %s' % x)

        y = bits[1].strip()
        try:
            y = _try_number(y)
        except ValueError:
            raise ValueError('Can\'t parse Y point: %s' % y)

        return x, y

    def convert_from_position(self, position, numbers=None):
        numbers = numbers if numbers is not None else self.numbers

        if numbers:
            x = position[0]
        else:
            x = self.str_letters[position[0] - 1]

        y = position[1]

        return '%s, %s' % (x, y)


class States:
    BORDER4 = 0
    BORDER2 = 1
    MIDDLE4 = 2
    MIDDLE2 = 3
    NAPALM = 4


class Game(BaseGame):
    """Реализация игры с ипользованием обычного random"""

    def __init__(self):
        super(Game, self).__init__()
        self._base_point = None
        self._base_diagonally = None
        self._base_axis = None
        self.last_shout_message = MISS
        self.wounded_ship = False
        self.last_hit = None
        self.state = States.BORDER4
        self.maps = []
        self.enemy_ships = {}
        self.hits = 0
        self.ship_under_fire = []

    def start_new_game(self, size=10, field=None, ships=None, numbers=None):
        super(Game, self).start_new_game(size, field, ships, numbers)
        self.maps = self.build_maps()
        for ship in self.ships:
            if ship not in self.enemy_ships:
                self.enemy_ships[ship] = 0
            self.enemy_ships[ship] += 1

    @property
    def base_point(self):
        if self._base_point is None:
            self._base_point = (
                random.randint(1, self.size),
                random.randint(1, self.size),
            )
        return self._base_point

    @property
    def base_diagonally(self):
        if self._base_diagonally is None:
            move = max(*self.base_point) - 1
            point = (self.base_point[0] - move, self.base_point[1] - move)
            length = -min(*point) + 1 + self.size
            self._base_diagonally = [
                (point[0] + i, point[1] + i) for i in xrange(length)
            ]
        return self._base_diagonally

    @property
    def base_axis(self):
        if self._base_axis is None:
            self._base_axis = {}
            for point in self.base_diagonally:
                if point[0] == 1:
                    self._base_axis['x1'] = point
                elif point[0] == self.size:
                    self._base_axis['x2'] = point
                if point[1] == 1:
                    self._base_axis['y1'] = point
                elif point[1] == self.size:
                    self._base_axis['y2'] = point
        return self._base_axis

    def expand_point_by(self, start, step, axis, min_value=1, max_value=None):
        if max_value is None:
            max_value = self.size
        result = set()
        point = list(start)
        while point[axis] >= min_value:
            if min_value <= point[0] <= max_value and min_value <= point[1] <= max_value:
                result.add(tuple(point))
            point[axis] -= step
        point = list(start)
        while point[axis] <= max_value:
            if min_value <= point[0] <= max_value and min_value <= point[1] <= max_value:
                result.add(tuple(point))
            point[axis] += step
        return result

    def build_border_n(self, n):
        return self.expand_point_by(
            self.base_axis['x1'], n, 1
        ).union(
            self.expand_point_by(
                self.base_axis['x2'], n, 1
            )
        ).union(
            self.expand_point_by(
                self.base_axis['y1'], n, 0
            )
        ).union(
            self.expand_point_by(
                self.base_axis['y2'], n, 0
            )
        )

    def build_border_4(self):
        return self.build_border_n(4)

    def build_border_2(self):
        return self.build_border_n(2)

    def build_middle_n(self, n):
        elements = set()
        for point in self.base_diagonally:
            elements = elements.union(self.expand_point_by(
                point, n, 0, 2, self.size - 1,
            ))
        return elements

    def build_middle_4(self):
        return self.build_middle_n(4)

    def build_middle_2(self):
        return self.build_middle_n(2)

    def build_napalm(self):
        return set(
            self.calc_position(i) for i in xrange(len(self.enemy_field))
        )

    def build_maps(self):
        return [
            self.build_border_4(),
            self.build_border_2(),
            self.build_middle_4(),
            self.build_middle_2(),
            self.build_napalm(),
        ]

    def generate_field(self):
        """Метод генерации поля"""
        self.field = [0] * self.size ** 2

        for length in self.ships:
            self.place_ship(length)

        for i in range(0, len(self.field)):
            if self.field[i] == BLOCKED:
                self.field[i] = EMPTY

    def place_ship(self, length):
        def _try_to_place():
            x = random.randint(1, self.size)
            y = random.randint(1, self.size)
            direction = random.choice([1, self.size])

            index = self.calc_index((x, y))
            values = self.field[index:None if direction != 1 else index + self.size - index % self.size:direction][:length]

            if len(values) < length or any(values):
                return False

            for i in range(0, length):
                current_index = index + direction * i

                for j in [0, 1, -1]:
                    if (current_index % self.size in (0, self.size - 1)
                            and (current_index + j) % self.size in (0, self.size - 1)):
                        continue

                    for k in [0, self.size, -self.size]:
                        neighbour_index = current_index + k + j

                        if (neighbour_index < 0
                                or neighbour_index >= len(self.field)
                                or self.field[neighbour_index] == SHIP):
                            continue

                        self.field[neighbour_index] = BLOCKED

                self.field[current_index] = SHIP

            return True

        while not _try_to_place():
            pass

    def do_shot(self):
        """
        Метод выбора координаты выстрела.
        """
        self.last_shot_position = self.choose_shot_position()
        return self.convert_from_position(self.last_shot_position)

    def hunt_for_wounded(self):
        if len(self.ship_under_fire) == 1:
            variants = set(filter(
                lambda point: 1 <= point[0] <= self.size and 1 <= point[1] <= self.size,
                [
                    (self.last_hit[0], self.last_hit[1] - 1),
                    (self.last_hit[0], self.last_hit[1] + 1),
                    (self.last_hit[0] - 1, self.last_hit[1]),
                    (self.last_hit[0] + 1, self.last_hit[1]),
                ],
            ))
        else:
            if self.ship_under_fire[0][0] == self.ship_under_fire[1][0]:
                variants = set([(point[0], point[1] - 1) for point in self.ship_under_fire]).union(
                    [(point[0], point[1] + 1) for point in self.ship_under_fire]
                )
            else:
                variants = set([(point[0] - 1, point[1]) for point in
                                self.ship_under_fire]).union(
                    [(point[0] + 1, point[1]) for point in self.ship_under_fire]
                )
            variants = set(filter(
                lambda point: 1 <= point[0] <= self.size and 1 <= point[1] <= self.size,
                variants
            ))
        while len(variants):
            candidate = random.sample(variants, 1)[0]
            variants.discard(candidate)
            if self.enemy_field[self.calc_index(candidate)] == EMPTY:
                break
        else:
            raise Exception('SHOULD BE KILLED ALREADY!')
        return candidate

    def expand_state(self):
        self.state += 1
        self.recheck_state()
        if self.state >= len(self.maps):
            raise Exception('MAP IS DEVASTATED ALREADY!')

    def hunt_for_new(self):
        map = self.maps[self.state]
        while len(map):
            candidate = random.sample(map, 1)[0]
            map.discard(candidate)
            if self.enemy_field[self.calc_index(candidate)] == EMPTY:
                break
        else:
            self.expand_state()
            return self.hunt_for_new()
        return candidate

    def choose_shot_position(self):
        if self.wounded_ship:
            return self.hunt_for_wounded()
        return self.hunt_for_new()

    def handle_enemy_reply(self, message):
        super(Game, self).handle_enemy_reply(message)
        self.last_shout_message = message
        if message == Messages.HIT:
            self.wounded_ship = True
            self.hits += 1
            self.last_hit = self.last_shot_position
            self.ship_under_fire.append(self.last_hit)
        elif message == Messages.KILL:
            self.mark_killed_ship_bounds(self.last_shot_position)
            self.wounded_ship = False
            self.enemy_ships[self.hits + 1] -= 1
            self.recheck_state()
            self.hits = 0
            self.ship_under_fire = []

    def recheck_state(self):
        if self.enemy_ships[4] + self.enemy_ships[3] + self.enemy_ships[2] == 0:
            self.state = States.NAPALM
            return
        if self.state == States.BORDER4 or self.state == States.MIDDLE4 and self.enemy_ships[4] == 0:
            self.state += 1
            return

    def mark_killed_ship_bounds(self, position):
        def mark_point((x, y)):
            for i in [-1, 0, 1]:
                for j in [-1, 0, 1]:
                    if i == 0 and j == 0:
                        continue
                    new_position = (x + i, y + j)
                    if new_position[0] <= 0 or new_position[1] <= 0 or new_position[0] > self.size or new_position[1] > self.size:
                        continue
                    index_to_mark = self.calc_index(new_position)
                    if self.enemy_field[index_to_mark] == SHIP and new_position not in marked_positions:
                        marked_positions.add(new_position)
                        mark_point(new_position)
                    elif self.enemy_field[index_to_mark] != SHIP:
                        self.enemy_field[index_to_mark] = MISS

        marked_positions = {position}
        mark_point(position)
