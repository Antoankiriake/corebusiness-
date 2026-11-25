## Business Logic (`CORE`)

### Responsibilities
The `CORE` layer encapsulates the application's rules, states, and domain logic independently of the presentation layer (`CLI`/`GUI`) and persistence layer (`DATA`). It does not perform direct input/output, file/database access, or network calls.

### Core Entities
- `GameConfig`: Holds initial match settings, maximum turns, and participating characters.
- `Game`: Sets up and starts the game (`setup_game`, `start_game`) and checks end conditions (`is_game_over`).
- `Turn`: Tracks turn numbers (`begin_turn`) and executes actions (`act`).
- `Character`: Stores stats (`health`, `damage`, `magic_res`, `bonus_prof`, `debuffs`) and performs `attack`, `heal`, `action`, and `check_status`.
- `CharacterProfile`, `Item`, `Ability`: Manage items, abilities, and stat modifiers.

### Design Patterns
- **Strategy (`DamageStrategy` / `StandardDamageStrategy`):** Encapsulates magic damage calculation so rules can be swapped or extended without modifying `Character`.
- **Action Dispatch (`ActionType` in `Turn.act`):** Routes turn commands (`ATTACK`, `HEAL`, `ABILITY`) cleanly.
- **Repository Interface (`GameConfigRepository`):** Defines a data contract in `CORE` to be implemented in `DATA`.

### Rules & Formulas
- Ability debuff total: `dmg_ability = sum(debuffs)`
- Magic damage: `max(0, (dmg_flat * max(0, 1 - res_tgt + res_pen) + bonus_flat) * max(0, bonus_prof - dmg_ability))`
- A character with `health > 0` is alive (`ALIVE`); at `0` or below they are defeated (`DEFEATED`).