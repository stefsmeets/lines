from future import standard_library
standard_library.install_aliases()
from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *

import os

import multiprocessing as mp
from collections import namedtuple

from . import lines

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


class LinesBackgroundDialog(Tk):

    """Dialog that provide settings window for Lines Background correction"""

    def __init__(self, parent, drc='.'):
        super().__init__()

        self.parent = parent

        self.init_vars()

        self.drc = '.'

        self.title("lines: background")

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
        
        self.ticks_file = StringVar()

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
        
        lfpattern    = Labelframe(master, text="Observed data (.xy, .xye)", padding=(10, 10, 10, 10))
        self.e_fname = Entry(
            lfpattern, textvariable=self.pattern_file)
        self.e_fname.grid(row=11, column=0, columnspan=3, sticky=E+W)
        but_load = Button(lfpattern, text="Browse..", width=10, command=self.load_pattern_file)
        but_load.grid(row=11, column=4, sticky=E)
        lfpattern.grid(row=0, sticky=E+W)
        lfpattern.columnconfigure(0, minsize=120)
        lfpattern.columnconfigure(0, weight=1)

        lfbgin = Labelframe(master, text="Background points (.xy, lines.out)", padding=(10, 10, 10, 10))
        self.e_fname = Entry(
            lfbgin, textvariable=self.bgin_file)
        self.e_fname.grid(row=21, column=0, columnspan=3, sticky=E+W)
        but_load = Button(lfbgin, text="Browse..", width=10, command=self.load_bgin_file)
        but_load.grid(row=21, column=4, sticky=E)
        lfbgin.grid(row=1, sticky=E+W)
        lfbgin.columnconfigure(0, minsize=120)
        lfbgin.columnconfigure(0, weight=1)

        lfticks = Labelframe(master, text="Tick marks (x)", padding=(10, 10, 10, 10))
        self.e_fname = Entry(
            lfticks, textvariable=self.ticks_file)
        self.e_fname.grid(row=21, column=0, columnspan=3, sticky=E+W)
        but_load = Button(lfticks, text="Browse..", width=10, command=self.load_ticks_file)
        but_load.grid(row=21, column=4, sticky=E)
        lfticks.grid(row=2, sticky=E+W)
        lfticks.columnconfigure(0, minsize=120)
        lfticks.columnconfigure(0, weight=1)

        lfbg   = Labelframe(master, text="Background correction", padding=(10, 10, 10, 10))
        Label(lfbg, text="Background order").grid(row=25, column=0, sticky=W)
        self.sb_order = Spinbox(lfbg, from_=1, to=10, textvariable=self.bgorder)
        self.sb_order.grid(row=25, column=1, sticky=W) 

        self.c_correct_background = Checkbutton(lfbg, variable=self.bgcorrect, text="Correct background? ")
        self.c_correct_background.grid(row=31, column=0, sticky=W)

        self.c_topasbg = Checkbutton(lfbg, variable=self.topasbg, text="Topas mode?")
        self.c_topasbg.grid(row=32, column=0, sticky=W)

        lfbg.grid(row=3, sticky=E+W)
        lfbg.columnconfigure(0, minsize=120)
        # lfbg.columnconfigure(0, weight=1)

    def buttonbox(self):
        box = Frame(self)

        w = Button(box, text="Run", width=10, command=self.ok, default=ACTIVE)
        w.pack(side=RIGHT, padx=5, pady=5)
        w = Button(box, text="Exit", width=10, command=self.cancel)
        w.pack(side=RIGHT, padx=5, pady=5)
        w = Button(box, text="Help", width=10, command=self.help)
        w.pack(side=RIGHT, padx=5, pady=5)

        self.bind("<F1>", self.help)
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

    def help(self):
        print("Lines: background (manual)")
        print("==========================")

        print("""
Lines is a background correction program to interactively 
remove the background for powder diffraction data. It respects your
standard deviations and never overwrites the original data. 

Clicking 'run' will initiate the background correction routine. 
Left-clicking will add a point, right-clicking on a poitn will remove it

Closing the plotting window will write the background corrected files. The 
corrected file is written to XXX_corr.xye and the background to XXX_bg.xye
The background points are by default written to the file lines.out. In case
this file exists, the original is backed up to lines.out~.

If XXX_corr.xye is used in the rietveld refinement program, by simply 
opening lines.out the background correction can be continued so it is then
possible to update the background correction without modifying the original
data.""")
        print()
        print("Observed data")
        print("-------------")
        print("""
    Path to your observed data to perform background correction on.
    Lines can read any ascii file with 2 or 3 space-separated columns, 
    such as .xy or .xye format.
    """)

        print("Background points")
        print("-----------------")
        print("""
    Path to the file containing the background points to load. Lines 
    will interpolate between these points to remove the background from 
    the observed data. Lines can read any ascii file with two space-
    separated columns, such as .xy format. By default, lines stores 
    the background points to the file lines.out
    """)

        print("Tick marks")
        print("----------")
        print("""
    Path to file with tick marks. This can be generated n Topas using 
    the macro 'Create_2Th_Ip_file(ticks.out)'. Should be a single column
    containing the 2thetha values for the tick marks.
    """)

        print("Background correction")
        print("---------------------")
        print("""
    Background order: Lines can interpolate between the 
        background points based on the order given here. The default 
        is 1 and indicates a linear background correction.
    
    Correct background?: Lines will update the background after the 
        plotting window is closed. Turning this off prevents that.
    
    Topas mode?: In case the calculated and difference plots are 
        present in the current folder, Lines will load these files and 
        plot them as well.

        Use the following macros to generate these files:

            Out_X_Yobs(x_yobs.xy)
            Out_X_Ycalc(x_ycalc.xy)
            Out_X_Difference(x_ydiff.xy)
    """)

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

        if self.ticks_file.get():
            gui_options["plot_ticks"] = [self.ticks_file.get()]

        # interactive matplotlib window is not thread safe, so call a separate process instead
        p = mp.Process(target=lines.run_script, kwargs={"gui_options":gui_options})
        p.start()

    def load_pattern_file(self):
        f = askopenfilename(initialdir=self.drc)
        if f:
            self.pattern_file.set(os.path.normpath(str(f)))
            self.drc = os.path.dirname(f)
            os.chdir(self.drc)
            if os.path.exists("x_yobs.xy") and os.path.exists("x_ycalc.xy") and os.path.exists("x_ydiff.xy"):
               self.topasbg.set(True)

            path_lines_out = os.path.normpath(os.path.join(self.drc,"lines.out"))

            if not self.bgin_file.get() and os.path.exists(path_lines_out):
                self.bgin_file.set(path_lines_out)

    def load_bgin_file(self):
        f = askopenfilename(initialdir=self.drc)
        if f:
            self.bgin_file.set(os.path.normpath(str(f)))
            self.drc = os.path.dirname(f)

    def load_ticks_file(self):
        f = askopenfilename(initialdir=self.drc)
        if f:
            self.ticks_file.set(os.path.normpath(str(f)))
            self.drc = os.path.dirname(f)



def run():
    app = LinesBackgroundDialog(None)
    app.mainloop()


if __name__ == '__main__':
    run()
