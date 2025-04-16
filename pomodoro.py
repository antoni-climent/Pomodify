import sys
import sqlite3
import datetime
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox
)
from PyQt5.QtCore import QTimer, Qt

# Database setup
db_path = os.path.expanduser("~/.pomodoro/pomodoro.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path)

cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS time_logs (
        date TEXT PRIMARY KEY,
        mins INTEGER
    )
''')
conn.commit()

def log_time(mins):
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT mins FROM time_logs WHERE date = ?", (today,))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE time_logs SET mins = ? WHERE date = ?", (row[0] + mins, today))
    else:
        cursor.execute("INSERT INTO time_logs (date, mins) VALUES (?, ?)", (today, mins))
    conn.commit()

def get_today_mins():
    today = datetime.date.today().isoformat()
    cursor.execute("SELECT mins FROM time_logs WHERE date = ?", (today,))
    row = cursor.fetchone()
    return row[0] if row else 0

def get_all_logs():
    cursor.execute("SELECT date, mins FROM time_logs ORDER BY date")
    return cursor.fetchall()

FOCUS_MINUTES = 60
BREAK_MINUTES = 10

class PomodoroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #f0f0f0;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 20px;
            }
            QPushButton {
                background-color: #2d89ef;
                color: white;
                padding: 14px 24px;
                font-size: 18px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #1b6ac9;
            }
        """)

        self.mode = "focus"
        self.time_left = FOCUS_MINUTES * 60
        self.running = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown)

        self.mode_label = QLabel(self.get_mode_text(), alignment=Qt.AlignCenter)
        self.mode_label.setStyleSheet("font-size: 28px; font-weight: bold; margin: 15px 0;")

        self.time_display = QLabel(self.format_time(), alignment=Qt.AlignCenter)
        self.time_display.setStyleSheet("font-size: 56px; font-weight: bold; margin-bottom: 20px;")

        self.status_label = QLabel(self.get_status_text(), alignment=Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; color: #aaa; margin-bottom: 20px;")

        self.start_btn = QPushButton("▶ Start")
        self.start_btn.clicked.connect(self.start_timer)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.clicked.connect(self.pause_timer)

        self.reset_btn = QPushButton("⏹ Reset")
        self.reset_btn.clicked.connect(self.reset_timer)

        self.history_btn = QPushButton("📜 Show History")
        self.history_btn.clicked.connect(self.show_history)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.addWidget(self.mode_label)
        main_layout.addWidget(self.time_display)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.history_btn, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

    def get_mode_text(self):
        return "🧠 Focus Time" if self.mode == "focus" else "☕ Break Time"

    def update_mode_label(self):
        self.mode_label.setText(self.get_mode_text())

    def get_status_text(self):
        return f"⏱️ Time logged today: {get_today_mins()} minutes"

    def format_time(self):
        mins, secs = divmod(self.time_left, 60)
        return f"{mins:02d}:{secs:02d}"

    def start_timer(self):
        if not self.running:
            self.running = True
            self.timer.start(1000)

    def pause_timer(self):
        self.running = False
        self.timer.stop()

    def reset_timer(self):
        self.pause_timer()
        self.mode = "focus"
        self.time_left = FOCUS_MINUTES * 60
        self.update_mode_label()
        self.status_label.setText(self.get_status_text())
        self.time_display.setText(self.format_time())

    def countdown(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.time_display.setText(self.format_time())
            if self.mode == "focus" and self.time_left % 60 == 0:
                log_time(1)
                self.status_label.setText(self.get_status_text())
        else:
            self.pause_timer()
            if self.mode == "focus":
                log_time(self.time_left // 60)
                self.mode = "break"
                self.time_left = BREAK_MINUTES * 60
                QMessageBox.information(self, "Focus Complete", "Time for a break!")
            else:
                self.mode = "focus"
                self.time_left = FOCUS_MINUTES * 60
                QMessageBox.information(self, "Break Over", "Let's get back to work!")

            self.update_mode_label()
            self.time_display.setText(self.format_time())
            self.status_label.setText(self.get_status_text())

    def show_history(self):
        logs = get_all_logs()
        history_msg = "\n".join([f"{date}: {mins} minutes" for date, mins in logs])
        QMessageBox.information(self, "History", history_msg or "No history available.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = PomodoroApp()
    window.show()
    sys.exit(app.exec_())
