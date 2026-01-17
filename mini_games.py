# mini_games.py - Simple mini-games with rewards

import tkinter as tk
from tkinter import messagebox
import random
import time
from assets import BUBBLE_CHAR

class BubblePopGame:
    """
    Simple bubble popping game where players click on floating bubbles.
    Rewards scale with performance where more bubbles popped means more happiness & coins.
    """
    
    def __init__(self, parent_window, buddy, update_callback, earn_bucks_callback):
        self.parent = parent_window
        self.buddy = buddy
        self.update_callback = update_callback
        self.earn_bucks_callback = earn_bucks_callback
        self.score = 0
        self.bubbles = []
        self.running = True
        self.start_time = time.time()
        
        # Creates the game window
        self.window = tk.Toplevel(parent_window)
        self.window.title("🎈 Bubble Pop!")
        self.window.geometry("400x500")
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Set background based on theme
        theme = "forest"
        if hasattr(parent_window, 'app') and hasattr(parent_window.app, 'current_theme'):
            theme = parent_window.app.current_theme
        
        bg_color = "#e6f7ff"  # Default
        if theme == "space":
            bg_color = "#1a1a2e"
        elif theme == "forest":
            bg_color = "#e0f2e0"
        elif theme == "sunset":
            bg_color = "#ffedcc"
        elif theme == "night":
            bg_color = "#2d2d44"
        elif theme == "chromatic":
            bg_color = "#2c2c2c"
        
        self.window.configure(bg=bg_color)
        
        # Create canvas
        self.canvas = tk.Canvas(
            self.window, 
            width=400, 
            height=400, 
            bg=bg_color, 
            highlightthickness=0
        )
        self.canvas.pack(pady=10)
        
        # Score display
        self.score_label = tk.Label(
            self.window, 
            text=f"Score: {self.score}", 
            font=("Comic Sans MS", 14, "bold"),
            bg=bg_color,
            fg="#e74c3c" if theme != "space" else "#ff9ff3"
        )
        self.score_label.pack(pady=5)
        
        # Time remaining
        self.time_label = tk.Label(
            self.window,
            text="Time: 30s",
            font=("Comic Sans MS", 12),
            bg=bg_color,
            fg="#2c3e50" if theme != "space" else "#54a0ff"
        )
        self.time_label.pack(pady=2)
        
        # Bind click event
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Start game loops
        self.create_bubble()
        self.move_bubbles()
        self.update_timer()
    
    def create_bubble(self):
        """Create a new bubble at random position"""
        if not self.running or not self.canvas.winfo_exists():
            return
            
        x = random.randint(30, 370)
        y = 400
        size = random.randint(20, 40)
        
        # Bubble colors based on theme
        theme = "forest"
        if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'current_theme'):
            theme = self.parent.app.current_theme
        
        if theme == "space":
            colors = ["#54a0ff", "#00d2d3", "#00b894"]
        elif theme == "forest":
            colors = ["#00b894", "#00cec9", "#55efc4"]
        elif theme == "sunset":
            colors = ["#ff9ff3", "#ff6b6b", "#ee5253"]
        elif theme == "night":
            colors = ["#54a0ff", "#00d2d3", "#5f27cd"]
        else:  # chromatic or default
            colors = ["#ff9ff3", "#ff6b6b", "#ff9e80"]
        
        color = random.choice(colors)
        
        # Create bubble with glow effect
        glow = self.canvas.create_oval(
            x-size//2-2, y-size//2-2, x+size//2+2, y+size//2+2,
            fill=color,
            outline=color,
            width=2
        )
        bubble = self.canvas.create_oval(
            x-size//2, y-size//2, x+size//2, y+size//2,
            fill="white",
            outline=color,
            width=2
        )
        text = self.canvas.create_text(
            x, y, 
            text=BUBBLE_CHAR, 
            font=("Courier", size//2, "bold"),
            fill=color
        )
        
        self.bubbles.append({
            "glow_id": glow,
            "id": bubble,
            "text_id": text,
            "x": x,
            "y": y,
            "size": size,
            "speed": random.uniform(0.8, 1.5)
        })
        
        # Schedule next bubble
        if len(self.bubbles) < 8:
            self.window.after(600, self.create_bubble)
    
    def move_bubbles(self):
        """Move all bubbles upward"""
        if not self.running or not self.canvas.winfo_exists():
            return
            
        to_remove = []
        
        for bubble in self.bubbles:
            # Move bubble up
            dy = -bubble["speed"] * 3
            self.canvas.move(bubble["glow_id"], 0, dy)
            self.canvas.move(bubble["id"], 0, dy)
            self.canvas.move(bubble["text_id"], 0, dy)
            bubble["y"] += dy
            
            # Remove if off-screen
            if bubble["y"] < -50:
                to_remove.append(bubble)
        
        # Remove off-screen bubbles
        for bubble in to_remove:
            self.canvas.delete(bubble["glow_id"])
            self.canvas.delete(bubble["id"])
            self.canvas.delete(bubble["text_id"])
            self.bubbles.remove(bubble)
        
        # Continue animation
        if self.running:
            self.window.after(30, self.move_bubbles)
    
    def on_click(self, event):
        """Handle bubble popping"""
        if not self.running:
            return
            
        x, y = event.x, event.y
        clicked = False
        
        for bubble in self.bubbles[:]:
            dx = x - bubble["x"]
            dy = y - bubble["y"]
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= bubble["size"]//2:
                # Remove bubble with pop effect
                self.canvas.delete(bubble["glow_id"])
                self.canvas.delete(bubble["id"])
                self.canvas.delete(bubble["text_id"])
                self.bubbles.remove(bubble)
                
                # Update score
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")
                
                # Reward buddy
                happiness_gain = min(25, self.score * 2)  # Cap at 25
                self.buddy.happiness = min(100, self.buddy.happiness + happiness_gain)
                
                clicked = True
                break
        
        if clicked:
            self.update_callback()
    
    def update_timer(self):
        """Update game timer"""
        if not self.running or not self.window.winfo_exists():
            return
        elapsed = time.time() - self.start_time
        remaining_float = 30.0 - elapsed
        remaining = int(max(0, remaining_float))

        # If time has fully elapsed, ensure we call end_game exactly once
        if remaining_float <= 0:
            # Update label to show 0s then end
            try:
                self.time_label.config(text=f"Time: 0s")
            except Exception:
                pass
            self.window.after(100, self.end_game)
            return

        # Otherwise show remaining seconds
        try:
            self.time_label.config(text=f"Time: {remaining}s")
        except Exception:
            pass

        # Schedule next tick (use 250ms for smoother UI)
        self.window.after(250, self.update_timer)
    
    def end_game(self):
        """End the game and award rewards"""
        self.running = False
        
        # Calculate rewards
        happiness_reward = min(25, self.score * 2)
        # Currency reward: half the score
        bucks_reward = max(0, int(self.score / 2))
        
        # Apply rewards
        self.buddy.happiness = min(100, self.buddy.happiness + happiness_reward)
        
        awarded = 0
        if hasattr(self, 'earn_bucks_callback'):
            try:
                awarded = self.earn_bucks_callback(bucks_reward) or bucks_reward
            except Exception:
                # Fallback: assume bucks_reward was applied
                awarded = bucks_reward

        # Show results in a popup and include updated total if available
        total_text = ''
        try:
            if hasattr(self.parent, 'app') and hasattr(self.parent.app, 'game_state'):
                total = self.parent.app.game_state.buddy_bucks
                total_text = f"\nTotal Buddy Bucks: {total}"
        except Exception:
            total_text = ''

        result_text = f"Game Over!\nScore: {self.score}\n+{happiness_reward} Happiness\n+{awarded} 💰 credited to your wallet{total_text}"
        try:
            messagebox.showinfo("Bubble Pop Results", result_text, parent=self.window)
        except Exception:
            # Fallback to inline label if messagebox fails
            tk.Label(
                self.window,
                text=result_text,
                font=("Comic Sans MS", 14, "bold"),
                bg=self.window.cget("bg"),
                fg="#2c3e50"
            ).pack(pady=20)

        tk.Button(
            self.window,
            text="Close",
            command=self.on_close,
            bg="#90ee90",
            font=("Comic Sans MS", 10)
        ).pack(pady=10)

        self.update_callback()
    
    def on_close(self):
        """Handle window close"""
        self.running = False
        if self.window.winfo_exists():
            self.window.destroy()

#There was a memory match game here but I have decided to remove it as it was too easy and not really that challenging 