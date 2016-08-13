import tkinter as tk


class DraggableWidget(tk.Widget):
    """
    Inheriting from this class allows your object to automatically be draggable
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._x = 0
        self._y = 0
        self._px = 0
        self._py = 0
        self._dx = 0
        self._dy = 0
        self._place_timer = None
        self._refresh = 10  # ms
        label.bind("<1>", self.on_click)
        label.bind("<B1-Motion>", self.on_move)
        label.bind("<ButtonRelease-1>", self.on_stop)

    def on_click(self, event):
        self._x = self.winfo_x()
        self._y = self.winfo_y()
        self._px = self.winfo_pointerx()
        self._py = self.winfo_pointery()
        self._place_again()

    def on_move(self, event):
        self._dx = self.winfo_pointerx() - self._px
        self._dy = self.winfo_pointery() - self._py

    def on_stop(self, event):
        if self._place_timer is not None:
            self.after_cancel(self._place_timer)
            self._place_timer = None
            self.place_forget()
            self.place(x=self._x + self._dx, y=self._y + self._dy)
        self._x = self.winfo_x()
        self._y = self.winfo_y()
        self._dx = 0
        self._dy = 0

    def _place_again(self, event=None):
        self.place_forget()
        self.place(x=self._x + self._dx, y=self._y + self._dy)
        self._place_timer = self.after(self._refresh, self._place_again)
