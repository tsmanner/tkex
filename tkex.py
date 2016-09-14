"""
This file contains some handy Python3 tkinter extensions.
    Objects:
        DraggableWidget

    Systems:
        Drop - New geometry manager that lets a user "drop" a window at
"""
import tkinter as tk
import math
from matplotlib.path import Path
import numpy as np


class DraggableWidget(tk.Widget):
    """
    Inheriting from this class allows your object to automatically be draggable if geometry is "place"
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._placed = False
        self._x = 0
        self._y = 0
        self._last_x = 0
        self._last_y = 0
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
        self._last_x = self._x
        self._last_y = self._y
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
        if self._x != self._last_x or self._y != self._last_y:
            self.place_forget()
            self.place(x=self._x, y=self._y)
            self._last_x = self._x
            self._last_y = self._y
        self._place_timer = self.after(self._refresh, self._place_again)

    def place(self, *args, **kwargs):
        self._placed = True
        super().place(*args, **kwargs)

    def place_forget(self, *args, **kwargs):
        self._placed = False
        super().place_forget()


"""
Drop Geometry Manager.  Uses place under the covers and the DraggableWidget base class.
"""


class DroppableWidget(DraggableWidget):
    """
    Inheriting from this class allows your object to be "dropped" into it's master and dragged into position
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def drop(self):
        self.master.update_idletasks()
        # self.scan()
        poly = None
        for child in self.master.children.values():
            if child is not self:
                coords = ((child.winfo_x(), child.winfo_y()),
                          (child.winfo_x() + child.winfo_reqwidth(), child.winfo_y() + child.winfo_reqheight()))
                this_poly = Path([(coords[0][0], coords[0][1]),
                                  (coords[0][0], coords[1][1]),
                                  (coords[1][0], coords[1][1]),
                                  (coords[1][0], coords[0][1])])
                if poly:
                    poly = Path.make_compound_path(poly, this_poly)
                else:
                    poly = this_poly
        self.place(x=0, y=0)

    def scan(self):
        r_max = round(math.sqrt((self.master.winfo_reqwidth() ** 2 + self.master.winfo_reqheight() ** 2)))
        theta_max = math.pi / 2
        scanned = set()
        for r in range(0, r_max + 1):
            theta_range = [0]
            step = theta_max / 2
            while theta_range[-1] < theta_max:
                theta_range.append(theta_range[-1] + step)
            for theta in theta_range:
                rx = round(r * math.cos(theta))
                ry = round(r * math.sin(theta))
                scanned.add((rx, ry))
                print(r, round(theta, 2), rx, ry)
        print(set(zip(range(0, self.master.winfo_reqwidth()), range(0, self.master.winfo_reqheight()))) - scanned)

    def print(self, event=None):
        print(self.winfo_x(), self.winfo_y())


if __name__ == '__main__':
    class Test(DroppableWidget, tk.Label):
        pass


    class TestMaster(tk.Frame):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.new_item_button = tk.Button(self, text="new", command=self.create_new_label)
            self.new_item_button.pack()
            self.label_frame = tk.Frame(self, height=150, width=150)
            self.label_frame.pack()
            self.labels = []

        def create_new_label(self):
            name = "test" + str(len(self.labels))
            self.labels.append(Test(self.label_frame, text=name))
            self.labels[-1].name = name
            self.labels[-1].drop()


    root = tk.Tk()
    tm = TestMaster(root)
    tm.pack()
    root.mainloop()
