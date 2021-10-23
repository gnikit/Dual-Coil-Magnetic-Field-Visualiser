import sys
import os
import subprocess
import numpy as np
import tkinter as tk
from mayavi import mlab
from scipy import special
from tkinter import messagebox as msg
from tkinter import ttk
import tkinter.font as tkFont
from PIL import ImageTk, Image

# Externally sourced functionality for TkInter Widgets
from TkInterToolTip import ToolTip

#####################################################
# Menu Externally sourced, supplied by: Bryan Oakley
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

    def custom_font(self, frame, **kwargs):
        return tkFont.Font(frame, **kwargs)


class Menu(tk.Frame):
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
        self.Inputs(self.frame)

    def Inputs(self, frame):
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
        self.cb.grid(column=1, row=3, padx=5, pady=5, sticky="ew")

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

    def description(self, input_frame):
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

    @staticmethod
    def tool_tips(input_frame):

        # Info logo image
        logo = ImageTk.PhotoImage(Image.open("assets/info_icon.png"))

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

    def sphere_el(self):
        mlab.close(all=True)
        fig = mlab.figure(1, size=(500, 500), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
        field = self.eval_magnetic_field()
        magnitude = mlab.pipeline.extract_vector_norm(field)
        contours = mlab.pipeline.iso_surface(
            magnitude,
            contours=3,
            transparent=True,
            opacity=0.6,
            colormap="YlGnBu",
            vmin=0,
            vmax=0.5,
        )

        field_lines = mlab.pipeline.streamline(
            magnitude,
            seedtype="sphere",
            integration_direction="both",
            transparent=True,
            opacity=0.3,
            colormap="jet",
            vmin=0,
            vmax=0.5,
            seed_resolution=12,
        )

        contours.actor.property.frontface_culling = True
        contours.normals.filter.feature_angle = 90

        field_lines.stream_tracer.maximum_propagation = 150
        field_lines.seed.widget.radius = 4
        sc = mlab.scalarbar(
            field_lines, title="Field Strength [T]", orientation="vertical", nb_labels=4
        )
        # horizontal and vertical position from left->right, bottom->top
        sc.scalar_bar_representation.position = np.array([0.9, 0.1])
        # width and height of colourbar
        sc.scalar_bar_representation.position2 = np.array([0.1, 0.8])
        mlab.view(azimuth=42, elevation=73, distance=104)
        mlab.show()

    def plane_el(self):
        mlab.close(all=True)
        fig = mlab.figure(1, size=(500, 500), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
        field = self.eval_magnetic_field()
        magnitude = mlab.pipeline.extract_vector_norm(field)
        contours = mlab.pipeline.iso_surface(
            magnitude,
            transparent=True,
            contours=3,
            opacity=0.6,
            colormap="YlGnBu",
            vmin=0,
            vmax=0.5,
        )

        field_lines = mlab.pipeline.streamline(
            magnitude,
            seedtype="plane",
            integration_direction="both",
            transparent=True,
            opacity=0.3,
            colormap="jet",
            vmin=0,
            vmax=0.5,
        )

        contours.actor.property.frontface_culling = True
        contours.normals.filter.feature_angle = 90

        field_lines.stream_tracer.maximum_propagation = 40.0
        field_lines.seed.widget.resolution = 20
        sc = mlab.scalarbar(
            field_lines, title="Field Strength [T]", orientation="vertical", nb_labels=4
        )
        # horizontal and vertical position from left->right, bottom->top
        sc.scalar_bar_representation.position = np.array([0.9, 0.1])
        # width and height of colourbar
        sc.scalar_bar_representation.position2 = np.array([0.1, 0.8])
        mlab.view(azimuth=42, elevation=73, distance=104)
        mlab.show()

    def line_el(self):
        """
        Function that uses a line element to "look through"
        the magnetic field
        """
        mlab.close(all=True)
        fig = mlab.figure(1, size=(500, 500), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
        field = self.eval_magnetic_field()
        magnitude = mlab.pipeline.extract_vector_norm(field)
        contours = mlab.pipeline.iso_surface(
            magnitude,
            transparent=True,
            contours=3,
            opacity=0.6,
            colormap="YlGnBu",
            vmin=0,
            vmax=0.5,
        )

        field_lines = mlab.pipeline.streamline(
            magnitude,
            seedtype="line",
            integration_direction="both",
            transparent=True,
            opacity=0.3,
            colormap="jet",
            vmin=0,
            vmax=0.5,
        )
        contours.actor.property.frontface_culling = True
        contours.normals.filter.feature_angle = 90
        # fig.scene.axes.cone_radius = 0.1

        field_lines.stream_tracer.maximum_propagation = 150
        field_lines.seed.widget.resolution = 30
        field_lines.seed.widget.point1 = [95, 100.5, 100]  # placing seed
        field_lines.seed.widget.point2 = [105, 100.5, 100]

        sc = mlab.scalarbar(
            field_lines, title="Field Strength [T]", orientation="vertical", nb_labels=4
        )
        # horizontal and vertical position from left->right, bottom->top
        sc.scalar_bar_representation.position = np.array([0.9, 0.1])
        # width and height of colourbar
        sc.scalar_bar_representation.position2 = np.array([0.1, 0.8])
        mlab.view(azimuth=42, elevation=73, distance=104)
        mlab.show()

    def eval_magnetic_field(self, normalise=False):
        R = float(self.e_R.get())
        I = float(self.e_I.get())
        if I == 0:
            return msg.showwarning(
                "WARNING:", "When I=0, \n There is no magnetic field generated"
            )

        x, y, z = np.ogrid[-20:20:200j, -20:20:200j, -20:20:200j]

        rho = np.sqrt(x ** 2 + y ** 2)

        mu = 4 * np.pi * 10.0 ** (-7)  # μ0 constant
        Bz_norm_factor = 1
        Brho_norm_factor = 1
        if normalise:
            Bz_norm_factor = mu / (2 * np.pi)
            Brho_norm_factor = Bz_norm_factor / rho

        E = special.ellipe(
            (4 * R * rho) / ((R + rho) ** 2 + z ** 2)
        )  # special ellipse E
        K = special.ellipk(
            (4 * R * rho) / ((R + rho) ** 2 + z ** 2)
        )  # special ellipse K
        Bz = (
            I
            * Bz_norm_factor
            / ((np.sqrt((R + rho) ** 2 + z ** 2)))
            * (K + (R ** 2 - rho ** 2 - z ** 2) / ((R - rho) ** 2 + z ** 2) * E)
        )
        Brho = (
            I
            * Brho_norm_factor
            * z
            / (rho * np.sqrt((R + rho) ** 2 + z ** 2))
            * (-K + (R ** 2 + rho ** 2 + z ** 2) / ((R - rho) ** 2 + z ** 2) * E)
        )
        del E, K, z

        # Just in case there is a div by zero at the origin
        Brho[np.isnan(Brho)] = 0

        Bx, By = (x / rho) * Brho, (y / rho) * Brho

        del Brho

        field = mlab.pipeline.vector_field(Bx, By, Bz, name="B field")
        del Bx, By, Bz

        return field

    def plot_field(self):
        if self.cb.get() == "line":
            return self.line_el()
        elif self.cb.get() == "plane":
            return self.plane_el()
        elif self.cb.get() == "sphere":
            return self.sphere_el()
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
    root = tk.Tk()
    root.title("Magnetic Field Visualiser")
    root.wm_geometry("550x450")

    # Set the theme
    root.tk.call("source", "themes/sun-valley/sun-valley.tcl")
    root.tk.call("set_theme", "light")

    main = Menu(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("550x400")
    root.mainloop()