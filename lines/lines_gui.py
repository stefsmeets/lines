from Tkinter import *
from tkFileDialog import *
from ttk import *

import os

import multiprocessing as mp
from collections import namedtuple

import lines

def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


class LinesBackgroundDialog(Tk, object):

    """Dialog that provide settings window for Lines Background correction"""

    def __init__(self, parent, drc='.'):
        super(LinesBackgroundDialog, self).__init__()

        self.parent = parent

        self.init_vars()

        self.drc = '.'

        self.title("GUI for lines background routine")

        body = Frame(self, padding=(10, 10, 10, 10))
        self.initial_focus = self.body(body)
        body.columnconfigure(0, weight=1)
        body.pack(fill=BOTH, anchor=CENTER, expand=True)

        self.buttonbox()
        
        self.grab_set()

        self.update()
        self.geometry(self.geometry())       

    def init_vars(self):
        self.pattern_file = StringVar()
        self.pattern_file.set("pattern.xye")

        self.bgin_file = StringVar()

        self.bgorder = IntVar()
        self.bgorder.set(1)

        self.bgcorrect = BooleanVar()
        self.bgcorrect.set(True)

        self.topasbg = BooleanVar()
        if os.path.exists("x_yobs.xy") and os.path.exists("x_ycalc.xy") and os.path.exists("x_ydiff.xy"):
            self.topasbg.set(True)
        else:
            self.topasbg.set(False)

    def body(self, master):
        
        lfpattern    = Labelframe(master, text="Pattern to perform background correction on (xy, xye)", padding=(10, 10, 10, 10))
        self.e_fname = Entry(
            lfpattern, textvariable=self.pattern_file)
        self.e_fname.grid(row=11, column=0, columnspan=3, sticky=E+W)
        but_load = Button(lfpattern, text="Browse..", width=10, command=self.load_pattern_file)
        but_load.grid(row=11, column=4, sticky=E)
        lfpattern.grid(row=0, sticky=E+W)
        lfpattern.columnconfigure(0, minsize=120)
        lfpattern.columnconfigure(0, weight=1)

        lfbgin = Labelframe(master, text="Path to saved background points (xy)", padding=(10, 10, 10, 10))
        self.e_fname = Entry(
            lfbgin, textvariable=self.bgin_file)
        self.e_fname.grid(row=21, column=0, columnspan=3, sticky=E+W)
        but_load = Button(lfbgin, text="Browse..", width=10, command=self.load_bgin_file)
        but_load.grid(row=21, column=4, sticky=E)
        lfbgin.grid(row=1, sticky=E+W)
        lfbgin.columnconfigure(0, minsize=120)
        lfbgin.columnconfigure(0, weight=1)

        lfbg   = Labelframe(master, text="Background correction", padding=(10, 10, 10, 10))
        Label(lfbg, text="Background order").grid(row=25, column=0, sticky=W)
        self.sb_order = Spinbox(lfbg, from_=1, to=10, textvariable=self.bgorder)
        self.sb_order.grid(row=25, column=1, sticky=W) 

        self.c_correct_background = Checkbutton(lfbg, variable=self.bgcorrect, text="Correct background? ")
        self.c_correct_background.grid(row=31, column=0, sticky=W)

        self.c_topasbg = Checkbutton(lfbg, variable=self.topasbg, text="Topas mode?")
        self.c_topasbg.grid(row=32, column=0, sticky=W)

        lfbg.grid(row=2, sticky=E+W)
        lfbg.columnconfigure(0, minsize=120)
        # lfbg.columnconfigure(0, weight=1)

    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="Run", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=RIGHT, padx=5, pady=5)
        w = Button(box, text="Exit", width=10, command=self.cancel)
        w.pack(side=RIGHT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack(fill=X, anchor=S, expand=False)

    def add_cell(self):
        var = self.init_cell()
        self.vars.append(var)
        self.page(var)

    def ok(self, event=None):
        if not self.validate():
            return

        # self.withdraw()
        self.update_idletasks()

        self.apply()

        # self.destroy()

    def cancel(self, event=None):
        self.destroy()

    def validate(self):
        return 1  # override

    def apply(self):
        gui_options = {
            "args": [self.pattern_file.get()],
            "topas_bg": self.topasbg.get()
        }

        bgin = self.bgin_file.get()
        if bgin:
            gui_options["bg_input"] = bgin

        if self.bgcorrect.get():
            gui_options["bg_correct"] = self.bgorder.get()

        # interactive matplotlib window is not thread safe, so call a separate process instead
        p = mp.Process(target=lines.run_script, kwargs={"gui_options":gui_options})
        p.start()

    def load_pattern_file(self):
        f = askopenfilename(initialdir=self.drc)
        if f:
            self.pattern_file.set(str(f))
            self.drc = os.path.dirname(f)

            path_lines_out = os.path.join(self.drc,"lines.out")

            if not self.bgin_file.get() and os.path.exists(path_lines_out):
                self.bgin_file.set(path_lines_out)

    def load_bgin_file(self):
        f = askopenfilename(initialdir=self.drc)
        if f:
            self.bgin_file.set(str(f))
            self.drc = os.path.dirname(f)


def run():
    app = LinesBackgroundDialog(None)
    app.mainloop()


if __name__ == '__main__':
    run()
