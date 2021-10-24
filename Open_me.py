import subprocess
import tkinter as tk
from tkinter import messagebox as msg
from tkinter import ttk
import tkinter.font as tkFont
from PIL import ImageTk, Image

# Externally sourced functionality for TkInter Widgets
from TkInterToolTip import ToolTip
from magnetic_field import MagneticField

# TODO: convert report to HTML
# TODO: Add documentation for physics https://journals.aps.org/pra/pdf/10.1103/PhysRevA.35.1535

#####################################################
# Multipage tkinter menu implementation
# link:http://stackoverflow.com/questions/14817210/using-buttons-in-tkinter-to-navigate-to-different-pages-of-the-application
####################################################


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.frame = tk.Frame(self)

    def show(self):
        self.lift()

    def quit(self):
        self.frame.quit()
        self.frame.destroy()

    @staticmethod
    def custom_font(frame, **kwargs):
        return tkFont.Font(frame, **kwargs)


class App(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

        self.pack(side="top", fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # use only a single page
        vis = Visualisation(self)
        vis.grid(row=0, column=0, sticky="nsew")
        vis.show()

        # Disable multipage menu
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        # self.frames = {}
        # for F in (StartPage, Visualisation, Report):
        #     frame = F(container, self)
        #     self.frames[F] = frame
        #     # put all of the pages in the same location;
        #     # the one on the top of the stacking order
        #     # will be the one that is visible.
        #     frame.grid(row=0, column=0, sticky="nsew")
        # self.show_frame(StartPage)


class Visualisation(Page):
    def __init__(self, *args, **kwargs):
        Page.__init__(self, *args, **kwargs)

        # Custom fonts
        self.bold20 = self.custom_font(self, size=16, weight=tkFont.BOLD)

        tk.Label(
            self, text="Magnetic Field Streamlines of a Single Coil", font=self.bold20
        ).pack(side="top", fill="x", pady=10)

        self.frame.pack()

        self.e_R = None
        self.e_I = None
        self.cb = None

        self.dark_theme = False
        if self.tk.eval("return $theme") == "dark":
            self.dark_theme = True

        self.inputs(self.frame)

    def inputs(self, frame):
        # Define child frame for the master
        input_frame = tk.Frame(frame)
        input_frame.grid(column=0, row=0)

        self.buttons_and_entries(input_frame)

        # Text for Mayavi Scenes Controls
        self.description(input_frame)

        # Labels
        self.labels(input_frame)

        # Add tooltips wideget
        self.tool_tips(input_frame)

        # Blank Lines
        input_frame.grid_rowconfigure(5, minsize=20)
        input_frame.grid_rowconfigure(7, minsize=10)
        input_frame.grid_rowconfigure(9, minsize=30)

    def buttons_and_entries(self, input_frame):
        # Validate that entries receive real numbers
        vcmd = (input_frame.register(self.validate), "%P")
        # Add Entry widgets
        # @note do not compound .grid on Entry, because it stores a None
        self.e_R = ttk.Entry(input_frame, validate="key", validatecommand=vcmd)
        self.e_R.insert(0, "1.0")
        self.e_R.grid(column=1, row=1, padx=5, pady=(0, 5), sticky="ew")

        self.e_I = ttk.Entry(input_frame, validate="key", validatecommand=vcmd)
        self.e_I.grid(column=1, row=2, padx=5, pady=(0, 5), sticky="ew")
        self.e_I.insert(0, "1.0")

        # Plot sphere element Button
        glyphs = ("sphere", "plane", "line")
        self.cb = ttk.Combobox(input_frame, values=glyphs, state="readonly")
        self.cb.current(0)
        self.cb.grid(column=1, row=3, padx=5, pady=(0, 5), sticky="ew")

        b_plot = ttk.Button(
            input_frame, text="Plot", command=self.plot_field, style="Accent.TButton"
        )
        b_plot.grid(column=0, row=6, sticky="ew")

        # Bottom row buttons
        ttk.Button(
            input_frame,
            text="Open Report",
            # anchor=tk.W,
            command=self.open_file,
            style="Toggle.TButton",
        ).grid(column=0, row=10)

        ttk.Button(
            input_frame, text="Quit", command=self.quit, style="Toggle.TButton"
        ).grid(column=3, row=10)

    @staticmethod
    def description(input_frame):
        sep = ttk.Separator(input_frame)
        sep.grid(row=7, column=0, padx=(10, 10), pady=20, columnspan=4, sticky="ew")

        desc_frame = ttk.LabelFrame(input_frame, text="Mayavi Visualisation Controls")
        desc_frame.grid(column=0, row=8, ipadx=10, ipady=10, columnspan=4)

        ttk.Label(
            desc_frame,
            text="\n"
            "-i: Enable\Disable glyph widget\n"
            "-Left-click: On the visualisation element to show more field lines\n"
            "-Right-click and Drag: On the visualisation element to adjust its size\n"
            "-Left-click and Drag: On the visualisation element to move it inside the field\n"
            "-Scroll-up\down: To zoom in\out respectively",
            justify="left",
            font=("-size", 8),
        ).pack()

    @staticmethod
    def labels(input_frame):
        ttk.Label(
            input_frame,
            text="Radius R",
            # justify=tk.LEFT,
            anchor=tk.W,
            # relief=tk.RIDGE,
        ).grid(column=0, row=1)

        ttk.Label(
            input_frame,
            text="Current I",
            # justify=tk.LEFT,
            anchor=tk.W,
            # relief=tk.RIDGE,
        ).grid(column=0, row=2)

        ttk.Label(
            input_frame,
            text="Inspector",
            # justify=tk.LEFT,
            anchor=tk.W,
            # relief=tk.RIDGE,
        ).grid(column=0, row=3)

    def tool_tips(self, input_frame):

        # Info logo image
        logo = ImageTk.PhotoImage(Image.open("assets/info_icon.png"))
        if self.dark_theme:
            logo = ImageTk.PhotoImage(Image.open("assets/info_icon_dark_theme.png"))

        # Information Buttons
        info1 = tk.Label(input_frame, image=logo)
        info1.image = logo
        info1.grid(column=2, row=3)

        infoToolTip = ToolTip(
            info1,
            msg=(
                "+Using different geometric structures as unit elements\n of the"
                " magnetic field. Click and Drag the element to visualise the"
                " field.\n+The magnetic fields generated in this GUI are independent of"
                " the medium.\n and hence μ/μ0, see Section 3 from the report.\n+Change"
                " the background-foreground from the settings button in Mayavi"
                " sc\n+Feel free to save Mayavi scenes from the save icon!"
            ),
            delay=0,
        )

        info2 = tk.Label(input_frame, image=logo)
        info2.image = logo
        info2.grid(column=2, row=2)

        # Add a tooltip to a widget.
        infoToolTip = ToolTip(
            info2,
            msg=(
                "+The DC current in Amperes flowing through the circular loop.\n+When"
                " the current increases (absolute value),\n the magnetic field strength"
                " increases too.\n+I<0: the direction which the current flows"
                " changes,\n intended for AC simulation but Tkinter only produces"
                " static Mayavi scenes.\n+For I=0 you get a WARNING."
            ),
            delay=0,
        )
        info3 = ttk.Label(input_frame, image=logo)
        info3.image = logo
        info3.grid(column=2, row=1)

        # Add a tooltip to a widget.
        infoToolTip = ToolTip(
            info3,
            msg=(
                "+The radius R from the center of the circular loop in meters.\n+As R"
                " increases the magnetic field strength increases too."
            ),
            delay=0,
        )

    @staticmethod
    def open_file():
        # TODO: make this use HTML
        return subprocess.Popen("a-doc.pdf", shell=True)

    def plot_field(self):
        if self.cb.get() == "line":
            return MagneticField.line_el(float(self.e_R.get()), float(self.e_I.get()))
        elif self.cb.get() == "plane":
            return MagneticField.plane_el(float(self.e_R.get()), float(self.e_I.get()))
        elif self.cb.get() == "sphere":
            return MagneticField.sphere_el(float(self.e_R.get()), float(self.e_I.get()))
        else:
            return

    @staticmethod
    def validate(value_if_allowed):
        if value_if_allowed:
            try:
                float(value_if_allowed)
                return True
            except ValueError:
                return False
        else:
            return False


if __name__ == "__main__":
    THEME = "dark"

    root = tk.Tk()
    root.title("Magnetic Field Visualiser")
    root.wm_geometry("550x460")

    # Set the theme
    root.tk.call("source", "themes/sun-valley/sun-valley.tcl")
    root.tk.call("set_theme", THEME)
    root.tk.call("set", "theme", THEME)  # for theme mode to be accessible inside App

    main = App(root)
    main.pack(side="top", fill="both", expand=True)

    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    # root.geometry("+{}+{}".format(x_cordinate, y_cordinate))

    root.mainloop()
