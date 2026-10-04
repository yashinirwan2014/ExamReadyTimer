import tkinter as tk

window = tk.Tk()

window.title("ExamReadyTimer")
window.geometry("700x500")

title = tk.Label(
    window,
    text="EXAMREADY",
    font=("Arial", 28, "bold")
)

title.pack(pady=30)

subtitle = tk.Label(
    window,
    text="STUDY • FOCUS • PREPARE",
    font=("Arial", 12)
)

subtitle.pack()

message = tk.Label(
    window,
    text="Your study dashboard is ready!",
    font=("Arial", 14)
)

message.pack(pady=40)

window.mainloop()
