# Auto Message Sender Script

A simple Python automation script designed to automatically paste and send a pre-defined text message multiple times using GUI automation and clipboard manipulation.

---

## 📋 Features

* **Clipboard Management:** Uses `pyperclip` to safely copy text to the system clipboard.
* **GUI Automation:** Uses `pyautogui` to simulate keystrokes (`Ctrl + V` and `Enter`).
* **Delay Handlers:** Incorporates countdown and execution delays to give the user time to focus on the target chat window.

---

## 🚀 Prerequisites & Installation

Ensure you have Python installed on your system.

1. **Clone the repository:**
   ```bash
┌─[live@parrot]─[~]
└──╼ $git clone [https://github.com/Mr-system2580/2/new/main/AUTO-TYPING](https://github.com/Mr-system2580/2/new/main/AUTO-TYPING)
┌─[live@parrot]─[~]
└──╼ $cd AUTO-TYPING

2 **Install the required dependencies:**
pip install pyautogui pyperclip

or  ┌─[live@parrot]─[~]
    └──╼ $pip install pyautogui pyperclip --break-system-packages
or
┌─[live@parrot]─[~]
└──╼ $python3 -m venv mazingira
┌─[live@parrot]─[~]
└──╼ $source mazingira/bin/activate
(mazingira) ┌─[live@parrot]─[~]
└──╼ $pip install pyautogui pyperclip

# HOE TO USE
1:Run the script:

(mazingira) ┌─[live@parrot]─[~]
└──╼ $python AUTO-typing.py

2:Immediately switch to your desired messaging application (e.g., WhatsApp Web, Telegram, Discord).
3:Click inside the message input box within 5 seconds.
4:The script will automatically paste and send the message for the specified number of iterations.

# ⚠️ Disclaimer & Usage Note
​This project is created strictly for educational and personal automation testing purposes. Please use it responsibly and avoid spamming individuals or services without consent.
