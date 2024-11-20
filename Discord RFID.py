import subprocess
import sys

# Function to check and install modules
def install_module(module_name):
    try:
        __import__(module_name)
    except ImportError:
        print(f"Module {module_name} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

# List of required modules
required_modules = ["tkinter", "asyncio", "discord", "discord.ext", "threading"]

# Install each module in the list
for module in required_modules:
    install_module(module)

# Proceed with the rest of the script
import tkinter as tk
from tkinter import messagebox, simpledialog
import asyncio
from discord.ext import commands
from discord import Intents

# In-memory storage for Discord API credentials and leading/trailing characters
discord_token = "your_discord_bot_token_here"
discord_channel_id = 0
leading_characters = ""
trailing_characters = ""

# Define intents
intents = Intents.default()
intents.messages = True
intents.guilds = True

# Discord bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# User data storage
users = {}
rfid_input = ""  # Buffer for RFID input

# Function to send a message to Discord
async def send_discord_message(rfid):
    user = users.get(rfid)
    if user:
        message = f"{user['name']} is at the space: {user['custom_text']}"
        channel = bot.get_channel(discord_channel_id)
        if channel:
            await channel.send(message)

# Start the Discord bot in the background
def start_discord_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    @bot.event
    async def on_ready():
        print(f"Bot logged in as {bot.user}")

    try:
        loop.create_task(bot.start(discord_token))
        loop.run_forever()
    except Exception as e:
        messagebox.showerror("Discord Bot Error", str(e))

# Function to handle keyboard input
def handle_keypress(event):
    global rfid_input
    rfid_input += event.char
    if event.keysym == "Return":  # Process input on Enter key
        process_rfid_input(rfid_input.strip())
        rfid_input = ""  # Reset after processing

# Process RFID input
def process_rfid_input(rfid):
    # Remove leading and trailing characters if defined
    if leading_characters:
        if rfid.startswith(leading_characters):
            rfid = rfid[len(leading_characters):]
    if trailing_characters:
        if rfid.endswith(trailing_characters):
            rfid = rfid[:-len(trailing_characters)]

    # Handle the cleaned RFID
    if rfid:
        if rfid in users:
            asyncio.run(send_discord_message(rfid))
        else:
            messagebox.showwarning("Unknown RFID", "This RFID is not registered!")

# Menu functionality
def quit_app():
    root.quit()

def update_discord_api():
    global discord_token, discord_channel_id
    token = simpledialog.askstring("Discord API", "Enter your Discord bot token:", parent=root)
    channel_id = simpledialog.askstring("Discord API", "Enter your Discord channel ID:", parent=root)
    if token and channel_id:
        try:
            channel_id = int(channel_id)
            discord_token = token
            discord_channel_id = channel_id
            messagebox.showinfo("Success", "Discord API information updated successfully.")
        except ValueError:
            messagebox.showerror("Error", "Channel ID must be a valid number.")

def update_leading_characters():
    global leading_characters
    chars = simpledialog.askstring("Leading Characters", "Enter leading characters to trim (if any):", parent=root)
    if chars is not None:
        leading_characters = chars
        messagebox.showinfo("Success", f"Leading characters set to: '{leading_characters}'")

def update_trailing_characters():
    global trailing_characters
    chars = simpledialog.askstring("Trailing Characters", "Enter trailing characters to trim (if any):", parent=root)
    if chars is not None:
        trailing_characters = chars
        messagebox.showinfo("Success", f"Trailing characters set to: '{trailing_characters}'")

def show_how_to():
    how_to_text = (
        "1. Set up a Discord bot and get your bot token.\n"
        "2. Add the bot to your server and obtain a channel ID.\n"
        "3. Use the 'Settings > Discord API' menu to input the bot token and channel ID.\n"
        "4. Use the 'Settings > Leading Characters' and 'Settings > Trailing Characters' menus to trim extra characters.\n"
        "5. Add users with their RFID, name, and custom message.\n"
        "6. When an RFID card is scanned, the bot sends a message to the configured channel."
    )
    messagebox.showinfo("How To", how_to_text)

def show_info():
    info_text = (
        "This script manages RFID-based user interactions with Discord.\n"
        "It was created by Josh Siefer."
    )
    messagebox.showinfo("Info", info_text)

# Tkinter GUI
def add_user():
    rfid = entry_rfid.get().strip()
    name = entry_name.get().strip()
    custom_text = entry_custom_text.get().strip()

    if not rfid or not name or not custom_text:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    users[rfid] = {"name": name, "custom_text": custom_text}
    listbox.insert(tk.END, f"{rfid}: {name} - {custom_text}")
    entry_rfid.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_custom_text.delete(0, tk.END)

def delete_user():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("Selection Error", "No user selected!")
        return

    index = selected[0]
    rfid = list(users.keys())[index]
    del users[rfid]
    listbox.delete(index)

# GUI setup
root = tk.Tk()
root.title("Discord User Manager")

# Menu
menu = tk.Menu(root)
root.config(menu=menu)

file_menu = tk.Menu(menu, tearoff=0)
file_menu.add_command(label="Quit", command=quit_app)
menu.add_cascade(label="File", menu=file_menu)

settings_menu = tk.Menu(menu, tearoff=0)
settings_menu.add_command(label="Discord API", command=update_discord_api)
settings_menu.add_command(label="Leading Characters", command=update_leading_characters)
settings_menu.add_command(label="Trailing Characters", command=update_trailing_characters)
menu.add_cascade(label="Settings", menu=settings_menu)

about_menu = tk.Menu(menu, tearoff=0)
about_menu.add_command(label="How To", command=show_how_to)
about_menu.add_command(label="Info", command=show_info)
menu.add_cascade(label="About", menu=about_menu)

frame = tk.Frame(root)
frame.pack(pady=10)

# Entry fields for user registration
tk.Label(frame, text="RFID").grid(row=0, column=0, padx=5, pady=5)
entry_rfid = tk.Entry(frame)
entry_rfid.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Name").grid(row=1, column=0, padx=5, pady=5)
entry_name = tk.Entry(frame)
entry_name.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame, text="Custom Text").grid(row=2, column=0, padx=5, pady=5)
entry_custom_text = tk.Entry(frame)
entry_custom_text.grid(row=2, column=1, padx=5, pady=5)

btn_add = tk.Button(frame, text="Add User", command=add_user)
btn_add.grid(row=3, column=0, columnspan=2, pady=5)

listbox = tk.Listbox(root, width=50, height=10)
listbox.pack(pady=10)

btn_delete = tk.Button(root, text="Delete User", command=delete_user)
btn_delete.pack(pady=5)

# RFID input field for scanning
tk.Label(root, text="RFID Input").pack(pady=5)
entry_rfid_input = tk.Entry(root)
entry_rfid_input.pack(pady=5)
entry_rfid_input.bind("<Return>", handle_keypress)  # Trigger on Enter key

# Start Discord bot
import threading
threading.Thread(target=start_discord_bot, daemon=True).start()

root.mainloop()
