"""
This file contains some handy Python3 tkinter extensions.
    DraggableWidget
"""
import tkinter as tk


class DraggableWidget(tk.Widget):
    """
    Inheriting from this class allows your object to automatically be draggable if geometry is "place"
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._placed = False
        self._x = 0
        self._y = 0
        self._px = 0
        self._py = 0
        self._place_timer = None
        self._refresh = 10  # ms
        self.bind("<1>", self.on_click)
        self.bind("<B1-Motion>", self.on_move)
        self.bind("<ButtonRelease-1>", self.on_stop)

    def on_click(self, event):
        if not self._placed:
            return
        self._x = self.winfo_x()
        self._y = self.winfo_y()
        self._px = self.winfo_pointerx()
        self._py = self.winfo_pointery()
        self._place_again()

    def on_move(self, event):
        if not self._placed:
            return
        px = self.winfo_pointerx()
        py = self.winfo_pointery()
        self._x += px - self._px
        self._y += py - self._py
        self._px = px
        self._py = py

    def on_stop(self, event):
        if not self._placed:
            return
        if self._place_timer is not None:
            self.after_cancel(self._place_timer)
            self._place_timer = None
            self.place_forget()
            self.place(x=self._x, y=self._y)
        self._x = self.winfo_x()
        self._y = self.winfo_y()

    def _place_again(self, event=None):
        self.place_forget()
        self.place(x=self._x, y=self._y)
        self._place_timer = self.after(self._refresh, self._place_again)

    def place(self, *args, **kwargs):
        self._placed = True
        super().place(*args, **kwargs)

    def place_forget(self, *args, **kwargs):
        self._placed = False
        super().place_forget()


if __name__ == '__main__':
    class Test(DraggableWidget, tk.Label):
        pass


    root = tk.Tk()
    frm1 = tk.Frame(root, height=300, width=600)
    frm1.pack()
    l = Test(frm1, text="placed!")
    l.place(x=0, y=0)
    frm2 = tk.Frame(root, height=300, width=600)
    frm2.pack()
    l1 = Test(frm2, text="packed!")
    l1.pack()
    root.mainloop()
