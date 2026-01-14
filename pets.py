import random
import time

# Define available pet types 
PET_TYPES = {
    "Fuzzball": {"emoji": "🐹", "color": "#FFDAB9", "rarity": "common"},
    "Glitterpup": {"emoji": "🐶✨", "color": "#E6E6FA", "rarity": "uncommon"},
    "Slimey": {"emoji": "🟢", "color": "#98FB98", "rarity": "common"},
    "Starwhisker": {"emoji": "🐱🌟", "color": "#DDA0DD", "rarity": "rare"},
    "Dragonling": {"emoji": "🐉", "color": "#FFB6C1", "rarity": "epic"},
    "Nebulite": {"emoji": "👾🌌", "color": "#4B0082", "rarity": "legendary"}
}


# This is a mapping of rarity levels to their weights for random selection, like a gacha
RARITY_WEIGHTS = {
    "common": 50,
    "uncommon": 30,
    "rare": 15,
    "epic": 4,
    "legendary": 1
}

def get_random_pet():
    """Gacha-style pet adoption: weighted random selection."""
    choices = []
    for name, data in PET_TYPES.items():
        choices.extend([name] * RARITY_WEIGHTS[data["rarity"]])
    chosen = random.choice(choices)
    return {
        "name": chosen,
        "emoji": PET_TYPES[chosen]["emoji"],
        "color": PET_TYPES[chosen]["color"],
        "rarity": PET_TYPES[chosen]["rarity"]
    }

class Buddy:
    def __init__(self, pet_data):
        self.name = pet_data["name"]
        self.emoji = pet_data["emoji"]
        self.color = pet_data["color"]
        self.rarity = pet_data["rarity"]
        
        #stats for the monsters
        self.hunger - 80
        self.happiness = 70
        self.energy = 90
        self.cleanliness = 75
        
        #emotional state
        self.emotion = 'happy'
        
    def get_lowest_stat(self):
        stats = {
            "hunger": self.hunger,
            "happiness": self.happiness,
            "energy": self.energy,
            "cleanliness": self.cleanliness
        }
        lowest_stat = min(stats, key=stats.get)
        return lowest_stat, stats[lowest_stat]s