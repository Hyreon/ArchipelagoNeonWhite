# data class

normal_cards = [
    "Purify",
    "Elevate",
    "Stomp",
    "Godspeed",
    "Fireball",
    "Dominion"
]

ability_groups = {
    "Fires": [f"{card} - Fire" for card in normal_cards],
    "Discards": [f"{card} - Discard" for card in normal_cards]
}


abilities = [
    "Katana",
    "Book of Life",
    "Purify - Fire",
    "Purify - Discard",
    "Elevate - Fire",
    "Elevate - Discard",
    "Godspeed - Fire",
    "Godspeed - Discard",
    "Stomp - Fire",
    "Stomp - Discard",
    "Fireball - Fire",
    "Fireball - Discard",
    "Dominion - Fire",
    "Dominion - Discard"
]  # handrolled, to preserve order
