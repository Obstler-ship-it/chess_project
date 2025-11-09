import tkinter as tk

root = tk.Tk()
img = tk.PhotoImage(file="GUI/White_King.png")

canvas = tk.Canvas(root, width=400, height=400)
canvas.pack()
canvas.create_image(50, 50, image=img, anchor="nw")

root.mainloop()

