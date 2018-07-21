# coding: utf-8
from __future__ import unicode_literals
from seabattle.game import Game

import pytest


@pytest.fixture
def game():
    g = Game()
    g.start_new_game()

    return g


@pytest.fixture
def game_with_field(game):
    field = [0, 0, 0, 0, 0, 0, 1, 0, 0, 1,
             1, 1, 1, 0, 0, 0, 0, 0, 0, 1,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 1, 0, 1, 0, 1, 0, 0,
             1, 1, 0, 1, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
             0, 1, 0, 1, 0, 1, 1, 1, 0, 0,
             0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 1, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    game.start_new_game(field=field)

    return game


@pytest.fixture
def small_game():
    g = Game()
    g.start_new_game(size=3, field=[0] * 9)

    return g


def test_helper_functions(game):
    assert game.calc_index((4, 7)) == 63

    assert game.calc_position(63) == (4, 7)

    # assert game.convert_to_position('a10') == (1, 10)
    # assert game.convert_to_position('d 7') == (5, 7)
    # assert game.convert_to_position('д 5') == (5, 5)
    # assert game.convert_to_position('g 3') == (4, 3)

    # assert game.convert_to_position('k 1') == (10, 1)
    # assert game.convert_to_position('k 2') == (10, 2)
    # assert game.convert_to_position('k 10') == (10, 10)
    # assert game.convert_to_position('k два') == (10, 2)

    # assert game.convert_to_position('d пять') == (5, 5)

    assert game.convert_to_position('10 10') == (10, 10)
    assert game.convert_to_position('1 10') == (1, 10)
    assert game.convert_to_position('10 1') == (10, 1)
    assert game.convert_to_position('1 2') == (1, 2)
    assert game.convert_to_position('8 4') == (8, 4)
    assert game.convert_to_position('восемь четыре') == (8, 4)

    # assert game.convert_to_position('уже 4') == (7, 4)
    # assert game.convert_to_position('the 4') == (8, 4)
    # assert game.convert_to_position('за 4') == (8, 4)

    with pytest.raises(ValueError):
        assert game.convert_to_position('1') == (1, 1)

    # with pytest.raises(ValueError):
    #    game.convert_to_position('т шесть')

    # with pytest.raises(ValueError):
    #    game.convert_to_position('д пятнадцать')

    # assert game.convert_from_position((1, 1)) == 'а, 1'
    # assert game.convert_from_position((6, 5)) == 'е, 5'
    assert game.convert_from_position((6, 5), numbers=True) == '6, 5'


def test_shot(game_with_field):
    assert game_with_field.handle_enemy_shot((10, 1)) == 'hit'
    assert game_with_field.handle_enemy_shot((10, 2)) == 'kill'

    assert game_with_field.handle_enemy_shot((1, 10)) == 'kill'


def test_dead_ship(game_with_field):
    assert game_with_field.handle_enemy_shot((7, 1)) == 'kill'

    assert game_with_field.handle_enemy_shot((1, 5)) == 'hit'
    assert game_with_field.handle_enemy_shot((2, 5)) == 'kill'

    assert game_with_field.handle_enemy_shot((1, 2)) == 'hit'
    assert game_with_field.handle_enemy_shot((2, 2)) == 'hit'
    assert game_with_field.handle_enemy_shot((3, 2)) == 'kill'


def test_repeat(game):
    game.last_shot_position = (5, 7)
    assert '5, 7' == game.repeat()


def test_handle_shot(game_with_field):
    assert game_with_field.handle_enemy_shot((4, 7)) == 'hit'
    assert game_with_field.handle_enemy_shot((4, 7)) == 'hit'

    assert game_with_field.handle_enemy_shot((7, 1)) == 'kill'
    assert game_with_field.handle_enemy_shot((7, 1)) == 'kill'

    assert game_with_field.handle_enemy_shot((4, 2)) == 'miss'

    with pytest.raises(ValueError):
        game_with_field.handle_enemy_shot((19, 6))


def test_shot2(game):
    result = game.do_shot()
    parts = result.split(', ')
    assert parts[0] in game.str_letters
    assert 0 < int(parts[1]) <= game.size


def test_handle_reply(game):
    game.do_shot()
    game.handle_enemy_reply('miss')


def test_mark_killed(small_game):
    small_game.last_shot_position = (1, 1)
    small_game.handle_enemy_reply('kill')
    assert small_game.enemy_field == [1, 4, 0, 4, 4, 0, 0, 0, 0]


def test_base_point(small_game):
    assert 0 < small_game.base_point[0] <= 3
    assert 0 < small_game.base_point[1] <= 3
    assert small_game.base_point == small_game.base_point


def test_base_diagonally(small_game):
    assert small_game.base_diagonally == small_game.base_diagonally
    assert max(small_game.base_diagonally[0][0], small_game.base_diagonally[0][1]) == 1
    assert min(small_game.base_diagonally[-1][0], small_game.base_diagonally[-1][1]) == 3
    assert 3 <= len(small_game.base_diagonally) <= 5
    for i in xrange(len(small_game.base_diagonally)):
        if i == 0:
            continue
        assert small_game.base_diagonally[i][0] - small_game.base_diagonally[i - 1][0] == 1
        assert small_game.base_diagonally[i][1] - small_game.base_diagonally[i - 1][1] == 1


def test_base_axis(small_game):
    assert small_game.base_axis == small_game.base_axis
    assert small_game.base_axis['x1'][0] == 1
    assert small_game.base_axis['x1'] in small_game.base_diagonally
    assert small_game.base_axis['y1'][1] == 1
    assert small_game.base_axis['y1'] in small_game.base_diagonally
    assert small_game.base_axis['x2'][0] == 3
    assert small_game.base_axis['x2'] in small_game.base_diagonally
    assert small_game.base_axis['y2'][1] == 3
    assert small_game.base_axis['y2'] in small_game.base_diagonally


def test_build_border_4(game):
    border4 = game.build_border_4()
    for element in border4:
        assert element[0] == 1 or element[0] == 10 or element[1] == 1 or element[1] == 10
    assert 8 <= len(border4) <= 10


def test_middle_2(game):
    middle_2 = game.build_middle_2()
    for element in middle_2:
        assert (
            1 < element[0] < 10
            and 1 < element[1] < 10
        )
        game.last_shot_position = element
        game.handle_enemy_reply('miss')
    assert len(middle_2) == 32


def test_strategy_recheck_after_4(game):
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    assert game.state == 1


def test_strategy_move_to_napalm(game):
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.do_shot()
    game.handle_enemy_reply('kill')
    assert game.state == 4


@pytest.mark.skip('Used only to see strategy in action')
def test_shots(game):
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('hit')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('miss')
    game.print_enemy_field()
    game.do_shot()
    game.handle_enemy_reply('kill')
    game.print_enemy_field()
