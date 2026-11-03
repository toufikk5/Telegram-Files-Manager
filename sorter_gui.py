import customtkinter as ctk
from tkinter import messagebox
import threading
import asyncio
from sorter_core import client, get_group_entity, get_topics, sync_topic, load_log, save_log,convert_folder_to_pdf
import os


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Telegram File Sorter")
root.geometry("420x420")

groups_list = []
topics_list = []

# ---------- Background asyncio loop (runs forever alongside the GUI) ----------

bg_loop = asyncio.new_event_loop()

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

bg_thread = threading.Thread(target=start_background_loop, args=(bg_loop,), daemon=True)
bg_thread.start()

def run_async(coro, on_done=None):
    """Schedule an async function to run on the background loop, without freezing the GUI."""
    future = asyncio.run_coroutine_threadsafe(coro, bg_loop)
    if on_done:
        future.add_done_callback(lambda f: root.after(0, lambda: on_done(f)))
    return future


# ---------- Async logic ----------

async def _fetch_groups():
    await client.connect()

    if not await client.is_user_authorized():
        raise RuntimeError(
            "Telegram session is not authorized. "
            "Please run test_login.py first."
        )

    dialogs = await client.get_dialogs()
    return [d for d in dialogs if d.is_group]


async def _load_topics(entity):
    async with client:
        return await get_topics(client, entity)


async def _sync_topic(entity, topic_id, topic_name):
    log = load_log()
    async with client:
        new_count = await sync_topic(client, entity, topic_id, topic_name, log)
    save_log(log)
    return new_count


# ---------- GUI callbacks ----------

def fetch_groups():
    global groups_list
    status_label.configure(text="Connecting...")
    connect_button.configure(state="disabled")

    def on_done(future):
        global groups_list
        connect_button.configure(state="normal")
        try:
            groups_list = future.result()
            group_names = [d.name for d in groups_list]
            group_dropdown.configure(values=group_names)
            if group_names:
                group_dropdown.set(group_names[0])
            status_label.configure(text="Groups loaded! Pick one below.")
        except Exception as e:
            status_label.configure(text=f"Error: {e}")

    run_async(_fetch_groups(), on_done)


def load_topics():
    global topics_list
    selected_name = group_dropdown.get()
    if not selected_name:
        messagebox.showwarning("No selection", "Please select a group first!")
        return

    entity = None
    for dialog in groups_list:
        if dialog.name == selected_name:
            entity = dialog.entity
            break

    status_label.configure(text="Loading topics...")
    load_topics_button.configure(state="disabled")

    def on_done(future):
        global topics_list
        load_topics_button.configure(state="normal")
        try:
            topics_list = future.result()
            topic_names = [t.title for t in topics_list]
            topic_dropdown.configure(values=topic_names)
            if topic_names:
                topic_dropdown.set(topic_names[0])
            status_label.configure(text="Topics loaded! Pick one below.")
        except Exception as e:
            status_label.configure(text=f"Error: {e}")

    run_async(_load_topics(entity), on_done)



def show_convert_choice(topic_name):
    convert_frame.pack(pady=10)
    convert_label.configure(text=f"Convert files in '{topic_name}' to PDF?")
    
    def on_convert():
        desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop', 'Telegram Downloads')
        folder = os.path.join(desktop_path, topic_name)
        status_label.configure(text="Converting...")
        convert_frame.pack_forget()

        async def _convert():
            return await asyncio.to_thread(convert_folder_to_pdf, folder)

        def on_convert_done(future):
            try:
                count = future.result()
                status_label.configure(text=f"Converted {count} file(s) to PDF.")
            except Exception as e:
                status_label.configure(text=f"Error: {e}")

        run_async(_convert(), on_convert_done)
    
    def on_keep():
        convert_frame.pack_forget()
        status_label.configure(text="Kept original files.")
    
    convert_yes_button.configure(command=on_convert)
    convert_no_button.configure(command=on_keep)


def sync_selected_topic():
    selected_group = group_dropdown.get()
    selected_topic = topic_dropdown.get()

    if not selected_group or not selected_topic:
        messagebox.showwarning("No selection", "Please select a group and a topic first!")
        return

    entity = None
    for dialog in groups_list:
        if dialog.name == selected_group:
            entity = dialog.entity
            break

    target_topic = None
    for topic in topics_list:
        if topic.title == selected_topic:
            target_topic = topic
            break

    status_label.configure(text=f"Syncing '{selected_topic}'... please wait")
    sync_button.configure(state="disabled")

    def on_done(future):
        sync_button.configure(state="normal")
        try:
            new_count = future.result()
            status_label.configure(text=f"Done! {new_count} new file(s) in '{selected_topic}'.")
            show_convert_choice(selected_topic)
        except Exception as e:
            status_label.configure(text=f"Error: {e}")

    run_async(_sync_topic(entity, target_topic.id, target_topic.title), on_done)


# ---------- Layout ----------

main_frame = ctk.CTkFrame(root, fg_color="transparent")
main_frame.place(relx=0.5, rely=0.5, anchor="center")

title_label = ctk.CTkLabel(main_frame, text="📂 Telegram File Sorter", font=ctk.CTkFont(size=20, weight="bold"))
title_label.pack(pady=(0, 15))

connect_button = ctk.CTkButton(main_frame, text="Connect to Telegram", command=fetch_groups, width=320)
connect_button.pack(pady=8)

group_dropdown = ctk.CTkComboBox(main_frame, values=[], state="readonly", width=320)
group_dropdown.pack(pady=8)

load_topics_button = ctk.CTkButton(main_frame, text="Load Topics", command=load_topics, fg_color="#3a3a3a", hover_color="#4a4a4a", width=320)
load_topics_button.pack(pady=8)

topic_dropdown = ctk.CTkComboBox(main_frame, values=[], state="readonly", width=320)
topic_dropdown.pack(pady=8)

sync_button = ctk.CTkButton(main_frame, text="⬇ Sync Topic", command=sync_selected_topic, fg_color="#2e7d32", hover_color="#388e3c", width=320)
sync_button.pack(pady=(20, 8))

status_label = ctk.CTkLabel(main_frame, text="Click 'Connect' to load your groups", wraplength=340, text_color="gray")
status_label.pack(pady=15)

convert_frame = ctk.CTkFrame(main_frame, fg_color="transparent")

convert_label = ctk.CTkLabel(convert_frame, text="")
convert_label.pack(pady=(0, 8))

convert_buttons_row = ctk.CTkFrame(convert_frame, fg_color="transparent")
convert_buttons_row.pack()

convert_yes_button = ctk.CTkButton(convert_buttons_row, text="Convert to PDF", fg_color="#2e7d32", hover_color="#388e3c", width=150)
convert_yes_button.pack(side="left", padx=5)

convert_no_button = ctk.CTkButton(convert_buttons_row, text="Keep Original", fg_color="#3a3a3a", hover_color="#4a4a4a", width=150)
convert_no_button.pack(side="left", padx=5)

root.mainloop()