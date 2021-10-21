# -*- coding: utf-8 -*-
# Ioannis Nikiteas, 2015, Royal Holloway University of London
# 3D Simulation of an EM field
import sys
import os
import subprocess
import numpy as np
import tkinter as tk
from mayavi import mlab
from scipy import special
from tkinter import messagebox as msg

# Externally sourced functionality for TkInter Widgets
from TkInterToolTip import ToolTip

#####################################################
# Menu Externally sourced, supplied by: Bryan Oakley
# link:http://stackoverflow.com/questions/14817210/using-buttons-in-tkinter-to-navigate-to-different-pages-of-the-application
####################################################

TITLE_FONT = ("Times New Roman", 18, "bold")


class Menu(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, Visualisation, Report):
            framee = F(container, self)
            self.frames[F] = framee
            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            framee.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, c):
        """Show a frame for the given class"""
        framee = self.frames[c]
        framee.tkraise()

    def quit(self):
        self.root.quit()
        self.root.destroy()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Home Page", font=TITLE_FONT)
        # img = PhotoImage(file="1.gif")             #Image in the background
        # container_lbl = Label(self, image = img)    #not working for some reason
        container_lbl = tk.Label(self, bg="orange")
        container_lbl.pack(side="bottom", fill="both", expand=True)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(
            self,
            text="Go to Magnetic Field Simulation",
            command=lambda: controller.show_frame(Visualisation),
        )
        button2 = tk.Button(
            self, text="Go to Lab Report", command=lambda: controller.show_frame(Report)
        )
        # button3 = Button(self, text="Go to Page Three",
        #                    command=lambda: controller.show_frame(PageThree))
        button1.pack()
        button2.pack()
        # button3.pack()


class Report(tk.Frame):
    def __init__(self, parent, controller):
        """
        Opens the lab report.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Lab Report Tab", font=TITLE_FONT)
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(
            self,
            text="Go to Home Page",
            command=lambda: controller.show_frame(StartPage),
        )
        button.pack()
        frame = tk.Frame(self)
        frame.pack()
        self.Inputs(frame)
        container_lbl = tk.Label(self, bg="orange")
        container_lbl.pack(side="bottom", fill="both", expand=True)

    def Inputs(self, frame):
        input_frame = tk.Frame(frame)
        input_frame.grid(column=0, row=0)

        # Open Report Button
        self.open_report = tk.Button(
            input_frame,
            text="Open Lab Report\n in pdf viewer",
            height=2,
            fg="red",
            command=self.open_file,
        )
        self.open_report.grid(column=0, row=6)

    def open_file(self):
        return subprocess.Popen("a-doc.pdf", shell=True)


class Visualisation(tk.Frame):
    def __init__(self, parent, controller):
        """
        Visualise the magnetic field generated from a loop of wire with
        the help of a GUI.
        """
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(
            self, text="Magnetic Field Simulation of a Single Coil", font=TITLE_FONT
        )
        label.pack(side="top", fill="x", pady=10)
        button = tk.Button(
            self,
            text="Go to Home Page",
            command=lambda: controller.show_frame(StartPage),
        )
        button.pack()
        frame = tk.Frame(self)  # Define main frame for the Mayavi GUI
        frame.pack()
        self.Inputs(frame)

    def Inputs(self, frame):
        """
        Child to: Tk
        ________________________________________________

        Inputs method structures the GUI.
        It contains all the Buttons, Labels and Text boxes
        """
        # Define child frame for the master
        input_frame = tk.Frame(frame)
        input_frame.grid(column=0, row=0)

        # Add Sliders
        self.slR = tk.Scale(input_frame, from_=1.0, to=5.0, orient=tk.HORIZONTAL)
        self.slR.set(1.0)
        self.slR.grid(column=1, row=1)
        self.slI = tk.Scale(input_frame, from_=-5.0, to=5.0, orient=tk.HORIZONTAL)
        self.slI.set(1.0)
        self.slI.grid(column=1, row=2)

        # Plot sphere element Button
        self.seed_sphere = tk.Button(
            input_frame, text="PLOT with \nSphere element", command=self.sphere_el
        )
        self.seed_sphere.grid(column=2, row=6)

        # Plot plane element Button
        self.seed_plane = tk.Button(
            input_frame, text="PLOT with \nPlane element", command=self.plane_el
        )
        self.seed_plane.grid(column=1, row=6)

        # Plot line element Button
        self.plot_button = tk.Button(
            input_frame,
            text=" PLOT with \nLine element",
            height=2,
            fg="red",
            command=self.line_el,
        )
        self.plot_button.grid(column=0, row=6)

        # Text for Mayavi Scenes Controls
        import tkinter.font as tkFont

        text_size = tkFont.Font(family="Times New Roman", size=12)
        text = tk.Text(input_frame, width=58, height=6, font=text_size)
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

        # Labels
        self.labelR = tk.Label(
            input_frame,
            text="Radius R [m]:",
            justify=tk.LEFT,
            anchor=tk.W,
            relief=tk.RIDGE,
        )
        self.labelR.grid(column=0, row=1)
        self.labelI = tk.Label(
            input_frame,
            text="Current I [A]:",
            justify=tk.LEFT,
            anchor=tk.W,
            relief=tk.RIDGE,
        )
        self.labelI.grid(column=0, row=2)
        self.labelbuttons = tk.Label(
            input_frame,
            text="Volume Elements to Visualise the Field :",
            justify=tk.LEFT,
            relief=tk.RIDGE,
        )
        self.labelbuttons.grid(column=0, row=4, columnspan=1, sticky=tk.W)

        # Blank Lines
        self.emptylabel0 = tk.Label(input_frame, text=" ", justify=tk.LEFT)
        self.emptylabel0.grid(column=0, row=3)
        self.emptylabel1 = tk.Label(input_frame, text=" ", justify=tk.LEFT)
        self.emptylabel1.grid(column=0, row=5)
        self.emptylabel3 = tk.Label(input_frame, text=" ", justify=tk.LEFT)
        self.emptylabel3.grid(column=0, row=7, columnspan=4)

        # Information Buttons
        self.info1Text = tk.StringVar()
        self.info1Text.set("  i  ")
        self.info1 = tk.Label(input_frame, textvariable=self.info1Text, relief=tk.RIDGE)
        self.info1.grid(column=2, row=4)

        # Add a tooltip to a widget.
        self.infoToolTip = ToolTip(
            self.info1,
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

        ##################################################################
        self.info2Text = tk.StringVar()
        self.info2Text.set("  i  ")
        self.info2 = tk.Label(input_frame, textvariable=self.info2Text, relief=tk.RIDGE)
        self.info2.grid(column=2, row=2)

        # Add a tooltip to a widget.
        self.infoToolTip = ToolTip(
            self.info2,
            msg=(
                "+The DC current in Amperes flowing through the circular loop.\n+When"
                " the current increases (absolute value),\n the magnetic field strength"
                " increases too.\n+I<0: the direction which the current flows"
                " changes,\n intended for AC simulation but Tkinter only produces"
                " static Mayavi scenes.\n+For I=0 you get a WARNING."
            ),
            delay=0,
        )

        #################################################################
        self.info4Text = tk.StringVar()
        self.info4Text.set("  i  ")
        self.info4 = tk.Label(input_frame, textvariable=self.info4Text, relief=tk.RIDGE)
        self.info4.grid(column=2, row=1)

        # Add a tooltip to a widget.
        self.infoToolTip = ToolTip(
            self.info4,
            msg=(
                "+The radius R from the center of the circular loop in meters.\n+As R"
                " increases the magnetic field strength increases too."
            ),
            delay=0,
        )

    def sphere_el(self):
        """
        Visualising the magnetic field and using as a sphere as a volume
        element to analyse the field and its magnetic field lines
        """
        field, fig = self.eval_magnetic_field()
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
        )

        field_lines.stream_tracer.maximum_propagation = 150.0
        field_lines.seed.widget.radius = 5.5
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

        field, fig = self.eval_magnetic_field()
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
        field, fig = self.eval_magnetic_field()
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
        R = float(self.slR.get())
        I = float(self.slI.get())
        if I == 0:
            return msg.showwarning(
                "WARNING:", "When I=0, \n There is no magnetic field generated"
            )

        x, y, z = [
            i.astype(np.float32)
            for i in np.ogrid[-20:20:200j, -20:20:200j, -20:20:200j]
        ]

        rho = np.sqrt(x ** 2 + y ** 2)
        # Polar decomposition
        x_trans = x / rho  # cos(a) term
        y_trans = y / rho  # sin(a) term
        # Free memory early
        del x, y

        mu = 4 * np.pi * 10.0 ** -7  # μ0 constant
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
        del E, K, z, rho
        # On the axis of the coil we get a divided by zero. This returns a
        # NaN, where the field is actually zero :
        Brho[np.isnan(Brho)] = 0

        Bx, By = x_trans * Brho, y_trans * Brho

        del x_trans, y_trans, Brho
        mlab.close(all=True)
        fig = mlab.figure(1, size=figsize, bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))

        field = mlab.pipeline.vector_field(Bx, By, Bz)
        del Bx, By, Bz

        return (field, fig)


# class PageTwo(Frame):
#
#    def __init__(self, parent, controller):
#        Frame.__init__(self, parent)
#        self.controller = controller
#        label = Label(self, text="LaTex Lab Report", font=TITLE_FONT)
#        label.pack(side="top", fill="x", pady=10)
#        button = Button(self, text="Go to Home Page",
#                           command=lambda: controller.show_frame(StartPage))
#        button.pack()

# class PageThree(Frame):
#
#    def __init__(self, parent, controller):
#        Frame.__init__(self, parent)
#        self.controller = controller
#        label = Label(self, text="This is page 3", font=TITLE_FONT)
#        label.pack(side="top", fill="x", pady=10)
#        button = Button(self, text="Go to the start page",
#                           command=lambda: controller.show_frame(StartPage))
#        button.pack()

if __name__ == "__main__":
    root = tk.Tk()
    main = Menu(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("550x400")
    root.mainloop()