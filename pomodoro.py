import tkinter as tk
from tkinter import messagebox
import sqlite3
import time
from datetime import datetime
import threading
import os

class PomodoroApp:
    def __init__(self, root):
        """Initialize the Pomodoro Timer application"""
        # Setup main window
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("500x400")
        self.root.configure(bg="#2A2A3A")  # Dark theme with blue tint
        
        # Timer configuration variables
        self.focus_time = tk.IntVar(value=60)  # Default 25 minutes (standard Pomodoro)
        self.rest_time = tk.IntVar(value=10)    # Default 5 minutes rest
        self.remaining_time = tk.StringVar(value="Ready to start")
        
        # Timer state variables
        self.running = False
        self.is_paused = False
        self.is_resting = False
        self.timer_thread = None
        
        # Setup database and UI components
        self.setup_db()
        self.create_widgets()
    
    def setup_db(self):
        """Create and configure the SQLite database"""
        self.conn = sqlite3.connect("pomodoro_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                                date TEXT,
                                focus_minutes INTEGER)''')
        self.conn.commit()
    
    def create_widgets(self):
        """Create and arrange all UI elements"""
        # Focus time input
        tk.Label(self.root, text="Focus Time (min):", bg="#1E1E2E", fg="#FFD700", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        tk.Entry(self.root, textvariable=self.focus_time, font=("Arial", 14), bg="#2E2E3E", fg="white", width=10).pack()
        
        # Rest time input
        tk.Label(self.root, text="Rest Time (min):", bg="#1E1E2E", fg="#FFD700", font=("Arial", 14, "bold")).pack(pady=(10, 0))
        tk.Entry(self.root, textvariable=self.rest_time, font=("Arial", 14), bg="#2E2E3E", fg="white", width=10).pack()
        
        # Control buttons frame
        button_frame = tk.Frame(self.root, bg="#1E1E2E")
        button_frame.pack(pady=15)
        
        # Start/Pause button
        self.start_button = tk.Button(
            button_frame, 
            text="Start", 
            command=self.toggle_timer, 
            bg="#4CAF50", 
            fg="white", 
            font=("Arial", 14, "bold"),
            width=10
        )
        self.start_button.grid(row=0, column=0, padx=5)
        
        # Stop/Reset button
        self.stop_button = tk.Button(
            button_frame, 
            text="Stop", 
            command=self.stop_timer, 
            bg="#f44336", 
            fg="white", 
            font=("Arial", 14, "bold"),
            width=10
        )
        self.stop_button.grid(row=0, column=1, padx=5)
        
        # History button
        self.history_button = tk.Button(
            self.root, 
            text="Show History", 
            command=self.show_history, 
            bg="#2196F3", 
            fg="white", 
            font=("Arial", 14, "bold")
        )
        self.history_button.pack(pady=5)
        
        # Status display
        self.status_label = tk.Label(
            self.root, 
            text="Ready to start", 
            bg="#1E1E2E", 
            fg="#FFD700", 
            font=("Arial", 16, "bold")
        )
        self.status_label.pack(pady=10)
        
        # Timer display
        self.timer_label = tk.Label(
            self.root, 
            textvariable=self.remaining_time, 
            bg="#1E1E2E", 
            fg="#FFA500", 
            font=("Arial", 24, "bold")
        )
        self.timer_label.pack(pady=10)
    
    def toggle_timer(self):
        """Start, pause or resume the timer"""
        if not self.running:
            # Start or resume timer
            self.running = True
            
            # Set button to pause mode
            self.start_button.config(text="Pause", bg="#FF9800")
            
            if self.is_paused:
                # We're resuming a paused timer
                self.is_paused = False
            else:
                # Starting a new timer
                if not self.timer_thread or not self.timer_thread.is_alive():
                    duration = self.focus_time.get() * 60 if not self.is_resting else self.rest_time.get() * 60
                    self.update_status("Focus Time!" if not self.is_resting else "Break Time!", 
                                    "#FFD700" if not self.is_resting else "#4CAF50")
                    self.timer_thread = threading.Thread(target=self.run_timer, args=(duration,))
                    self.timer_thread.daemon = True  # Thread will terminate when main program ends
                    self.timer_thread.start()
        else:
            # Pause timer
            self.is_paused = True
            self.running = False
            self.start_button.config(text="Resume", bg="#4CAF50")
    
    def stop_timer(self):
        """Stop the timer and reset to initial state"""
        self.running = False
        self.is_paused = False
        self.is_resting = False
        
        # Reset UI
        self.remaining_time.set("Ready to start")
        self.update_status("Timer Stopped", "#f44336")
        self.start_button.config(text="Start", bg="#4CAF50")
        
        # Stop any running timer thread
        if self.timer_thread and self.timer_thread.is_alive():
            self.timer_thread = None
    
    def run_timer(self, duration):
        """Run the timer countdown for the specified duration"""
        # Initial setup
        if hasattr(self, 'paused_time_remaining'):
            # If resuming from pause, use the stored remaining time
            remaining_seconds = self.paused_time_remaining
            end_time = time.time() + remaining_seconds
            delattr(self, 'paused_time_remaining')  # Remove the attribute after using it
        else:
            # Fresh timer start
            end_time = time.time() + duration
        
        pause_start_time = None
        
        while True:  # Changed to infinite loop with explicit exit conditions
            # Check if timer was stopped
            if not self.running and not self.is_paused:
                return
            
            # Handle pause state
            if self.is_paused:
                if pause_start_time is None:
                    pause_start_time = time.time()
                time.sleep(0.1)
                continue
            elif pause_start_time is not None:
                # Resuming from pause - adjust end time
                pause_duration = time.time() - pause_start_time
                end_time += pause_duration
                pause_start_time = None
                
            # Calculate remaining time
            current_time = time.time()
            remaining_seconds = max(0, int(end_time - current_time))
            
            # Update timer display
            minutes, seconds = divmod(remaining_seconds, 60)
            self.remaining_time.set(f"{minutes}:{seconds:02d}")
            
            # Log focus time every minute
            if not self.is_resting and remaining_seconds % 60 == 0 and remaining_seconds > 0:
                self.log_focus_time(1)
            
            # Check if timer completed
            if remaining_seconds <= 0:
                break
                
            time.sleep(0.1)
        
        # Timer completed
        if self.running:
            self.timer_completed()
    
    def timer_completed(self):
        """Handle timer completion - switch between focus and rest modes"""
        if self.is_resting:
            # End of rest period
            self.is_resting = False
            self.update_status("Focus Time!", "#FFD700")
            self.notify_user("Break Over! Time to focus.")
            
            # Start focus time
            if self.running:
                self.timer_thread = threading.Thread(target=self.run_timer, args=(self.focus_time.get() * 60,))
                self.timer_thread.daemon = True
                self.timer_thread.start()
        else:
            # End of focus period
            self.is_resting = True
            self.update_status("Break Time!", "#4CAF50")
            self.notify_user("Focus Time Over! Take a break.")
            
            # Start rest time
            if self.running:
                self.timer_thread = threading.Thread(target=self.run_timer, args=(self.rest_time.get() * 60,))
                self.timer_thread.daemon = True
                self.timer_thread.start()
    
    def notify_user(self, message):
        """Send notification to user when timer completes"""
        # Show GUI notification
        messagebox.showinfo("Pomodoro", message)
        
        # Send system notification on Linux
        if os.name == "posix":
            os.system(f'notify-send "Pomodoro" "{message}"')
    
    def update_status(self, text, color):
        """Update the status display"""
        self.status_label.config(text=text, fg=color)
    
    def log_focus_time(self, minutes):
        """Record completed focus time to database"""
        today = datetime.today().strftime('%Y-%m-%d')
        
        # Create a new connection to avoid thread issues
        conn = sqlite3.connect("pomodoro_history.db")
        cursor = conn.cursor()
        
        # Check if today already has an entry
        cursor.execute("SELECT focus_minutes FROM history WHERE date = ?", (today,))
        result = cursor.fetchone()
        
        # Update or insert record
        if result:
            total_minutes = result[0] + minutes
            cursor.execute("UPDATE history SET focus_minutes = ? WHERE date = ?", (total_minutes, today))
        else:
            cursor.execute("INSERT INTO history (date, focus_minutes) VALUES (?, ?)", (today, minutes))
        
        conn.commit()
        conn.close()
    
    def show_history(self):
        """Display focus time history"""
        self.cursor.execute("SELECT date, focus_minutes FROM history ORDER BY date DESC")
        records = self.cursor.fetchall()
        
        if records:
            # Format history data for display
            history_text = "Your Pomodoro History:\n\n" + "\n".join([f"{date}: {minutes} minutes" for date, minutes in records])
        else:
            history_text = "No history found. Complete some focus sessions first!"
            
        messagebox.showinfo("Pomodoro History", history_text)
    
    def __del__(self):
        """Clean up database connection when app closes"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()