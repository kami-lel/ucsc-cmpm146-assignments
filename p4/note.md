

Tool Dependency:

- bench: plank
- furnace: bench, cobble
- axe:

    - stone_axe: bench, cobble, stick
    - wooden_axe: bench, plank, stick
    - iron_axe: bench, ingot, stick

- pickaxe:

    - iron_pickaxe: bench, ingot, stick
    - stone_pickaxe: bench, cobble, stick
    - wooden_pickaxe: bench, plank, stick

Resource:

- wood: iron_axe | stone_axe | wooden_axe | punch
- cobble: wooden_pickaxe | iron_pickaxe | stone_pickaxe
- coal: wooden_pickaxe | iron_pickaxe | stone_pickaxe
- ore: iron_pickaxe | stone_pickaxe

Items:

- ingot: ore, coal
- plank: wood
- stick: plank
- rail: ingot, stick
- cart: ingot

----

