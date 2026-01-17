import json
import os
import time
from datetime import datetime, date
from pets import Buddy

SAVE_DIR = "saves"
os.makedirs(SAVE_DIR, exist_ok=True)

class GameState:
    def __init__(self):
        self.buddy_bucks = 50  # Starting currency
        self.gacha_rolls = 1    # Starting with 1 free roll
        self.unlocked_themes = ["forest"]  # Default theme for the game
        self.pet_collection = []  # List of pets
        self.last_daily_bonus = None
        self.achievements = {
            "evolved_pets": 0,
            "satisfaction_rewards": 0,
            "legendary_pets": 0,
            "night_play": False
        }

        #  To initialize the minigame parameters 
        self.achievements.setdefault("bubble_pop_total", 0)

        # Achievement definitioons for tracking 
        self.ACHIEVEMENT_DEFS = {
            "bubble_master": {"title": "Bubble Master", "desc": "Earn total coins from Bubble Pop.", "metric": "bubble_pop_total", "threshold": 10, "reward": 20},
            "evolver": {"title": "Evolver", "desc": "Evolve 2 pets.", "metric": "evolved_pets", "threshold": 2, "reward": 100},
            "satisfied": {"title": "Satisfied", "desc": "Earn satisfaction rewards.", "metric": "satisfaction_rewards", "threshold": 10, "reward": 30},
            "legend_collector": {"title": "Legend Collector", "desc": "Obtain a legendary pet.", "metric": "legendary_pets", "threshold": 1, "reward": 0},
            "night_owl": {"title": "Night Owl", "desc": "Played late at night.", "metric": "night_play", "threshold": True, "reward": 0}
        }

        # Small collector achievement: own X pets
        self.ACHIEVEMENT_DEFS.setdefault("collector", {"title": "Collector", "desc": "Own multiple buddies.", "metric": "pet_count", "threshold": 3, "reward": 0})

        # Runtime achievement (unlocked/claimed timestamps)
        self.achievement_state = {}
        for aid in self.ACHIEVEMENT_DEFS.keys():
            self.achievement_state.setdefault(aid, {"unlocked": False, "unlocked_at": None, "claimed": False, "claimed_at": None})

        # Map themes to achievement IDs that unlock them
        self.THEME_REQUIREMENTS = {
            "space": "evolver",
            "sunset": "satisfied",
            "chromatic": "legend_collector",
            "night": "night_owl"
        }
        
        self.current_theme = "forest"
        self.last_save_time = 0
        
        # Load saved game if it exists
        self.load_game()
    
    def load_game(self):
        """Load game state from file"""
        save_path = os.path.join(SAVE_DIR, "game_state.json")
        
        if os.path.exists(save_path):
            try:
                with open(save_path, "r") as f:
                    data = json.load(f)
                
                self.buddy_bucks = data.get("buddy_bucks", 50)
                self.gacha_rolls = data.get("gacha_rolls", 1)
                self.unlocked_themes = data.get("unlocked_themes", ["forest"])
                self.pet_collection = data.get("pet_collection", [])
                self.last_daily_bonus = data.get("last_daily_bonus")
                self.achievements = data.get("achievements", self.achievements)
                # Load achievement live state if present
                self.achievement_state = data.get("achievement_state", self.achievement_state)
                self.current_theme = data.get("current_theme", "forest")
            except Exception as e:
                print(f"Error loading game state: {e}")
        
        # Unlock themes based on achievements
        self.check_achievements()
        self.check_theme_unlocks()
    
    def save_game(self):
        """Save game state to file"""
        # Only save every 60 seconds to avoid excessive writing 
        if time.time() - self.last_save_time < 60:
            return
        
        self.last_save_time = time.time()
        save_path = os.path.join(SAVE_DIR, "game_state.json")
        
        data = {
            "buddy_bucks": self.buddy_bucks,
            "gacha_rolls": self.gacha_rolls,
            "unlocked_themes": self.unlocked_themes,
            "pet_collection": self.pet_collection,
            "last_daily_bonus": self.last_daily_bonus,
            "achievements": self.achievements,
            "achievement_state": self.achievement_state,
            "current_theme": self.current_theme
        }
        
        try:
            with open(save_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving game state: {e}")

    def force_save(self):
        """Forcefully save game state to file, bypassing throttle."""
        self.last_save_time = time.time()
        save_path = os.path.join(SAVE_DIR, "game_state.json")
        data = {
            "buddy_bucks": self.buddy_bucks,
            "gacha_rolls": self.gacha_rolls,
            "unlocked_themes": self.unlocked_themes,
            "pet_collection": self.pet_collection,
            "last_daily_bonus": self.last_daily_bonus,
            "achievements": self.achievements,
            "achievement_state": self.achievement_state,
            "current_theme": self.current_theme
        }
        try:
            with open(save_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error force-saving game state: {e}")
    
    def has_gacha_roll(self):
        """Check if player can adopt a new pet"""
        return self.gacha_rolls > 0 or self.buddy_bucks >= 50
    
    def use_gacha_roll(self):
        """Consume a gacha roll ticket when adopting a pet"""
        if self.gacha_rolls > 0:
            self.gacha_rolls -= 1
            self.save_game()
            return True
        elif self.buddy_bucks >= 50:
            self.buddy_bucks -= 50
            self.save_game()
            return True
        return False
    
    def add_pet_to_collection(self, buddy_id):
        """Add a pet to the collection"""
        if buddy_id not in self.pet_collection:
            self.pet_collection.append(buddy_id)
            # Re-check achievements that depend on pet count
            self.check_achievements()
            self.check_theme_unlocks()
            self.save_game()
    
    def get_daily_bonus(self):
        """Award daily login bonus"""
        today = date.today().isoformat()
        
        if self.last_daily_bonus != today:
            self.last_daily_bonus = today
            self.buddy_bucks += 20
            self.save_game()
            return 20
        return 0
    
    def earn_bucks(self, amount):
        """Add buddy bucks with achievement tracking"""
        self.buddy_bucks += amount
        
        # Check for legendary pet achievement
        if amount >= 100 and "legendary" in self.pet_collection[-1]:
            self.achievements["legendary_pets"] += 1

        # Re-check achievements and theme unlocks
        self.check_achievements()
        self.check_theme_unlocks()
        self.save_game()
        return amount

    def record_bubble_earn(self, amount):
        """Record bubble pop earnings and unlock a small achievement when threshold reached."""
        try:
            total = self.achievements.get("bubble_pop_total", 0) + amount
            self.achievements["bubble_pop_total"] = total

            # Detect if bubble_master was unlocked by this addition
            prev_state = self.achievement_state.get("bubble_master", {"unlocked": False})
            prev_unlocked = bool(prev_state.get("unlocked", False))

            # Re-check achievements (may mark bubble_master unlocked)
            self.check_achievements()

            new_state = self.achievement_state.get("bubble_master", {"unlocked": False})
            new_unlocked = bool(new_state.get("unlocked", False))

            # Persist the progress
            self.save_game()

            # Return True if newly unlocked
            return (not prev_unlocked) and new_unlocked
        except Exception as e:
            print(f"Error recording bubble earnings: {e}")
        return False
    
    def unlock_theme(self, theme_name):
        """Unlock a new theme"""
        if theme_name not in self.unlocked_themes and theme_name in ["space", "sunset", "night", "chromatic"]:
            self.unlocked_themes.append(theme_name)
            self.save_game()
            return True
        return False
    
    def check_theme_unlocks(self):
        """Check and unlock themes based on achievements"""
        # Ensure any time-based flags are captured (night_play)
        current_hour = datetime.now().hour
        if current_hour >= 22:
            self.achievements["night_play"] = True

        # Unlock themes based on achievement_state via THEME_REQUIREMENTS
        for theme, aid in self.THEME_REQUIREMENTS.items():
            state = self.achievement_state.get(aid, {})
            if state.get("unlocked"):
                self.unlock_theme(theme)

    def check_achievements(self):
        """Check all achievement definitions and mark unlocked ones.

        This does not automatically grant the reward so claiming must be done
        via `claim_achievement` to give currency and mark claimed.
        """
        changed = False
        for aid, meta in self.ACHIEVEMENT_DEFS.items():
            metric = meta.get("metric")
            threshold = meta.get("threshold", 0)
            if metric == "pet_count":
                current = len(self.pet_collection)
            else:
                current = self.achievements.get(metric, None)
            state = self.achievement_state.setdefault(aid, {"unlocked": False, "unlocked_at": None, "claimed": False, "claimed_at": None})

            unlocked = False
            # Support for boolean metrics (like night_play)
            if isinstance(current, bool):
                unlocked = bool(current)
            elif isinstance(current, (int, float)) and isinstance(threshold, (int, float)):
                unlocked = (current >= threshold)
            else:
                # Fallback
                unlocked = bool(current)

            if not state.get("unlocked") and unlocked:
                state["unlocked"] = True
                state["unlocked_at"] = time.time()
                changed = True

        if changed:
            # Persist achievement state and unlock themes
            try:
                self.force_save()
            except Exception:
                self.save_game()
            # Unlock any themes that depend on newly unlocked achievements
            try:
                self.check_theme_unlocks()
            except Exception:
                pass

    def claim_achievement(self, aid):
        """Claim an unlocked achievement by id. Returns reward amount or NONE on failure."""
        if aid not in self.ACHIEVEMENT_DEFS:
            return None

        state = self.achievement_state.setdefault(aid, {"unlocked": False, "unlocked_at": None, "claimed": False, "claimed_at": None})
        if not state.get("unlocked") or state.get("claimed"):
            return None

        reward = self.ACHIEVEMENT_DEFS[aid].get("reward", 0)
        try:
            self.buddy_bucks += reward
            state["claimed"] = True
            state["claimed_at"] = time.time()
            # Persist immediately
            self.force_save()
            return reward
        except Exception as e:
            print(f"Error claiming achievement {aid}: {e}")
            return None
    
    def get_pet_save_path(self, pet_id):
        """Get save path for a specific pet"""
        return os.path.join(SAVE_DIR, f"pet_{pet_id}.json")
    
    def save_pet(self, pet_id, buddy):
        """Save individual pet data"""
        save_path = self.get_pet_save_path(pet_id)
        try:
            with open(save_path, "w") as f:
                json.dump({
                    "pet_data": buddy.to_dict(),
                    "last_saved": time.time()
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving pet {pet_id}: {e}")
    
    def load_pet(self, pet_id):
        """Load individual pet data"""
        save_path = self.get_pet_save_path(pet_id)
        
        if not os.path.exists(save_path):
            return None
        
        try:
            with open(save_path, "r") as f:
                data = json.load(f)
            return Buddy(from_data=data["pet_data"])
        except Exception as e:
            print(f"Error loading pet {pet_id}: {e}")
            return None
    
    def award_evolution(self):
        """Award bonuses for evolution"""
        self.buddy_bucks += 100
        self.achievements["evolved_pets"] += 1
        # Check achievements and theme unlocks for awarding evolution
        self.check_achievements()
        self.check_theme_unlocks()
        self.save_game()
        return 100
    
    def award_satisfaction(self):
        """Award bonuses for satisfaction"""
        self.buddy_bucks += 30
        self.achievements["satisfaction_rewards"] += 1
        # Check achievements and theme unlocks for awardiing satisfaction
        self.check_achievements()
        self.check_theme_unlocks()
        self.save_game()
        return 30