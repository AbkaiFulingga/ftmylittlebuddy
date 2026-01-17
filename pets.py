import random
import time
import math
import os
from assets import PET_ART, RARITY_DEFINITIONS, PERSONALITY_TRAITS

PET_SPECIES = [
    "fuzzball", "glitterpup", "slimey", 
    "starwhisker", "dragonling", "nebulite"
]

class Buddy:
    def __init__(self, species=None, rarity=None, personality=None, from_data=None):
        if from_data:
            self.load_from_data(from_data)
            return
            
        # Random generation if not loaded
        self.species = species or random.choice(PET_SPECIES)
        self.rarity = rarity or self._determine_rarity()
        self.personality = personality or self._determine_personality()
        
        # Core stats (0-100)
        self.hunger = 80
        self.energy = 85
        self.cleanliness = 75
        self.happiness = 70
        
        # Hidden stats
        self.affection = 50  # 0-100
        self.satisfaction = 0  # 0-100, resets after getting reward
        
        # Evolution tracking
        self.stage = 1  # 1=baby, 2=child, 3=adult
        self.evolution_timer = 0
        self.evolution_ready = False
        self.evolution_branch = None
        
        # Visual state/interaction 
        self.blink_state = 0  # 0=open, 1=blink
        self.last_blink = time.time()
        self.last_breath = time.time()
        self.breath_phase = 0
        self.last_action = "idle"
        
        # Apply rarity and personality bonuses
        self.apply_rarity_bonus()
        self.decay_multipliers = self.get_decay_multipliers()
    
    def _determine_rarity(self):
        """Determine rarity based on weighted chances"""
        available = list(PET_ART.get(self.species, {}).keys())
        if not available:
            # Fallback to global rarities if species has no art entries
            choices = []
            for rarity, data in RARITY_DEFINITIONS.items():
                choices.extend([rarity] * data["chance"])
            return random.choice(choices)

        # Build weighted list only from available rarities
        choices = []
        for rarity, data in RARITY_DEFINITIONS.items():
            if rarity in available:
                choices.extend([rarity] * data["chance"])

        if not choices:
            # As a final fallback which should not be called , pick any available rarity
            return random.choice(available)

        return random.choice(choices)
    
    def _determine_personality(self):
        """Determine 1-2 personality traits"""
        traits = list(PERSONALITY_TRAITS.keys())
        num_traits = random.choice([1, 1, 2])  # More likely to have 1 trait
        return random.sample(traits, num_traits)
    
    def apply_rarity_bonus(self):
        """Apply stat bonuses based on rarity"""
        bonus = RARITY_DEFINITIONS[self.rarity]["stat_bonus"]
        self.hunger = min(100, self.hunger + bonus)
        self.energy = min(100, self.energy + bonus)
        self.cleanliness = min(100, self.cleanliness + bonus)
        self.happiness = min(100, self.happiness + bonus)

    # Tunable multipliers to control game pacing
    DECAY_SPEED_MULTIPLIER = 1.8  # multiply base decay to make stats fall faster for gameplay
    ACTION_GAIN_MULTIPLIER = 1.5  # multiply action gains to make recovery snappier for gameplay
    
    def get_decay_multipliers(self):
        """Get decay multipliers based on personality"""
        multipliers = {
            "hunger_decay": 1.0,
            "energy_decay": 1.0,
            "cleanliness_decay": 1.0,
            "happiness_decay": 1.0,
            "affection_decay": 1.0
        }
        
        for trait in self.personality:
            trait_data = PERSONALITY_TRAITS[trait]
            
            if "all_decay" in trait_data:
                for key in multipliers:
                    multipliers[key] *= trait_data["all_decay"]
            else:
                if "hunger_decay" in trait_data:
                    multipliers["hunger_decay"] *= trait_data["hunger_decay"]
                if "energy_decay" in trait_data:
                    multipliers["energy_decay"] *= trait_data["energy_decay"]
                if "cleanliness_decay" in trait_data:
                    multipliers["cleanliness_decay"] *= trait_data["cleanliness_decay"]
                if "happiness_decay" in trait_data:
                    multipliers["happiness_decay"] *= trait_data["happiness_decay"]
                if "affection_decay" in trait_data:
                    multipliers["affection_decay"] *= trait_data["affection_decay"]
        
        # Evolution stage affects decay
        if self.stage >= 2:
            for key in multipliers:
                multipliers[key] *= 0.9  # 10% less decay for evolved pets
        if self.stage >= 3:
            for key in multipliers:
                multipliers[key] *= 0.85  # 15% less decay for adult pets
        
        return multipliers
    
    def get_stat_average(self):
        """Calculate average of visible stats"""
        return (self.hunger + self.energy + self.cleanliness + self.happiness) / 4
    
    def update_evolution_status(self, elapsed_seconds):
        """Check if pet is ready to evolve"""
        current_avg = self.get_stat_average()
        # Normal evolution time (in seconds) defined per rarity in assets
        evolution_time = RARITY_DEFINITIONS[self.rarity]["evolution_time"]

        # FAST_EVOLVE override for testing/DEV shorten required time and lower stat threshold
        fast_flag = os.getenv("FAST_EVOLVE", "0").lower() in ("1", "true", "yes")
        if fast_flag:
            evolution_time = 5  # 5 seconds to evolve for testing
            stat_threshold = 30
        else:
            # Slightly easier require a lower average so evolution occurs sooner
            stat_threshold = 50

        # Make evolution faster across rarities (non-testing) for better responsiveness
        try:
            # reduce evolution times by ~40%
            evolution_time = max(3, int(evolution_time * 0.6))
        except Exception:
            pass

        # Reset timer if stats drop below threshold
        if current_avg < stat_threshold:
            self.evolution_timer = 0
            self.evolution_ready = False
            return

        # Increment timer
        self.evolution_timer += elapsed_seconds

        # Check if the pet is ready to evolve
        if self.stage < 3 and self.evolution_timer >= evolution_time:
            self.evolution_ready = True
            self.determine_evolution_branch()
    
    def determine_evolution_branch(self):
        """Determine which evolution branch to take"""
        highest_stat = max(
            ("hunger", self.hunger),
            ("energy", self.energy),
            ("cleanliness", self.cleanliness),
            ("happiness", self.happiness),
            ("affection", self.affection),
            key=lambda x: x[1]
        )[0]
        
        if highest_stat == "happiness":
            self.evolution_branch = "joy"
        elif highest_stat == "cleanliness":
            self.evolution_branch = "pure"
        elif highest_stat == "hunger" and self.hunger > 80:
            self.evolution_branch = "plush"
        elif highest_stat == "energy":
            self.evolution_branch = "spark"
        elif self.affection > 80:
            self.evolution_branch = "bonded"
        else:
            # Default to joy branch
            self.evolution_branch = "joy"
    
    def evolve(self):
        """Perform evolution"""
        if not self.evolution_ready or self.stage >= 3:
            return False
        
        self.stage += 1
        self.evolution_ready = False
        self.evolution_timer = 0
        
        # Reset stats with bonus
        bonus = 10 if self.stage == 2 else 15
        self.hunger = min(100, self.hunger + bonus)
        self.energy = min(100, self.energy + bonus)
        self.cleanliness = min(100, self.cleanliness + bonus)
        self.happiness = min(100, self.happiness + bonus)
        
        # Update the decay multipliers
        self.decay_multipliers = self.get_decay_multipliers()
        
        return True
    
    def apply_action(self, action_type):
        """Apply effects of player action"""
        self.last_action = action_type
        
        if action_type == "feed":
            self.hunger = min(100, self.hunger + int(25 * self.ACTION_GAIN_MULTIPLIER))
            self.happiness = min(100, self.happiness + int(5 * self.ACTION_GAIN_MULTIPLIER))
            self.cleanliness = max(0, self.cleanliness - int(8 / self.ACTION_GAIN_MULTIPLIER))
            self.affection = min(100, self.affection + int(3 * self.ACTION_GAIN_MULTIPLIER))
        
        elif action_type == "play":
            self.happiness = min(100, self.happiness + int(20 * self.ACTION_GAIN_MULTIPLIER))
            self.energy = max(0, self.energy - int(12 / self.ACTION_GAIN_MULTIPLIER))
            self.affection = min(100, self.affection + int(8 * self.ACTION_GAIN_MULTIPLIER))
        
        elif action_type == "clean":
            self.cleanliness = min(100, self.cleanliness + int(30 * self.ACTION_GAIN_MULTIPLIER))
            self.happiness = min(100, self.happiness + int(10 * self.ACTION_GAIN_MULTIPLIER))
            self.affection = min(100, self.affection + int(5 * self.ACTION_GAIN_MULTIPLIER))
        
        elif action_type == "sleep":
            self.energy = min(100, self.energy + int(40 * self.ACTION_GAIN_MULTIPLIER))
            self.hunger = max(0, self.hunger - int(5 / self.ACTION_GAIN_MULTIPLIER))
            self.affection = min(100, self.affection + int(2 * self.ACTION_GAIN_MULTIPLIER))
        
        elif action_type == "pet":
            self.happiness = min(100, self.happiness + int(8 * self.ACTION_GAIN_MULTIPLIER))
            self.affection = min(100, self.affection + int(10 * self.ACTION_GAIN_MULTIPLIER))
        
        # Update thesatisfaction parameters
        satisfaction_gain = {
            "feed": 5,
            "play": 8,
            "clean": 6,
            "sleep": 4,
            "pet": 7
        }.get(action_type, 3)
        
        self.satisfaction = min(100, self.satisfaction + satisfaction_gain)
        
        # Check if satisfaction reward is due
        if self.satisfaction >= 100:
            self.satisfaction = 0
            return True  # Satisfaction reward earned
        
        return False
    
    def apply_decay(self, elapsed_seconds):
        """Apply natural stat decay"""
        # Base decay rates per minute, scaled to elapsed seconds
        base_decay = {
            "hunger": 3 * elapsed_seconds / 60,
            "energy": 4 * elapsed_seconds / 60,
            "cleanliness": 2 * elapsed_seconds / 60,
            "happiness": 3 * elapsed_seconds / 60,
            "affection": 1 * elapsed_seconds / 60
        }
        # Speed up global decay to make gameplay more responsive and fast paced
        for k in base_decay:
            base_decay[k] *= self.DECAY_SPEED_MULTIPLIER
        
        # Apply personality multipliers
        decay_rates = {
            "hunger": base_decay["hunger"] * self.decay_multipliers["hunger_decay"],
            "energy": base_decay["energy"] * self.decay_multipliers["energy_decay"],
            "cleanliness": base_decay["cleanliness"] * self.decay_multipliers["cleanliness_decay"],
            "happiness": base_decay["happiness"] * self.decay_multipliers["happiness_decay"],
            "affection": base_decay["affection"] * self.decay_multipliers["affection_decay"]
        }
        
        # Apply decay
        self.hunger = max(0, self.hunger - decay_rates["hunger"])
        self.energy = max(0, self.energy - decay_rates["energy"])
        self.cleanliness = max(0, self.cleanliness - decay_rates["cleanliness"])
        self.happiness = max(0, self.happiness - decay_rates["happiness"])
        self.affection = max(0, self.affection - decay_rates["affection"])
        
        # Update evolution status
        self.update_evolution_status(elapsed_seconds)
    
    def get_ascii_art(self, current_theme):
        """Get appropriate ASCII art based on state"""
        now = time.time()
        
        # Blinking (every 3-5 seconds)
        if now - self.last_blink > random.uniform(3, 5):
            self.blink_state = 1 - self.blink_state
            self.last_blink = now
        
        # Handle breathing animation
        if now - self.last_breath > 0.5:  # Update every 0.5 seconds
            self.breath_phase = (self.breath_phase + 0.2) % (2 * math.pi)
            self.last_breath = now
        
        # Determine which art to use
        art_key = "idle"
        if self.last_action == "feed":
            art_key = "eating"
        elif self.last_action == "play":
            art_key = "bouncing" if self.species == "slimey" else "breathing"
        elif self.last_action == "pet" and self.affection > 75:
            art_key = "purring"
        elif self.energy < 30:
            art_key = "sleeping"
        
        # This section is mostly for fallback purposes
        try:
            # If the exact rarity doesn't exist for this species, fall back to any available rarity.
            species_art = PET_ART.get(self.species, {})
            if self.rarity in species_art:
                art_set = species_art[self.rarity]
            else:
                # choose a fallback rarity (prefer common->uncommon->rare order if present)
                fallback = next(iter(species_art.keys()), None)
                if fallback:
                    art_set = species_art[fallback]
                    print(f"Warning: using fallback rarity '{fallback}' for {self.species} (requested '{self.rarity}')")
                else:
                    raise KeyError(f"no art for species {self.species}")
            
            # Stage-specific art for evolution showcase
            if self.stage == 1:
                art_set = art_set["baby"]
            elif self.stage == 2:
                art_set = art_set["child"]
            else:  # stage 3
                art_set = art_set["adult"]
                art_key = self.evolution_branch or "joy"
            
            # Use blink art if needed
            if self.blink_state == 1 and "blink" in art_set:
                lines = art_set["blink"]
            else:
                # Try requested key, then fall back to any available art in this stage
                lines = art_set.get(art_key)
                if lines is None:
                    # pick the first available art variant for this stage
                    try:
                        lines = next(iter(art_set.values()))
                    except StopIteration:
                        raise KeyError(f"no art variants for {self.species}/{self.rarity}/{self.stage}")
            
            # Apply breathing effect
            breath_offset = int(1.5 * (1 + math.sin(self.breath_phase)))
            breathed_lines = []
            
            for line in lines:
                # Don't add breathing effect to lines that are already at max width
                if len(line) + 2 * breath_offset > max(len(l) for l in lines) + 2:
                    breathed_lines.append(line)
                else:
                    breathed_lines.append(" " * breath_offset + line + " " * breath_offset)
            
            # Add Zzz if sleeping
            if self.energy < 30 or art_key == "sleeping":
                return "   Z z z…\n" + "\n".join(breathed_lines)
            
            return "\n".join(breathed_lines)
        except KeyError as e:
            print(f"Missing art for {self.species}/{self.rarity}/stage {self.stage}: {e}")
            return "🐾"
        except Exception as e:
            print(f"Error getting ASCII art: {e}")
            return "🐾"
    
    def get_personality_display(self):
        """Get display string for personality traits"""
        return ", ".join([trait.replace("_", " ").title() for trait in self.personality])
    
    def to_dict(self):
        """Convert pet to dictionary for saving"""
        return {
            "species": self.species,
            "rarity": self.rarity,
            "personality": self.personality,
            "hunger": self.hunger,
            "energy": self.energy,
            "cleanliness": self.cleanliness,
            "happiness": self.happiness,
            "affection": self.affection,
            "satisfaction": self.satisfaction,
            "stage": self.stage,
            "evolution_timer": self.evolution_timer,
            "evolution_ready": self.evolution_ready,
            "evolution_branch": self.evolution_branch,
            "blink_state": self.blink_state,
            "last_blink": self.last_blink,
            "last_breath": getattr(self, "last_breath", time.time()),
            "breath_phase": getattr(self, "breath_phase", 0),
            "last_action": self.last_action
        }
    
    def load_from_data(self, data):
        """Load pet from dictionary"""
        self.species = data["species"]
        self.rarity = data["rarity"]
        self.personality = data["personality"]
        self.hunger = data["hunger"]
        self.energy = data["energy"]
        self.cleanliness = data["cleanliness"]
        self.happiness = data["happiness"]
        self.affection = data["affection"]
        self.satisfaction = data["satisfaction"]
        self.stage = data["stage"]
        self.evolution_timer = data["evolution_timer"]
        self.evolution_ready = data["evolution_ready"]
        self.evolution_branch = data["evolution_branch"]
        self.blink_state = data.get("blink_state", 0)
        self.last_blink = data.get("last_blink", time.time())
        self.last_breath = data.get("last_breath", time.time())
        self.breath_phase = data.get("breath_phase", 0)
        self.last_action = data.get("last_action", "idle")
        self.decay_multipliers = self.get_decay_multipliers()