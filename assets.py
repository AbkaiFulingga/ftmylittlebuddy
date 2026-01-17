# assets.py - ASCII art, themes, and static data, I used ASCII art for the simplicity that it provides so I do not have to draw any of my own art for the project
PET_ART = {
    # Fuzzball species
    "fuzzball": {
        "common": {
            "baby": {
                "idle": [
                    "  .-.  ",
                    " (o o) ",
                    "  |=|  ",
                    " /   \\ ",
                    "|     |",
                    "'-----'"
                ],
                "blink": [
                    "  .-.  ",
                    " ( - -) ",
                    "  |=|  ",
                    " /   \\ ",
                    "|     |",
                    "'-----'"
                ],
                "eating": [
                    "  .-.  ",
                    " (o o) ",
                    "  |=|  ",
                    " / 0 \\ ",
                    "|     |",
                    "'-----'"
                ]
            },
            "child": {
                "idle": [
                    "   .-.-.   ",
                    "  (o o o)  ",
                    "   |=|=|   ",
                    "  /  |  \\  ",
                    " |       | ",
                    " '-------' "
                ],
                "blink": [
                    "   .-.-.   ",
                    "  (- - -)  ",
                    "   |=|=|   ",
                    "  /  |  \\  ",
                    " |       | ",
                    " '-------' "
                ]
            },
            "adult": {
                "joy": [
                    "   .-\"\"\"-.   ",
                    "  / o   o \\  ",
                    " |    \"    | ",
                    " |  \\___/  | ",
                    "  \\       /  ",
                    "   '-----'   ",
                    "     | |     ",
                    "    /   \\    "
                ],
                "pure": [
                    "   .-*\"\"*-.   ",
                    "  /* o o o *\\ ",
                    " |*   \" \"   *|",
                    " |*  \\___/  *|",
                    "  \\*       */  ",
                    "   '-*****-'   ",
                    "      | |      ",
                    "     /   \\     "
                ]
            }
        }
    },
    
    # Glitterpup species
    "glitterpup": {
        "uncommon": {
            "baby": {
                "idle": [
                    "   /^\\   ",
                    "  / o \\  ",
                    " (  \"  ) ",
                    "  \\~~~/  ",
                    "   | |   ",
                    "  /   \\  "
                ],
                "blink": [
                    "   /^\\   ",
                    "  / - \\  ",
                    " (  \"  ) ",
                    "  \\~~~/  ",
                    "   | |   ",
                    "  /   \\  "
                ],
                "eating": [
                    "   /^\\   ",
                    "  / o \\  ",
                    " (  \"  ) ",
                    "  \\ 0 /  ",
                    "   | |   ",
                    "  /   \\  "
                ]
            },
            "child": {
                "idle": [
                    "   *^*   ",
                    "  * o *  ",
                    " ( \" \" ) ",
                    "  \\~~~/  ",
                    "  *| |*  ",
                    "  /   \\  "
                ],
                "blink": [
                    "   *^*   ",
                    "  * - *  ",
                    " ( \" \" ) ",
                    "  \\~~~/  ",
                    "  *| |*  ",
                    "  /   \\  "
                ]
            },
            "adult": {
                "spark": [
                    "   *^\\^*   ",
                    "  * o o *  ",
                    " (* \"*\" *) ",
                    "  *\\~*~/  ",
                    "  **| |** ",
                    "   /   \\   ",
                    "  *-----*  ",
                    " *       * "
                ],
                "bonded": [
                    "   *^\\^*   ",
                    "  * o o *  ",
                    " (* \"*\" *) ",
                    "  *\\~*~/  ",
                    "  **| |** ",
                    "   / H \\   ",
                    "  *-----*  ",
                    " *       * "
                ]
            }
        }
    },
    
    # Slimey species
    "slimey": {
        "common": {
            "baby": {
                "idle": [
                    "  .--.  ",
                    " / oo \\ ",
                    "|  ..  |",
                    " \\ -- / ",
                    "  '~~'  "
                ],
                "blink": [
                    "  .--.  ",
                    " / -- \\ ",
                    "|  ..  |",
                    " \\ -- / ",
                    "  '~~'  "
                ],
                "bouncing": [
                    "   oo   ",
                    "  .--.  ",
                    " /    \\ ",
                    "| .. .. |",
                    " \\ -- / ",
                    "  '~~'  "
                ]
            },
            "child": {
                "idle": [
                    "   .--.   ",
                    "  / oo \\  ",
                    " |  ..  | ",
                    "  \\ -- /  ",
                    "   '--'   ",
                    "  /    \\  ",
                    " |      | ",
                    "  '----'  "
                ],
                "blink": [
                    "   .--.   ",
                    "  / -- \\  ",
                    " |  ..  | ",
                    "  \\ -- /  ",
                    "   '--'   ",
                    "  /    \\  ",
                    " |      | ",
                    "  '----'  "
                ]
            },
            "adult": {
                "plush": [
                    "   .****.   ",
                    "  / o**o \\  ",
                    " |  ****  | ",
                    "  \\ **** /  ",
                    "   '****'   ",
                    "  /      \\  ",
                    " |  ~~~~  | ",
                    "  '------'  "
                ],
                "pure": [
                    "   .****.   ",
                    "  /* o o *\\ ",
                    " |*  ***  *| ",
                    "  \\* *** */  ",
                    "   '**** *'  ",
                    "  /*     *\\  ",
                    " |*  ***  *| ",
                    "  '*-----*'  "
                ]
            }
        }
    },
    
    # Starwhisker species
    "starwhisker": {
        "rare": {
            "baby": {
                "idle": [
                    "  ^ ^  ",
                    " (• •) ",
                    "  > <  ",
                    " /   \\ ",
                    "*     *",
                    " \\___/ "
                ],
                "blink": [
                    "  ^ ^  ",
                    " (- -) ",
                    "  > <  ",
                    " /   \\ ",
                    "*     *",
                    " \\___/ "
                ],
                "purring": [
                    "  ^ ^  ",
                    " (• •) ",
                    "  > <  ",
                    " / * \\ ",
                    "*  *  *",
                    " \\_*_/ "
                ]
            },
            "child": {
                "idle": [
                    "   ^ ^ ^   ",
                    "  (• • •)  ",
                    "   > < >   ",
                    "  /  *  \\  ",
                    " *   *   * ",
                    "  \\__*__/  "
                ],
                "blink": [
                    "   ^ ^ ^   ",
                    "  (- - -)  ",
                    "   > < >   ",
                    "  /  *  \\  ",
                    " *   *   * ",
                    "  \\__*__/  "
                ]
            },
            "adult": {
                "cosmic": [
                    "   ^  *  ^   ",
                    "  (• * • * •) ",
                    "   >* <* >*   ",
                    "  /*  *  *\\  ",
                    " *  *  *  *  ",
                    "  \\__*_*__/  ",
                    "    |   |     ",
                    "   / /  \\   "
                ],
                "bonded": [
                    "   ^  *  ^   ",
                    "  (• * • * •) ",
                    "   >* <* >*   ",
                    "  /*  *  *\\  ",
                    " * * * * ",
                    "  \\__*_*__/  ",
                    "    |   |     ",
                    "   //   \\   "
                ]
            }
        }
    },
    
    # Dragonling species
    "dragonling": {
        "epic": {
            "baby": {
                "idle": [
                    "   ,_,   ",
                    "  (o,o)  ",
                    "  (   )  ",
                    "   \"\"\"   ",
                    "  / | \\  ",
                    " /  |  \\ "
                ],
                "blink": [
                    "   ,_,   ",
                    "  (-,-)  ",
                    "  (   )  ",
                    "   \"\"\"   ",
                    "  / | \\  ",
                    " /  |  \\ "
                ],
                "breathing": [
                    "   ,_,   ",
                    "  (o,o)  ",
                    "  ( ~ )  ",
                    "  / ^ \\  ",
                    " /  |  \\ ",
                    "    |    "
                ]
            },
            "child": {
                "idle": [
                    "    ,_,,_,    ",
                    "   ( o o o )   ",
                    "    (  \"  )    ",
                    "   /  ^^^  \\   ",
                    "  /   | |   \\  ",
                    " |    | |    | ",
                    "  \\   | |   /  ",
                    "   '-------'   "
                ],
                "blink": [
                    "    ,_,,_,    ",
                    "   ( - - - )   ",
                    "    (  \"  )    ",
                    "   /  ^^^  \\   ",
                    "  /   | |   \\  ",
                    " |    | |    | ",
                    "  \\   | |   /  ",
                    "   '-------'   "
                ]
            },
            "adult": {
                "spark": [
                    "   **,_,,**    ",
                    "  **(o o o)**   ",
                    "   **( ^ )**    ",
                    "   /* ^^^ *\\   ",
                    "  /*  | |  *\\  ",
                    " |*   | |   *| ",
                    "  \\*  | |  */  ",
                    "   '*******'   ",
                    "    |*****|    ",
                    "   //     \\   "
                ],
                "bonded": [
                    "   **,_,,**    ",
                    "  **(o o o)**   ",
                    "   **( ^ )**    ",
                    "   /* ^^^ *\\   ",
                    "  /* * * * *\\  ",
                    " |*   ***   *| ",
                    "  \\*  ***  */  ",
                    "   '*******'   ",
                    "    |*****|    ",
                    "   //     \\   "
                ]
            }
        }
    },
    
    # Nebulite species (legendary)
    "nebulite": {
        "legendary": {
            "baby": {
                "idle": [
                    "  .-=-.  ",
                    " ( o o ) ",
                    "  \\ - /  ",
                    "  /   \\  ",
                    " |  .  | ",
                    "  '-=-'  "
                ],
                "blink": [
                    "  .-=-.  ",
                    " ( - - ) ",
                    "  \\ - /  ",
                    "  /   \\  ",
                    " |  .  | ",
                    "  '-=-'  "
                ],
                "floating": [
                    "   ...   ",
                    "  .-=-.  ",
                    " ( o o ) ",
                    "  \\ - /  ",
                    "  /   \\  ",
                    " |  .  | "
                ]
            },
            "child": {
                "idle": [
                    "   .-=-.   ",
                    "  ( o o o ) ",
                    "   \\ - - /  ",
                    "   /  *  \\  ",
                    "  | * . * | ",
                    "   \\  *  /  ",
                    "    '-=-'   "
                ],
                "blink": [
                    "   .-=-.   ",
                    "  ( - - - ) ",
                    "   \\ - - /  ",
                    "   /  *  \\  ",
                    "  | * . * | ",
                    "   \\  *  /  ",
                    "    '-=-'   "
                ]
            },
            "adult": {
                "cosmic": [
                    "   *.-= =-.*   ",
                    "  *( o * o )*  ",
                    "  *\\ - * - /*  ",
                    "  /*   *   *\\  ",
                    " |*  * . *  *| ",
                    "  \\*  * *  */  ",
                    "   '*-=== -*'  ",
                    "     \\ * /     ",
                    "      \\*/      ",
                    "        *     "
                ],
                "bonded": [
                    "   *.-= =-.*   ",
                    "  *( o * o )*  ",
                    "  *\\ - * - /*  ",
                    "  /* * * * *\\  ",
                    " |*   ***   *| ",
                    "  \\*  * *  */  ",
                    "   '*-=== -*'  ",
                    "     \\ * /     ",
                    "      \\*/      ",
                ]
            }
        }
    }
}

# RARITY DEFINITIONS for behaviour gameplay  
RARITY_DEFINITIONS = {
    "common": {
        "chance": 50,
        "color": "#7f8c8d",
        "stat_bonus": 0,
        "evolution_time": 300  # 300 seconds in mins = 5 minutes
    },
    "uncommon": {
        "chance": 30,
        "color": "#2ecc71",
        "stat_bonus": 5,
        "evolution_time": 270  # 270 secondsin mins =4.5 minutes
    },
    "rare": {
        "chance": 15,
        "color": "#3498db",
        "stat_bonus": 10,
        "evolution_time": 240  # 240 seconds in mins is 4 minutes
    },
    "epic": {
        "chance": 4,
        "color": "#9b59b6",
        "stat_bonus": 15,
        "evolution_time": 210  # 210 secondsin mins is 3.5 minutes
    },
    "legendary": {
        "chance": 1,
        "color": "#f1c40f",
        "stat_bonus": 20,
        "evolution_time": 180  # 180 seconds in mins is 3 minutes
    }
}

# PERSONALITY TRAITS 
PERSONALITY_TRAITS = {
    "playful": {
        "happiness_decay": 1.3,
        "energy_decay": 1.2,
        "play_reward": 1.5,
        "color": "#e74c3c"
    },
    "lazy": {
        "energy_decay": 0.7,
        "happiness_decay": 0.8,
        "sleep_reward": 1.3,
        "color": "#9b59b6"
    },
    "hungry": {
        "hunger_decay": 1.4,
        "feed_reward": 1.2,
        "cleanliness_decay": 1.1,
        "color": "#e67e22"
    },
    "neat_freak": {
        "cleanliness_decay": 1.3,
        "clean_reward": 1.5,
        "happiness_reward": 1.2,
        "color": "#1abc9c"
    },
    "chill": {
        "all_decay": 0.8,
        "action_reward": 0.9,
        "color": "#3498db"
    }
}

#THEME DEFINITIONS for unlocking under achievements
THEMES = {
    "forest": {
        "bg": "#e0f2e0",
        "fg": "#1e5f2c",
        "bar_bg": "#c5e8c5",
        "button_bg": "#a8d8a8",
        "rarity_colors": {
            "common": "#7f8c8d",
            "uncommon": "#2ecc71",
            "rare": "#3498db",
            "epic": "#9b59b6",
            "legendary": "#f1c40f"
        },
        "unlock_condition": "default"
    },
    "space": {
        "bg": "#0f0c29",
        "fg": "#e0e0ff",
        "bar_bg": "#2a275f",
        "button_bg": "#3a376f",
        "rarity_colors": {
            "common": "#7f8c8d",
            "uncommon": "#2ecc71",
            "rare": "#3498db",
            "epic": "#9b59b6",
            "legendary": "#f1c40f"
        },
        "unlock_condition": "evolved_2_pets"
    },
    "sunset": {
        "bg": "#ff9e80",
        "fg": "#5e2a2a",
        "bar_bg": "#ffb49a",
        "button_bg": "#ff7a64",
        "rarity_colors": {
            "common": "#7f8c8d",
            "uncommon": "#2ecc71",
            "rare": "#3498db",
            "epic": "#9b59b6",
            "legendary": "#f1c40f"
        },
        "unlock_condition": "satisfaction_10_times"
    },
    "night": {
        "bg": "#1a1a2e",
        "fg": "#e6e6e6",
        "bar_bg": "#2d2d44",
        "button_bg": "#3f3f5a",
        "rarity_colors": {
            "common": "#7f8c8d",
            "uncommon": "#2ecc71",
            "rare": "#3498db",
            "epic": "#9b59b6",
            "legendary": "#f1c40f"
        },
        "unlock_condition": "play_at_22h"
    },
    "chromatic": {
        "bg": "#2c2c2c",
        "fg": "#ffffff",
        "bar_bg": "#444444",
        "button_bg": "#555555",
        "rarity_colors": {
            "common": "#aaaaaa",
            "uncommon": "#50fa7b",
            "rare": "#8be9fd",
            "epic": "#bd93f9",
            "legendary": "#ff79c6"
        },
        "unlock_condition": "legendary_pet"
    }
}

# Bubble pop ASSETS
BUBBLE_CHAR = "●"