import sys
import os
import subprocess
import numpy as np
import tkinter as tk
from mayavi import mlab
from scipy import special
from tkinter import messagebox as msg
import tkinter.font as tkFont
from tkinter.ttk import Combobox

# Externally sourced functionality for TkInter Widgets
from TkInterToolTip import ToolTip

#####################################################
# Menu Externally sourced, supplied by: Bryan Oakley
# link:http://stackoverflow.com/questions/14817210/using-buttons-in-tkinter-to-navigate-to-different-pages-of-the-application
####################################################


class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()

    def quit(self):
        self.root.quit()
        self.root.destroy()

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

        frame = tk.Frame(self)  # Define main frame for the Mayavi GUI
        frame.pack()
        self.Inputs(frame)

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
        dval1 = tk.StringVar(input_frame, value="1.0")  # default value
        dval2 = tk.StringVar(input_frame, value="1.0")  # default value
        # Add Entry widgets
        # @note do not compound .grid on Entry, because it stores a None
        self.e_R = tk.Entry(
            input_frame, textvariable=dval1, validate="key", validatecommand=vcmd
        )
        self.e_R.grid(column=1, row=1, sticky="ew")
        self.e_I = tk.Entry(
            input_frame, textvariable=dval2, validate="key", validatecommand=vcmd
        )
        self.e_I.grid(column=1, row=2, sticky="ew")

        # Plot sphere element Button
        glyphs = ("line", "plane", "sphere")
        self.cb = Combobox(input_frame, values=glyphs, state="readonly")
        self.cb.grid(column=1, row=3, sticky="ew")

        b_plot = tk.Button(input_frame, text="Plot", command=self.plot_field)
        b_plot.grid(column=0, row=6, sticky="ew")

        # Bottom row buttons
        tk.Button(
            input_frame,
            text="Open Report",
            height=1,
            # anchor=tk.W,
            command=self.open_file,
        ).grid(column=0, row=10)

        tk.Button(input_frame, text="Quit", height=1, command=self.quit).grid(
            column=3, row=10
        )

    @staticmethod
    def description(input_frame):
        text_size = tkFont.Font(family="Times New Roman", size=12)
        text = tk.Text(input_frame, width=58, height=8, font=text_size)
        text.config(state=tk.NORMAL)
        text.config(bg="orange", fg="black")
        text.insert(
            tk.INSERT,
            "Mayavi Visualisation Controls:\n \n-Left-click: On the visualisation"
            " element to show more field lines\n-Right-click and Drag: On the"
            " visualisation element to adjust its size\n-Left-click and Drag: On the"
            " visualisation element to move it inside the field\n-Scroll-up\down: To"
            " zoom in\out respectively",
        )
        text.config(state=tk.DISABLED)
        text.grid(column=0, row=8, columnspan=4)

    @staticmethod
    def labels(input_frame):
        tk.Label(
            input_frame,
            text="Radius R",
            # justify=tk.LEFT,
            anchor=tk.W,
            relief=tk.RIDGE,
        ).grid(column=0, row=1)

        tk.Label(
            input_frame,
            text="Current I",
            # justify=tk.LEFT,
            anchor=tk.W,
            relief=tk.RIDGE,
        ).grid(column=0, row=2)

        tk.Label(
            input_frame,
            text="Inspector",
            # justify=tk.LEFT,
            anchor=tk.W,
            relief=tk.RIDGE,
        ).grid(column=0, row=3)

    @staticmethod
    def tool_tips(input_frame):

        # Information Buttons
        info1Text = tk.StringVar()
        info1Text.set("  i  ")
        info1 = tk.Label(input_frame, textvariable=info1Text, relief=tk.RIDGE)
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

        info2Text = tk.StringVar()
        info2Text.set("  i  ")
        info2 = tk.Label(input_frame, textvariable=info2Text, relief=tk.RIDGE)
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

        info3Text = tk.StringVar()
        info3Text.set("  i  ")
        info3 = tk.Label(input_frame, textvariable=info3Text, relief=tk.RIDGE)
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

    def eval_magnetic_field(self, figsize=(500, 500), normalise=False):
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
    main = Menu(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("550x400")
    root.mainloop()