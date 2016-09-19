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
        self.tkraise()
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
            max_x = self.master.winfo_reqwidth() - self.winfo_reqwidth() + 5
            max_y = self.master.winfo_reqheight() - self.winfo_reqheight() + 5
            if self._x > max_x:
                self._x = max_x
            if self._x < -5:
                self._x = -5
            if self._y > max_y:
                self._y = max_y
            if self._y < -5:
                self._y = -5
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


class SeriesWidget(DraggableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert isinstance(self.master, Series)

    def on_stop(self, *args, **kwargs):
        super().on_stop(*args, **kwargs)
        self.master.cleanup()


"""
Tk Series.  Basically a list of tk widgets displayed in order, either horizontally or vertically.
"""


class Series(tk.Frame):
    def __init__(self, *args, orientation=None, **kwargs):
        if orientation is None:
            raise ValueError("No orientation provided")
        elif orientation not in [tk.HORIZONTAL, tk.VERTICAL]:
            raise ValueError("Invalid orientation provided, must be tkinter.HORIZONTAL or tkinter.VERTICAL")
        tk.Frame.__init__(self, *args, **kwargs)
        self.series = []
        self.orientation = orientation
        if orientation == tk.HORIZONTAL:
            self.sort_function = lambda w: w.winfo_x()
        else:
            self.sort_function = lambda w: w.winfo_y()

    def append(self, p_object):
        self.update_idletasks()
        x = y = 0
        height = p_object.winfo_reqheight()
        width = p_object.winfo_reqwidth()
        for widget in self.series:
            assert isinstance(widget, tk.Widget)
            if self.orientation == tk.HORIZONTAL:
                x += widget.winfo_reqwidth()
                if height < widget.winfo_reqheight():
                    height = widget.winfo_reqheight()
            else:
                y += widget.winfo_reqheight()
                if width < widget.winfo_reqwidth():
                    width = widget.winfo_reqwidth()
        self.series.append(p_object)
        p_object.place(x=x, y=y)
        self.config(width=x+width, height=y+height)

    def pack(self, *args, **kwargs):
        super().pack(*args, **kwargs)
        self.cleanup()

    def place(self, *args, **kwargs):
        super().place(*args, **kwargs)
        self.cleanup()

    def grid(self, *args, **kwargs):
        super().grid(*args, **kwargs)
        self.cleanup()

    def cleanup(self):
        x = y = 0
        self.series.sort(key=self.sort_function)
        for widget in self.series:
            widget.place_forget()
            widget.place(x=x, y=y)
            if self.orientation == tk.HORIZONTAL:
                x += widget.winfo_reqwidth()
            else:
                y += widget.winfo_reqheight()


class Row(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, orientation=tk.HORIZONTAL, **kwargs)


class Column(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, orientation=tk.VERTICAL, **kwargs)


"""
Drop Geometry Manager.  Uses place under the covers and the DraggableWidget base class.
"""


class DroppableWidget(DraggableWidget):
    """
    Inheriting from this class allows your object to be "dropped" into it's master and dragged into position
    Design Notes:
        Make drop place the widget at the current location then cause a window cleanup.
        Window cleanup will go around the screen and push widgets around until they don't overlap.
            1 - is the widget Top/Left most by center? That's the anchor(specify the anchor with tk vars?)
            2 -
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
    import random


    class Test(SeriesWidget, tk.Button):
        pass


    class TestMaster(tk.Frame):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.new_item_button = tk.Button(self, text="new", command=self.create_new_label, height=8, width=15)
            self.new_item_button.pack(anchor=tk.W)
            self.labels = Row(self, width=50)
            self.labels.pack()

        def create_new_label(self):
            name = "AA<" + str(len(self.labels.series)) + ">"
            colors = ["dark red", "orange", "yellow", "dark green", "blue", "violet"]
            color = colors[random.randint(0, len(colors) - 1)]
            new_test = Test(master=self.labels, text=name, width=10, height=5, bg=color)
            new_test.config(command=lambda: print(new_test.name))
            new_test.name = name
            self.labels.append(new_test)


    root = tk.Tk()
    tm = TestMaster(root)
    tm.pack()
    root.mainloop()
