import tkinter as tk
from tkinter import messagebox
import sqlite3
import time
from datetime import datetime
import threading
import os

class PomodoroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pomodoro Timer")
        self.root.geometry("500x400")
        self.root.configure(bg="#f0f0f0")
        
        self.focus_time = tk.IntVar(value=60)
        self.rest_time = tk.IntVar(value=10)
        self.remaining_time = tk.StringVar(value="")
        self.running = False
        self.stop_flag = False
        self.paused_time = 0
        
        self.setup_db()
        self.create_widgets()
    
    def setup_db(self):
        self.conn = sqlite3.connect("pomodoro_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS history (
                                date TEXT,
                                focus_minutes INTEGER)''')
        self.conn.commit()
    
    def create_widgets(self):
        tk.Label(self.root, text="Focus Time (min):", bg="#f0f0f0", font=("Arial", 14, "bold")).pack()
        tk.Entry(self.root, textvariable=self.focus_time, font=("Arial", 14)).pack()
        
        tk.Label(self.root, text="Rest Time (min):", bg="#f0f0f0", font=("Arial", 14, "bold")).pack()
        tk.Entry(self.root, textvariable=self.rest_time, font=("Arial", 14)).pack()
        
        self.start_button = tk.Button(self.root, text="Start", command=self.toggle_timer, bg="#4CAF50", fg="white", font=("Arial", 14, "bold"))
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(self.root, text="Stop", command=self.stop_timer, bg="#f44336", fg="white", font=("Arial", 14, "bold"))
        self.stop_button.pack(pady=5)
        
        self.history_button = tk.Button(self.root, text="Show History", command=self.show_history, bg="#2196F3", fg="white", font=("Arial", 14, "bold"))
        self.history_button.pack(pady=5)
        
        self.status_label = tk.Label(self.root, text="Ready", bg="#f0f0f0", font=("Arial", 16, "bold"))
        self.status_label.pack(pady=10)
        
        self.timer_label = tk.Label(self.root, textvariable=self.remaining_time, bg="#f0f0f0", font=("Arial", 18, "bold"))
        self.timer_label.pack(pady=10)
    
    def toggle_timer(self):
        if self.running:
            self.stop_flag = True
            self.running = False
            self.start_button.config(text="Resume", bg="#FF9800")
        else:
            self.stop_flag = False
            self.running = True
            self.start_button.config(text="Pause", bg="#f44336")
            threading.Thread(target=self.run_timer, args=(self.paused_time or self.focus_time.get() * 60, "Focus Time!", "#FF9800", True)).start()
    
    def stop_timer(self):
        self.stop_flag = True
        self.running = False
        self.paused_time = 0
        self.remaining_time.set("Timer Stopped")
        self.update_status("Stopped", "#f44336")
        self.start_button.config(text="Start", bg="#4CAF50")
    
    def run_timer(self, duration, status_text, color, is_focus):
        self.update_status(status_text, color)
        for remaining in range(duration, 0, -1):
            if self.stop_flag:
                self.paused_time = remaining
                return
            
            # Log time every 60 seconds during focus sessions
            if is_focus and remaining % 60 == 0:
                self.log_focus_time(1)  # Save 1 min each time
            
            self.remaining_time.set(f"Time left: {remaining // 60}:{remaining % 60:02d}")
            self.root.update()
            time.sleep(1)

        self.remaining_time.set("")
        self.paused_time = 0
        self.running = False
        self.start_button.config(text="Start", bg="#4CAF50")

        self.notify_user("Focus Time Over! Take a break." if is_focus else "Break Over! Time to focus.")

        if is_focus:
            self.update_status("Break Time!", "#4CAF50")
            threading.Thread(target=self.run_timer, args=(self.rest_time.get() * 60, "Break Time!", "#4CAF50", False)).start()
        else:
            self.update_status("Session Complete", "#4CAF50")

    
    def notify_user(self, message):
        messagebox.showinfo("Pomodoro", message)
        if os.name == "posix":  # Linux/macOS
            os.system(f'notify-send "{message}"')
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
        self.root.update()
    
    def log_focus_time(self, minutes):
        today = datetime.today().strftime('%Y-%m-%d')
        
        # Create a NEW database connection in this thread
        conn = sqlite3.connect("pomodoro_history.db")
        cursor = conn.cursor()
        
        cursor.execute("SELECT focus_minutes FROM history WHERE date = ?", (today,))
        result = cursor.fetchone()

        if result:
            total_minutes = result[0] + minutes
            cursor.execute("UPDATE history SET focus_minutes = ? WHERE date = ?", (total_minutes, today))
        else:
            cursor.execute("INSERT INTO history (date, focus_minutes) VALUES (?, ?)", (today, minutes))

        conn.commit()
        conn.close()  # Close the connection to avoid leaks
    
    def show_history(self):
        self.cursor.execute("SELECT * FROM history")
        records = self.cursor.fetchall()
        history_text = "History:\n" + "\n".join([f"{date}: {minutes} min" for date, minutes in records])
        messagebox.showinfo("History", history_text)
    
    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()
