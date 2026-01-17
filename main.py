import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import json
import os
import random
from pets import Buddy
from game_state import GameState
import mini_games
from assets import THEMES, RARITY_DEFINITIONS

class MyLittleBuddyApp:
    def __init__(self, root):
        self.root = root
        # Expose app on root so child windows / mini-games can access the game state to avoid complications
        try:
            self.root.app = self
        except Exception:
            pass
        self.root.title("My Little Buddy")
        self.root.geometry("650x750")
        self.root.resizable(False, False)
        
        # Game state
        self.game_state = GameState()
        self.current_pet = None
        self.current_pet_id = None
        self.running = True
        self.action_cooldown = 0
        self.action_cooldowns = {}  # Track individual action cooldowns
        # Accumulator to apply decay in discrete intervals
        self._decay_accum = 0.0

        # Secret dev-mode spacebar counter, press spacebar 8 times to enable 
        self._space_count = 0
        self._last_space_time = 0
        self.dev_mode = False
        
        # UI references
        self.main_frame = None
        self.pet_display = None
        self.currency_label = None
        self.bars = {}
        self.bar_labels = {}
        self.mini_game_instance = None
        
        # Setup UI
        self.setup_styles()
        self.create_menu()

        # Bind key events for secret dev mode
        try:
            self.root.bind("<Key>", self._on_key_press)
        except Exception:
            pass

        # Bind quick action keys: q=feed, w=play, e=clean, r=sleep since some users might not want to use the mouse to click 
        try:
            for key, action in (("q", "feed"), ("w", "play"), ("e", "clean"), ("r", "sleep")):
                self.root.bind(key, lambda ev, a=action: self.perform_action(a))
                # Also bind uppercase
                self.root.bind(key.upper(), lambda ev, a=action: self.perform_action(a))
        except Exception:
            pass
        
        # Show adoption screen after a brief delay to ensure window is ready
        self.root.after(100, self.show_adoption_screen)
        
        # Start game loop
        self.start_game_loop()
    
    def setup_styles(self):
        """Configure Tkinter"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Progress bar styles
        style.configure("Horizontal.TProgressbar", thickness=15, background="#4caf50")
        style.configure("Low.Horizontal.TProgressbar", thickness=15, background="#e74c3c")
        style.configure("Medium.Horizontal.TProgressbar", thickness=15, background="#f39c12")
        style.configure("High.Horizontal.TProgressbar", thickness=15, background="#2ecc71")
    
    def create_menu(self):
        """Create application menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Buddy menu
        buddy_menu = tk.Menu(menubar, tearoff=0)
        self.buddy_menu = buddy_menu
        buddy_menu.add_command(label="Adopt New Buddy", command=self.show_adoption_screen)
        buddy_menu.add_command(label="Switch Buddy", command=self.switch_pet)
        buddy_menu.add_command(label="Save Game", command=self.save_game)
        menubar.add_cascade(label="Buddy", menu=buddy_menu)
        
        # Shop menu
        shop_menu = tk.Menu(menubar, tearoff=0)
        self.shop_menu = shop_menu
        shop_menu.add_command(label="Buy Gacha Roll (50 💰)", command=self.buy_gacha_roll)
        shop_menu.add_command(label="Achievements", command=self.view_achievements)
        menubar.add_cascade(label="Shop", menu=shop_menu)
        
        # Games menu
        games_menu = tk.Menu(menubar, tearoff=0)
        self.games_menu = games_menu
        games_menu.add_command(label="Bubble Pop", command=self.start_bubble_pop)
        menubar.add_cascade(label="Mini-Games", menu=games_menu)
        
        # Theme menu
        theme_menu = tk.Menu(menubar, tearoff=0)
        self.theme_menu = theme_menu
        # Populate via helper so it can be refreshed later
        self.update_theme_menu()
        menubar.add_cascade(label="Themes", menu=theme_menu)

    def update_theme_menu(self):
        """Rebuild the Themes menu entries based on unlocked themes"""
        try:
            if not hasattr(self, 'theme_menu') or not self.theme_menu:
                return
            # Clear any existing entries
            try:
                self.theme_menu.delete(0, 'end')
            except Exception:
                pass

            unlocked = getattr(self.game_state, "unlocked_themes", ["forest"]) if self.game_state else ["forest"]
            for theme in THEMES.keys():
                label = f"{theme.title()} Theme"
                state = "normal" if theme in unlocked else "disabled"
                if theme in unlocked:
                    label += " (Unlocked)"
                else:
                    # Show which achievement unlocks this theme if available
                    try:
                        aid = getattr(self.game_state, 'THEME_REQUIREMENTS', {}).get(theme)
                        if aid:
                            req_title = self.game_state.ACHIEVEMENT_DEFS.get(aid, {}).get('title', aid)
                            label += f" (Locked: {req_title})"
                        else:
                            # Fall back to theme metadata from assets
                            cond = THEMES.get(theme, {}).get('unlock_condition')
                            if cond:
                                label += f" (Locked: {cond})"
                    except Exception:
                        pass
                try:
                    self.theme_menu.add_command(label=label, command=lambda t=theme: self.change_theme(t), state=state)
                except Exception:
                    # Fallback: add without state
                    self.theme_menu.add_command(label=label, command=lambda t=theme: self.change_theme(t))
        except Exception:
            pass
    
    def change_theme(self, theme_name):
        """Change application theme"""
        if theme_name not in getattr(self.game_state, "unlocked_themes", ["forest"]):
            messagebox.showinfo("🔒 Theme Locked", f"You need to unlock the {theme_name.title()} theme first!")
            return
        
        self.game_state.current_theme = theme_name
        theme = THEMES[theme_name]
        
        # Update window background
        self.root.configure(bg=theme["bg"])
        
        # Update menu colors
        style = ttk.Style()
        style.configure("Horizontal.TProgressbar", background=theme["button_bg"])
        style.configure("Low.Horizontal.TProgressbar", background="#e74c3c")
        style.configure("Medium.Horizontal.TProgressbar", background="#f39c12")
        style.configure("High.Horizontal.TProgressbar", background="#2ecc71")
        
        # Refresh UI
        if self.main_frame and self.main_frame.winfo_exists():
            self.refresh_ui()
    
    def show_adoption_screen(self):
        """Show gacha adoption screen"""
        # Prevent reopening if adoption screen is already visible
        if hasattr(self, 'adoption_frame') and self.adoption_frame and getattr(self.adoption_frame, 'winfo_exists', lambda: False)():
            return
        # Clean up existing UI
        if self.main_frame and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        if self.mini_game_instance:
            try:
                self.mini_game_instance.on_close()
            except:
                pass

        # ONLY CHECK rolls, DO NOT CONSUME ANY ROLLS 
        if not self.game_state.has_gacha_roll():
            messagebox.showwarning(
                "🎟️ No Rolls!",
                f"You need 50 Buddy Bucks!\nYou have: {self.game_state.buddy_bucks} 💰"
            )
            return

        adoption_frame = tk.Frame(self.root, bg=THEMES[self.game_state.current_theme]["bg"])
        adoption_frame.pack(expand=True, fill="both")

        # Disable the Adopt menu item while on the adoption screen
        try:
            if hasattr(self, 'buddy_menu'):
                self.buddy_menu.entryconfig("Adopt New Buddy", state="disabled")
        except Exception:
            pass
        # Remember adoption frame for re-entrancy checks
        self.adoption_frame = adoption_frame

        tk.Label(adoption_frame, text="✨ Adopt Your Little Buddy! ✨", 
                 font=("Comic Sans MS", 20, "bold"),
                 bg=THEMES[self.game_state.current_theme]["bg"],
                 fg=THEMES[self.game_state.current_theme]["fg"]).pack(pady=30)

        # Show starting currency
        info_text = f"Starting with {self.game_state.buddy_bucks} 💰 and {self.game_state.gacha_rolls} 🎟️"
        tk.Label(adoption_frame, text=info_text, bg=THEMES[self.game_state.current_theme]["bg"],
                 fg=THEMES[self.game_state.current_theme]["fg"]).pack(pady=5)

        adopt_button = tk.Button(adoption_frame, text="🎲 Gacha Adopt!", 
                                 font=("Courier", 14, "bold"),
                                 bg=THEMES[self.game_state.current_theme]["button_bg"],
                                 width=18, height=2,
                                 command=lambda: self.adopt_new_buddy(adoption_frame, adopt_button))
        adopt_button.pack(pady=30)

        self.adoption_frame = adoption_frame
        self.preview_label = tk.Label(adoption_frame, text="", 
                                      font=("Courier New", 10, "bold"),
                                      bg=THEMES[self.game_state.current_theme]["bg"],
                                      fg=THEMES[self.game_state.current_theme]["fg"])
        self.preview_label.pack(pady=10, padx=20)

        self.name_label = tk.Label(adoption_frame, text="", 
                                   bg=THEMES[self.game_state.current_theme]["bg"],
                                   fg=THEMES[self.game_state.current_theme]["fg"])
        self.name_label.pack()
    
    def adopt_new_buddy(self, adoption_frame, adopt_button):
        """Handle new buddy adoption (preview first, consume on confirm)"""
        adopt_button.config(state="disabled", text="Spinning...")
        self.root.update()
        time.sleep(1.0)

        # CREATE PET (NO ROLL CONSUMED YET)
        self.current_pet = Buddy()
        self.current_pet_id = f"{self.current_pet.species}_{int(time.time())}"

        # SHOW PREVIEW
        art = self.current_pet.get_ascii_art(self.game_state.current_theme)
        self.preview_label.config(text=art)

        rarity_color = RARITY_DEFINITIONS[self.current_pet.rarity]["color"]
        self.name_label.config(
            text=f"{self.current_pet.species.title()} ({self.current_pet.rarity.title()})\n"
                 f"Personality: {self.current_pet.get_personality_display()}",
            fg=rarity_color
        )

        # ONLY CONSUME ROLL WHEN PLAYER CONFIRMS
        def confirm_adoption():
            if self.game_state.use_gacha_roll():  # ← CONSUMPTION HAPPENS HERE
                self.game_state.add_pet_to_collection(self.current_pet_id)
                self.game_state.save_pet(self.current_pet_id, self.current_pet)
                self.start_main_ui(adoption_frame)
            else:
                messagebox.showerror("🎫 Roll Failed!", "Not enough resources!")

        def cancel_adoption():
            # Return to main UI without consuming roll
            self.start_main_ui(adoption_frame)

        # Present only Keep (confirm)
        tk.Button(adoption_frame, text="❤️ Keep This Buddy!", 
                  command=confirm_adoption).pack(pady=15)
    
    def start_main_ui(self, old_frame):
        """Initialize main game UI"""
        old_frame.destroy()
        self.setup_main_ui()
    
    def setup_main_ui(self):
        """Create main game interface"""
        theme = THEMES[self.game_state.current_theme]
        
        # Main frame
        self.main_frame = tk.Frame(self.root, bg=theme["bg"])
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Currency display
        currency_frame = tk.Frame(self.main_frame, bg=theme["bg"])
        currency_frame.pack(fill="x", pady=5)
        
        self.currency_label = tk.Label(
            currency_frame,
            text=f"💰 {self.game_state.buddy_bucks} | 🎟️ {self.game_state.gacha_rolls}",
            font=("Comic Sans MS", 12, "bold"),
            bg=theme["bg"],
            fg=theme["fg"]
        )
        self.currency_label.pack(side="left", padx=10)
        # Dev mode badge (non-intrusive)
        self.dev_badge = tk.Label(
            currency_frame,
            text="",
            font=("Comic Sans MS", 10, "bold"),
            bg=theme["bg"],
            fg="#ffcc00"
        )
        self.dev_badge.pack(side="right", padx=10)
        
        # Pet display
        self.pet_display = tk.Label(
            self.main_frame,
            text="",
            font=("Courier New", 10, "bold"),
            bg=theme["bg"],
            fg=theme["fg"],
            justify="center",
            cursor="heart"
        )
        self.pet_display.pack(pady=10, padx=20)
        self.pet_display.bind("<Button-1>", self.pet_the_pet)
        
        # Info panel
        info_frame = tk.Frame(self.main_frame, bg=theme["bg"])
        info_frame.pack(fill="x", pady=5)
        
        # Pet name and stage
        name_text = f"{self.current_pet.species.title()} - Stage {self.current_pet.stage}"
        if self.current_pet.stage == 3:
            name_text += f" ({self.current_pet.evolution_branch.title()})"
        
        tk.Label(
            info_frame,
            text=name_text,
            font=("Comic Sans MS", 14, "bold"),
            bg=theme["bg"],
            fg=theme["fg"]
        ).pack(side="left")
        
        # Satisfaction meter
        sat_frame = tk.Frame(info_frame, bg=theme["bg"])
        sat_frame.pack(side="right", padx=10)
        
        tk.Label(
            sat_frame,
            text="Satisfaction:",
            bg=theme["bg"],
            fg=theme["fg"]
        ).pack(side="left")
        
        self.satisfaction_bar = ttk.Progressbar(
            sat_frame,
            length=100,
            maximum=100,
            value=self.current_pet.satisfaction,
            style="Horizontal.TProgressbar"
        )
        self.satisfaction_bar.pack(side="left", padx=5)
        
        # Status bars
        self.bar_frame = tk.Frame(self.main_frame, bg=theme["bg"])
        self.bar_frame.pack(pady=10, fill="x")
        
        # Stats to display, emojis here because I do not want to draw any illustrations for them
        stats = [
            ("hunger", "🍗 Hunger"),
            ("energy", "⚡ Energy"),
            ("cleanliness", "🚿 Cleanliness"),
            ("happiness", "😊 Happiness"),
            ("affection", "❤️ Affection")
        ]
        
        self.bars = {}
        for stat, label in stats:
            frame = tk.Frame(self.bar_frame, bg=theme["bg"])
            frame.pack(fill="x", pady=2)
            
            tk.Label(
                frame,
                text=label,
                width=15,
                anchor="w",
                bg=theme["bg"],
                fg=theme["fg"]
            ).pack(side="left")
            
            value = getattr(self.current_pet, stat)
            bar = ttk.Progressbar(
                frame,
                length=350,
                maximum=100,
                value=value,
                style=self.get_bar_style(value)
            )
            bar.pack(side="left", fill="x", expand=True)
            self.bars[stat] = bar
            
            # Value label
            value_label = tk.Label(
                frame,
                text=f"{value:.1f}",
                width=6,
                bg=theme["bg"],
                fg=theme["fg"]
            )
            value_label.pack(side="right")
            self.bar_labels[stat] = value_label
        
        # Action buttons with emojis because illustrations are just not worth the time to make 
        btn_frame = tk.Frame(self.main_frame, bg=theme["bg"])
        btn_frame.pack(pady=15)
        
        actions = [
            ("🍗 Feed", "feed"),
            ("🎮 Play", "play"),
            ("🚿 Clean", "clean"),
            ("😴 Sleep", "sleep")
        ]
        
        for text, action in actions:
            btn = tk.Button(
                btn_frame,
                text=text,
                font=("Comic Sans MS", 10, "bold"),
                bg=theme["button_bg"],
                width=10,
                command=lambda a=action: self.perform_action(a)
            )
            btn.pack(side="left", padx=5)
            self.action_cooldowns[action] = 0  # Initialize cooldown
        
        # Initial pet display
        self.update_pet_display()
        # Update dev badge if needed
        try:
            self._update_dev_badge()
        except Exception:
            pass
        # Reenable Adopt menu item when returning to main UI
        try:
            if hasattr(self, 'buddy_menu'):
                self.buddy_menu.entryconfig("Adopt New Buddy", state="normal")
        except Exception:
            pass

    def _update_dev_badge(self):
        """Show/hide a small dev-mode badge in the UI."""
        try:
            if getattr(self, 'dev_mode', False):
                if hasattr(self, 'dev_badge') and self.dev_badge:
                    self.dev_badge.config(text='🔧 DEV MODE')
            else:
                if hasattr(self, 'dev_badge') and self.dev_badge:
                    self.dev_badge.config(text='')
        except Exception:
            pass
    
    def refresh_ui(self):
        """Refresh UI with the current theme"""
        if self.main_frame and self.main_frame.winfo_exists():
            self.main_frame.destroy()
        self.setup_main_ui()
    
    def update_currency_display(self):
        """Update the currency display"""
        if self.currency_label and self.currency_label.winfo_exists():
            self.currency_label.config(
                text=f"💰 {self.game_state.buddy_bucks} | 🎟️ {self.game_state.gacha_rolls}"
            )
    
    def update_bars(self):
        """Update status bars"""
        if not self.current_pet:
            return
            
        # Iterate over a snapshot of items to allow safe skips and removals
        for stat, bar in list(self.bars.items()):
            try:
                # Skip if the widget was destroyed
                if not bar or not getattr(bar, 'winfo_exists', lambda: False)():
                    continue

                value = getattr(self.current_pet, stat)
                # Only update existing widgets
                try:
                    bar['value'] = value
                    bar.config(style=self.get_bar_style(value))
                except Exception:
                    # If the underlying tk widget is gone, skip
                    continue

                # Update satisfaction bar when updating happiness
                if stat == "happiness":
                    try:
                        if getattr(self, 'satisfaction_bar', None) and getattr(self.satisfaction_bar, 'winfo_exists', lambda: False)():
                            self.satisfaction_bar['value'] = self.current_pet.satisfaction
                    except Exception:
                        pass

                # Update label 
                lbl = self.bar_labels.get(stat)
                if lbl and getattr(lbl, 'winfo_exists', lambda: False)():
                    try:
                        lbl.config(text=f"{value:.1f}")
                    except Exception:
                        pass
            except Exception:
                # Protect the UI update loop (error handling)
                continue
    
    def update_pet_display(self):
        """Update pet display with ASCII art"""
        if not self.current_pet or not self.pet_display:
            return
            
        art = self.current_pet.get_ascii_art(self.game_state.current_theme)
        self.pet_display.config(text=art)
    
    def get_bar_style(self, value):
        """Get progress bar style based on value"""
        if value < 30:
            return "Low.Horizontal.TProgressbar"
        elif value < 60:
            return "Medium.Horizontal.TProgressbar"
        else:
            return "High.Horizontal.TProgressbar"
    
    def pet_the_pet(self, event=None):
        """Handle pet interaction"""
        if not self.current_pet or self.action_cooldowns.get("pet", 0) > 0:
            return
        
        # Apply action
        satisfaction_reward = self.current_pet.apply_action("pet")
        
        # Show heart effect
        self.show_emoji_feedback("💖")
        
        # Handle rewards
        if satisfaction_reward:
            bucks = self.game_state.award_satisfaction()
            self.show_emoji_feedback(f"+{bucks}💰", duration=1500)
        
        # Update UI
        self.update_bars()
        self.update_pet_display()
        
        # Set cooldown
        self.action_cooldowns["pet"] = 5
    
    def perform_action(self, action_type):
        """Perform a care action"""
        if not self.current_pet or self.action_cooldowns.get(action_type, 0) > 0:
            return
        
        # Get daily bonus
        daily_bonus = self.game_state.get_daily_bonus()
        if daily_bonus > 0:
            self.show_emoji_feedback(f"+{daily_bonus}💰", duration=1200)
        
        # Apply action
        satisfaction_reward = self.current_pet.apply_action(action_type)
        
        # Handle satisfaction reward
        if satisfaction_reward:
            bucks = self.game_state.award_satisfaction()
            self.show_emoji_feedback(f"+{bucks}💰", duration=1500)
        
        # Check for evolution
        if self.current_pet.evolution_ready:
            if messagebox.askyesno("🌟 Evolution Ready!", 
                                  f"Your {self.current_pet.species} is ready to evolve!\n"
                                  f"Earn 100 💰 and unlock new form.\n\n"
                                  f"Evolve now?"):
                    if self.current_pet.evolve():
                        bucks = self.game_state.award_evolution()
                        # Persist pet immediately after evolution
                        if self.current_pet_id:
                            self.game_state.save_pet(self.current_pet_id, self.current_pet)
                        self.show_emoji_feedback("🌟✨", duration=1500)
                        # Standard evolution message
                        messagebox.showinfo("🎉 Evolution Complete!", 
                                            f"{self.current_pet.species.title()} evolved to Stage {self.current_pet.stage}!\n"
                                            f"+{bucks} Buddy Bucks!")
                        # Special notification when pet reaches max stage
                        if self.current_pet.stage >= 3:
                            messagebox.showinfo("🏆 Max Evolution!", 
                                                f"Your {self.current_pet.species.title()} has reached its final form! Congratulations!")
                        # Refresh main UI so labels (name/stage) reflect new stage/art
                        if self.main_frame and self.main_frame.winfo_exists():
                            self.refresh_ui()
        
        # Update UI
        self.update_bars()
        self.update_pet_display()
        self.update_currency_display()
        
        # Set cooldown (different for each action)
        cooldowns = {
            "feed": 5,
            "play": 8,
            "clean": 10,
            "sleep": 15
        }
        self.action_cooldowns[action_type] = cooldowns.get(action_type, 5)
    
    def show_emoji_feedback(self, emoji, duration=800):
        """Show temporary emoji feedback"""
        if hasattr(self, '_feedback_label') and self._feedback_label.winfo_exists():
            self._feedback_label.destroy()
        
        try:
            label = tk.Label(
                self.pet_display, 
                text=emoji, 
                font=("Comic Sans MS", 20, "bold"),
                fg="#ff69b4",
                bg=THEMES[self.game_state.current_theme]["bg"]
            )
            label.place(relx=0.5, rely=0.0, anchor="n")
            self._feedback_label = label
            
            def remove_feedback():
                if hasattr(self, '_feedback_label') and self._feedback_label.winfo_exists():
                    self._feedback_label.destroy()
            
            self.root.after(duration, remove_feedback)
        except:
            pass

    def show_claim_animation(self, amount):
        """Show a small floating +X💰 animation near the currency label."""
        try:
            if not hasattr(self, 'currency_label') or not self.currency_label:
                return

            # Create floating label relative to currency_label
            parent = self.currency_label
            x = parent.winfo_rootx() - self.root.winfo_rootx()
            y = parent.winfo_rooty() - self.root.winfo_rooty()

            lab = tk.Label(self.root, text=f"+{amount}💰", font=("Comic Sans MS", 14, "bold"), fg="#ffd700", bg=THEMES[self.game_state.current_theme]["bg"])
            lab.place(x=x + 60, y=y)

            # Animate upward movement and fade (simple)
            steps = 18
            def animate(step=0):
                try:
                    if step >= steps:
                        lab.destroy()
                        return
                    lab.place_configure(y=y - (step * 4))
                    # slight scale effect via font size tweaks (coarse)
                    self.root.after(30, lambda: animate(step + 1))
                except:
                    try:
                        lab.destroy()
                    except:
                        pass

            animate()
        except Exception:
            pass
    
    def game_loop(self):
        """Main game loop for stat decay and updates"""
        last_update = time.time()
        
        while self.running:
            current_time = time.time()
            elapsed = current_time - last_update
            last_update = current_time
            
            # Update cooldowns
            for action in self.action_cooldowns:
                if self.action_cooldowns[action] > 0:
                    self.action_cooldowns[action] -= elapsed
            
            # Apply stat decay if pet exists which it should 
            if self.current_pet:
                # Check if we're at night for theme unlock, not sure if it would work for vercel uploads
                current_hour = time.localtime().tm_hour
                if current_hour >= 22 and not self.game_state.achievements["night_play"]:
                    self.game_state.achievements["night_play"] = True
                    self.game_state.check_theme_unlocks()
                # Accumulate elapsed time and apply decay in 2s steps to keep changes small and discrete
                try:
                    self._decay_accum += elapsed
                    if self._decay_accum >= 2.0:
                        # number of 2-second steps to apply
                        steps = int(self._decay_accum // 2)
                        # apply decay in one call scaled to total seconds for efficiency
                        self.current_pet.apply_decay(steps * 2)
                        self._decay_accum -= steps * 2
                except Exception:
                    # fallback to continuous decay if something goes wrong
                    try:
                        self.current_pet.apply_decay(elapsed)
                    except Exception:
                        pass
                
                # Auto-save pet
                if hasattr(self, 'current_pet_id') and self.current_pet_id:
                    self.game_state.save_pet(self.current_pet_id, self.current_pet)
            
            # Auto-save game state
            self.game_state.save_game()
            
            # Update UI in main thread
            if self.root.winfo_exists():
                self.root.after(0, self.update_ui_from_loop)
            
            # Sleep to prevent 100% CPU usage
            time.sleep(0.1)
    
    def update_ui_from_loop(self):
        """Update UI from game loop"""
        if self.current_pet and self.pet_display and self.pet_display.winfo_exists():
            self.update_bars()
            self.update_pet_display()
    
    def start_game_loop(self):
        thread = threading.Thread(target=self.game_loop, daemon=True)
        thread.start()
    
    def start_bubble_pop(self):
        """Start bubble pop mini-game"""
        if not self.current_pet:
            messagebox.showwarning("⚠️ No Buddy", "You need to adopt a buddy first!")
            return
        
        if self.mini_game_instance:
            try:
                if self.mini_game_instance.window.winfo_exists():
                    self.mini_game_instance.window.lift()
                    return
            except:
                pass
        
        def update_callback():
            self.update_bars()
            self.update_pet_display()
        
        def earn_bucks_callback(amount):
            # Record achievement progress for bubble pop
            unlocked = False
            try:
                unlocked = self.game_state.record_bubble_earn(amount)
            except Exception:
                pass

            # Apply bucks (record_bubble_earn may already add reward money)
            # Use earn_bucks to keep centralized behavior
            try:
                self.game_state.earn_bucks(amount)
            except Exception:
                # Fallback direct credit
                self.game_state.buddy_bucks += amount

            self.update_currency_display()

            # If achievement unlocked, show a small non-intrusive popup
            if unlocked:
                try:
                    messagebox.showinfo("Achievement Unlocked!", "Bubble Master! You've earned bonus Buddy Bucks for popping bubbles.")
                except Exception:
                    pass

            return amount
        
        self.mini_game_instance = mini_games.BubblePopGame(
            self.root,
            self.current_pet,
            update_callback,
            earn_bucks_callback
        )
        # Disable games menu while a mini-game is active
        try:
            if hasattr(self, 'games_menu'):
                self.games_menu.entryconfig("Bubble Pop", state="disabled")
        except Exception:
            pass
        # Start watcher to re-enable when window closed
        self.root.after(500, self._watch_mini_game)
    
    
    #The memory match game is defunct and will be removed in future updates.
    def start_memory_match(self):
        """Start memory match mini-game"""
        if not self.current_pet:
            messagebox.showwarning("No Buddy", "You need to adopt a buddy first!")
            return
        
        if self.mini_game_instance:
            try:
                if self.mini_game_instance.window.winfo_exists():
                    self.mini_game_instance.window.lift()
                    return
            except:
                pass
        
        def update_callback():
            self.update_bars()
            self.update_pet_display()
        
        def earn_bucks_callback(amount):
            self.game_state.buddy_bucks += amount
            self.update_currency_display()
            try:
                self.game_state.force_save()
            except Exception:
                self.game_state.save_game()
        
        self.mini_game_instance = mini_games.MemoryMatchGame(
            self.root,
            self.current_pet,
            update_callback,
            earn_bucks_callback
        )
        # Disable games menu while a mini-game is active
        try:
            if hasattr(self, 'games_menu'):
                self.games_menu.entryconfig("Bubble Pop", state="disabled")
        except Exception:
            pass
        # Start watcher to re-enable when window closed
        self.root.after(500, self._watch_mini_game)
    
    def buy_gacha_roll(self):
        """Buy additional gacha roll"""
        if self.game_state.buddy_bucks >= 50:
            self.game_state.buddy_bucks -= 50
            self.game_state.gacha_rolls += 1
            self.update_currency_display()
            messagebox.showinfo("🛒 Purchased!", f"You got 1 Gacha Roll!\nTotal rolls: {self.game_state.gacha_rolls}")
        else:
            messagebox.showerror("❌ Not Enough", f"Need 50 💰\nYou have: {self.game_state.buddy_bucks}")
    
    def switch_pet(self):
        """Switch between owned pets"""
        if not self.game_state.pet_collection:
            messagebox.showinfo("EmptyEntries", "No buddies in your collection!")
            return
        
        # Create a selection window
        top = tk.Toplevel(self.root)
        top.title("Choose Your Buddy")
        top.geometry("350x400")
        top.configure(bg=THEMES[self.game_state.current_theme]["bg"])
        # Disable the menu entry while this window is open
        try:
            if hasattr(self, 'buddy_menu'):
                self.buddy_menu.entryconfig("Switch Buddy", state="disabled")
        except Exception:
            pass
        self.switch_window = top
        def _on_switch_close():
            try:
                if hasattr(self, 'buddy_menu'):
                    self.buddy_menu.entryconfig("Switch Buddy", state="normal")
            except Exception:
                pass
            try:
                top.destroy()
            except Exception:
                pass
        top.protocol("WM_DELETE_WINDOW", _on_switch_close)
        
        tk.Label(
            top,
            text="Select a Buddy:",
            font=("Comic Sans MS", 12, "bold"),
            bg=THEMES[self.game_state.current_theme]["bg"],
            fg=THEMES[self.game_state.current_theme]["fg"]
        ).pack(pady=10)
        
        # Create a scrollable frame
        canvas = tk.Canvas(top, bg=THEMES[self.game_state.current_theme]["bg"])
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=THEMES[self.game_state.current_theme]["bg"])
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Add pet options
        for pet_id in self.game_state.pet_collection:
            pet = self.game_state.load_pet(pet_id)
            if not pet:
                continue
            
            frame = tk.Frame(scroll_frame, bg=THEMES[self.game_state.current_theme]["bg"])
            frame.pack(fill="x", padx=5, pady=2)
            
            # Pet info
            info = f"{pet.species.title()} (Stage {pet.stage})"
            if pet.stage == 3:
                info += f" - {pet.evolution_branch.title()}"
            if "legendary" in pet.rarity:
                info += " ✨"
            
            tk.Label(
                frame,
                text=info,
                bg=THEMES[self.game_state.current_theme]["bg"],
                fg=RARITY_DEFINITIONS[pet.rarity]["color"],
                font=("Comic Sans MS", 10)
            ).pack(side="left", padx=5)
            
            # Select button
            tk.Button(
                frame,
                text="Select",
                command=lambda p=pet_id, w=top: self.select_pet(p, w),
                bg="#90ee90",
                font=("Comic Sans MS", 9)
            ).pack(side="right", padx=5)
    
    def select_pet(self, pet_id, window):
        """Switch to selected pet"""
        pet = self.game_state.load_pet(pet_id)
        if pet:
            self.current_pet = pet
            self.current_pet_id = pet_id
            
            if self.main_frame and self.main_frame.winfo_exists():
                self.main_frame.destroy()
            
            self.setup_main_ui()
        try:
            window.destroy()
        except Exception:
            pass
        # Ensure menu re-enabled
        try:
            if hasattr(self, 'buddy_menu'):
                self.buddy_menu.entryconfig("Switch Buddy", state="normal")
        except Exception:
            pass
    
    def view_collection(self):
        """View pet collection"""
        if not self.game_state.pet_collection:
            messagebox.showinfo("EmptyEntries", "Your collection is empty!")
            return
        # Prevent opening multiple collection windows
        if hasattr(self, 'collection_window') and self.collection_window and getattr(self.collection_window, 'winfo_exists', lambda: False)():
            return

        top = tk.Toplevel(self.root)
        top.title("My Collection")
        top.geometry("350x400")
        top.configure(bg=THEMES[self.game_state.current_theme]["bg"])
        # Disable menu entry while open
        try:
            if hasattr(self, 'shop_menu'):
                self.shop_menu.entryconfig("Collection", state="disabled")
        except Exception:
            pass
        self.collection_window = top
        def _on_collection_close():
            try:
                if hasattr(self, 'shop_menu'):
                    self.shop_menu.entryconfig("Collection", state="normal")
            except Exception:
                pass
            try:
                top.destroy()
            except Exception:
                pass
        top.protocol("WM_DELETE_WINDOW", _on_collection_close)

    def view_achievements(self):
        """Show achievements and currency rewards"""
        # Prevent multiple windows
        if hasattr(self, 'achievements_window') and self.achievements_window and getattr(self.achievements_window, 'winfo_exists', lambda: False)():
            return

        top = tk.Toplevel(self.root)
        top.title("Achievements")
        top.geometry("720x560")
        top.configure(bg=THEMES[self.game_state.current_theme]["bg"])

        # Disable menu entry while open
        try:
            if hasattr(self, 'shop_menu'):
                self.shop_menu.entryconfig("Achievements", state="disabled")
        except Exception:
            pass

        self.achievements_window = top

        def _on_ach_close():
            try:
                if hasattr(self, 'shop_menu'):
                    self.shop_menu.entryconfig("Achievements", state="normal")
            except Exception:
                pass
            try:
                top.destroy()
            except Exception:
                pass

        top.protocol("WM_DELETE_WINDOW", _on_ach_close)

        tk.Label(
            top,
            text="Achievements",
            font=("Comic Sans MS", 16, "bold"),
            bg=THEMES[self.game_state.current_theme]["bg"],
            fg=THEMES[self.game_state.current_theme]["fg"]
        ).pack(pady=8)

        # Scrollable frame for achievements
        canvas = tk.Canvas(top, bg=THEMES[self.game_state.current_theme]["bg"], highlightthickness=0)
        frame = tk.Frame(canvas, bg=THEMES[self.game_state.current_theme]["bg"])
        scroll = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.create_window((0,0), window=frame, anchor="nw")

        def on_config(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        frame.bind("<Configure>", on_config)
        canvas.pack(side="left", fill="both", expand=True, padx=8, pady=6)
        scroll.pack(side="right", fill="y")

        # Use GameState definitions to render achievements and claim actions
        for aid, meta in getattr(self.game_state, 'ACHIEVEMENT_DEFS', {}).items():
            state = self.game_state.achievement_state.get(aid, {"unlocked": False, "claimed": False})
            unlocked = bool(state.get("unlocked", False))
            claimed = bool(state.get("claimed", False))
            metric = meta.get("metric")
            threshold = meta.get("threshold")
            current = self.game_state.achievements.get(metric, 0)

            # Card container
            card = tk.Frame(frame, bg=THEMES[self.game_state.current_theme]["bg"], relief="groove", bd=1)
            card.pack(fill="x", pady=8, padx=6)

            left = tk.Frame(card, bg=THEMES[self.game_state.current_theme]["bg"])
            left.pack(side="left", fill="both", expand=True, padx=8, pady=6)

            tk.Label(left, text=meta.get("title", aid), font=("Comic Sans MS", 12, "bold"), bg=THEMES[self.game_state.current_theme]["bg"], fg=THEMES[self.game_state.current_theme]["fg"]).pack(anchor="w")
            tk.Label(left, text=meta.get("desc", ""), font=("Comic Sans MS", 9), bg=THEMES[self.game_state.current_theme]["bg"], fg="#666").pack(anchor="w", pady=(2,6))

            # Progress bar
            try:
                pb_max = threshold if isinstance(threshold, (int, float)) and threshold > 0 else 1
                pb_val = float(current) if isinstance(current, (int, float)) else (1.0 if bool(current) else 0.0)
                pb = ttk.Progressbar(left, length=260, maximum=pb_max, value=min(pb_val, pb_max), style="Horizontal.TProgressbar")
                pb.pack(anchor="w", pady=(0,4))
                prog_text = f"{int(pb_val)}/{int(pb_max)}" if isinstance(pb_val, (int, float)) else str(pb_val)
                tk.Label(left, text=prog_text, font=("Comic Sans MS", 9, "italic"), bg=THEMES[self.game_state.current_theme]["bg"], fg="#888").pack(anchor="w")
            except Exception:
                pass

            right = tk.Frame(card, bg=THEMES[self.game_state.current_theme]["bg"])
            right.pack(side="right", padx=8, pady=6)

            tk.Label(right, text=f"Reward:\n{meta.get('reward')}", font=("Comic Sans MS", 10), bg=THEMES[self.game_state.current_theme]["bg"], fg="#2c3e50").pack()

            # Claim button if unlocked and not yet claimed
            if unlocked and not claimed:
                def make_claim(aid_local):
                    def _claim():
                        reward = self.game_state.claim_achievement(aid_local)
                        if reward is not None:
                            try:
                                self.show_claim_animation(reward)
                            except:
                                pass
                            self.update_currency_display()
                            try:
                                messagebox.showinfo("Claimed!", f"You claimed {reward} 💰 from achievement.")
                            except:
                                pass
                            # Refresh achievements window and theme menu
                            try:
                                top.destroy()
                                self.update_theme_menu()
                                self.view_achievements()
                            except:
                                pass
                        else:
                            try:
                                messagebox.showwarning("Cannot Claim", "Achievement cannot be claimed.")
                            except:
                                pass
                    return _claim

                tk.Button(right, text="Claim", command=make_claim(aid), bg="#90ee90").pack(pady=6)
            elif claimed:
                tk.Label(right, text="Claimed", font=("Comic Sans MS", 10, "italic"), bg=THEMES[self.game_state.current_theme]["bg"], fg="#4caf50").pack(pady=10)

        tk.Button(top, text="Close", command=_on_ach_close, bg="#90ee90").pack(pady=8)
        
        tk.Label(
            top,
            text="My Buddy Collection",
            font=("Comic Sans MS", 14, "bold"),
            bg=THEMES[self.game_state.current_theme]["bg"],
            fg=THEMES[self.game_state.current_theme]["fg"]
        ).pack(pady=10)
        
        # Create scrollable frame
        canvas = tk.Canvas(top, bg=THEMES[self.game_state.current_theme]["bg"])
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=THEMES[self.game_state.current_theme]["bg"])
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # Add pets to collection
        for pet_id in self.game_state.pet_collection:
            pet = self.game_state.load_pet(pet_id)
            if not pet:
                continue
            
            frame = tk.Frame(scroll_frame, bg=THEMES[self.game_state.current_theme]["bg"], pady=5)
            frame.pack(fill="x", padx=5)
            
            # Pet info
            info_frame = tk.Frame(frame, bg=THEMES[self.game_state.current_theme]["bg"])
            info_frame.pack(side="left", fill="x", expand=True)
            
            info = f"{pet.species.title()} - {pet.rarity.title()}"
            tk.Label(
                info_frame,
                text=info,
                font=("Comic Sans MS", 10, "bold"),
                fg=RARITY_DEFINITIONS[pet.rarity]["color"],
                bg=THEMES[self.game_state.current_theme]["bg"]
            ).pack(anchor="w")
            
            details = f"Stage {pet.stage} • {pet.get_personality_display()}"
            tk.Label(
                info_frame,
                text=details,
                font=("Comic Sans MS", 8),
                bg=THEMES[self.game_state.current_theme]["bg"],
                fg=THEMES[self.game_state.current_theme]["fg"]
            ).pack(anchor="w")
            
            # Evolution stars
            if pet.stage >= 2:
                stars = "⭐" * pet.stage
                tk.Label(
                    info_frame,
                    text=stars,
                    font=("Comic Sans MS", 8),
                    fg="#f1c40f",
                    bg=THEMES[self.game_state.current_theme]["bg"]
                ).pack(anchor="w")
    
    def save_game(self):
        """Save current game state"""
        if self.current_pet and self.current_pet_id:
            self.game_state.save_pet(self.current_pet_id, self.current_pet)
        self.game_state.save_game()
        messagebox.showinfo("Saved!", "Game saved successfully!")

    def _watch_mini_game(self):
        """Poll to detect mini-game close and re-enable games menu."""
        try:
            mg = getattr(self, 'mini_game_instance', None)
            if not mg:
                # nothing running; ensure menu entries enabled
                if hasattr(self, 'games_menu'):
                    try:
                            self.games_menu.entryconfig("Bubble Pop", state="normal")
                    except Exception:
                        pass
                return

            win = getattr(mg, 'window', None)
            if not win or not getattr(win, 'winfo_exists', lambda: False)():
                # mini-game closed; clear instance and re-enable menu
                try:
                    self.mini_game_instance = None
                except Exception:
                    pass
                try:
                    if hasattr(self, 'games_menu'):
                        self.games_menu.entryconfig("Bubble Pop", state="normal")
                except Exception:
                    pass
                return
        except Exception:
            pass

        # keep watching
        try:
            self.root.after(500, self._watch_mini_game)
        except Exception:
            pass
    
    def on_closing(self):
        """Handle application closing"""
        self.save_game()
        self.running = False
        
        if self.mini_game_instance:
            try:
                self.mini_game_instance.on_close()
            except:
                pass
        
        try:
            self.root.destroy()
        except:
            pass

    def _on_key_press(self, event):
        """Handle key presses to detect secret dev-mode (8x spacebar)."""
        try:
            if event.keysym == 'space':
                now = time.time()
                # Reset counter if more than 2s between presses to ensure accidental space bar presses do not trigger dev mode 
                if now - self._last_space_time > 2:
                    self._space_count = 0
                self._space_count += 1
                self._last_space_time = now
                if self._space_count >= 8:
                    if not self.dev_mode:
                        self._enable_dev_mode()
                    else:
                        self._disable_dev_mode()
                    self._space_count = 0
            else:
                # Any other key breaks the consecutive chain
                self._space_count = 0
        except Exception:
            pass

    def _enable_dev_mode(self):
        """Enable dev/test mode: turn on FAST_EVOLVE and show feedback."""
        try:
            os.environ['FAST_EVOLVE'] = '1'
            self.dev_mode = True
            # Visible feedback
            try:
                self.show_emoji_feedback('🔧 Dev Mode ON', duration=2000)
            except Exception:
                messagebox.showinfo('Dev Mode', 'Dev mode enabled (FAST_EVOLVE=1)')
        except Exception as e:
            print('Failed to enable dev mode:', e)

    def _disable_dev_mode(self):
        """Disable dev/test mode: turn off FAST_EVOLVE and show feedback."""
        try:
            os.environ['FAST_EVOLVE'] = '0'
            self.dev_mode = False
            try:
                self.show_emoji_feedback('🔧 Dev Mode OFF', duration=2000)
            except Exception:
                messagebox.showinfo('Dev Mode', 'Dev mode disabled')
        except Exception as e:
            print('Failed to disable dev mode:', e)

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap("buddy.ico")
    except:
        pass
    
    app = MyLittleBuddyApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()