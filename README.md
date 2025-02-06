# ⏳ Pomodoro Timer App

A simple **Pomodoro Timer** built with Python and Tkinter, featuring session tracking with SQLite and desktop notifications for Linux. 📅🔔

---

## 🚀 Features
- 🎯 Customizable **focus** and **rest** times
- 📊 **Session history** stored using SQLite
- 🛑 **Start/Pause/Stop** functionality
- 🔔 **Desktop notifications** upon session completion
- 🖥️ Simple and intuitive **Tkinter GUI**

---

## 🛠️ Installation

### 🔧 Prerequisites
Ensure you have **Conda** installed. If not, install [Miniconda](https://docs.conda.io/en/latest/miniconda.html).

### 📥 Clone the Repository
```bash
git clone https://github.com/antoni-climent/Pomodify.git
cd Pomodify
```

### 📦 Install Dependencies
Run the setup script:
```bash
chmod +x install.sh
./install.sh
```
This will:
- Create a **Conda environment** 🐍
- Install required dependencies 📦
- Launch the Pomodoro app ⏳

Alternatively, install manually:
```bash
conda create -n pomodoro python=3.10
conda activate pomodoro
pip install -r requirements.txt
```

---

## ▶️ Usage
Run the application with:
```bash
conda activate pomodoro
python pomodoro.py
```

### 🎨 Interface Overview
- **Start**: Begin a Pomodoro session
- **Pause**: Pause the session
- **Stop**: Stop the session
- **Show History**: View past focus times

---

## 📜 Requirements
```txt
pysqlite3==0.5.4
tk==0.1.0
```

---

## 📸 Screenshots
The Pomodoro Timer app looks like this:

<img src="image.png" alt="alt text" width="300">

---

Happy Focusing! 🎯

