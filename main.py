from corebusiness_logic import ActionId, Game


def main() -> None:
    game = Game()
    config = game.setup_game()
    game.start_game(config)

    hero, enemy = config.characters[0], config.characters[1]

    game.turn.begin_turn()
    print(game.turn.act(ActionId.ATTACK, hero, enemy))

    game.turn.begin_turn()
    print(game.turn.act(ActionId.ABILITY, hero, enemy, ability_index=0))


if __name__ == "__main__":
    main()
