import gc
from typing import Tuple
import numpy as np
from mayavi import mlab
from mayavi.modules.iso_surface import IsoSurface
from mayavi.modules.streamline import Streamline
from scipy import special


class MagneticField(object):
    def __init__(self) -> None:
        pass

    @staticmethod
    def sphere_el(radius: float, current: float) -> None:
        fig = mlab.figure(1, size=(800, 600), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
        B = MagneticField.magnetic_field_single_coil(radius, current)
        field = mlab.pipeline.vector_field(B[0], B[1], B[2], name="B field")
        magnitude = mlab.pipeline.extract_vector_norm(field)
        contours: IsoSurface = mlab.pipeline.iso_surface(
            magnitude,
            contours=3,
            transparent=True,
            opacity=0.6,
            colormap="YlGnBu",
            vmin=0,
            vmax=0.5,
        )

        streamlines: Streamline = mlab.pipeline.streamline(
            magnitude,
            seedtype="sphere",
            integration_direction="both",
            transparent=True,
            opacity=0.3,
            colormap="jet",
            vmin=0,
            vmax=0.5,
        )

        contours.actor.property.frontface_culling = True
        contours.normals.filter.feature_angle = 90

        streamlines.stream_tracer.maximum_propagation = 150
        streamlines.seed.widget.radius = 4
        streamlines.seed.widget.seed_resolution = 12
        MagneticField.style(streamlines)

        del field, streamlines, contours, magnitude, B, fig

    @staticmethod
    def plane_el(radius: float, current: float) -> None:
        fig = mlab.figure(1, size=(800, 600), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
        B = MagneticField.magnetic_field_single_coil(radius, current)
        field = mlab.pipeline.vector_field(B[0], B[1], B[2], name="B field")
        magnitude = mlab.pipeline.extract_vector_norm(field)
        contours: IsoSurface = mlab.pipeline.iso_surface(
            magnitude,
            transparent=True,
            contours=3,
            opacity=0.6,
            colormap="YlGnBu",
            vmin=0,
            vmax=0.5,
        )

        streamlines: Streamline = mlab.pipeline.streamline(
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

        streamlines.stream_tracer.maximum_propagation = 40.0
        streamlines.seed.widget.resolution = 20
        streamlines.seed.widget.handle_size = 0.5
        streamlines.seed.widget.representation = "outline"
        MagneticField.style(contours)

        # @note
        # The garbage collection does not work for streamlines that results into
        #  all the memory in the heap not being able to be freed
        field.remove()

        # streamlines.stream_tracer.remove_all_inputs
        # streamlines.stream_tracer.remove_all_observers
        # streamlines.remove()
        # del streamlines
        del field, magnitude, contours, B, fig
        gc.collect()

    @staticmethod
    def line_el(radius: float, current: float) -> None:
        fig = mlab.figure(1, size=(800, 600), bgcolor=(1, 1, 1), fgcolor=(0, 0, 0))
        B = MagneticField.magnetic_field_single_coil(radius, current)
        field = mlab.pipeline.vector_field(B[0], B[1], B[2], name="B field")
        magnitude = mlab.pipeline.extract_vector_norm(field)
        contours: IsoSurface = mlab.pipeline.iso_surface(
            magnitude,
            transparent=True,
            contours=3,
            opacity=0.6,
            colormap="YlGnBu",
            vmin=0,
            vmax=0.5,
        )

        streamlines: Streamline = mlab.pipeline.streamline(
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

        streamlines.stream_tracer.maximum_propagation = 150
        streamlines.seed.widget.resolution = 30
        streamlines.seed.widget.point1 = [95, 100.5, 100]  # placing seed
        streamlines.seed.widget.point2 = [105, 100.5, 100]

        MagneticField.style(contours)

        del field, streamlines, contours, magnitude, B, fig

    @staticmethod
    def draw_circle(radius):
        l = 200
        theta = np.linspace(0, 2 * np.pi, l)
        y = radius * np.sin(theta)
        x = radius * np.cos(theta)
        z = np.zeros(l)
        return mlab.points3d(x, y, z)

    @staticmethod
    def magnetic_field_single_coil(
        radius: float, current: float, normalise: bool = False
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculate the magnetic field of a single coil loop

        The equations in Cylindrical coordinates are given by:
        .. math::
        B_z = \frac{\mu_0I}{2\pi}\frac{1}{[(R + \rho)^2 + z^2]^{1/2}} \times
            \left[K(k^2)+\frac{R^2 - \rho^2 - z^2}{(R-\rho)^2 + z^2}E(k^2)\right]
        B_\rho = \frac{\mu_0I}{2\pi\rho} \frac{z}{[R+\rho)^2 +z^2]^{1/2}} \times
            \left[-K(k^2) + E(k^2)\frac{R^2+\rho^2+z^2}{(R-\rho)^2+z^2}\right]

        where K and E are the elliptic integrals
        Args:
            radius (float): radius of the coil
            current (float): current through the coil
            normalise (bool, optional): normalise field. Defaults to False.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: Magnetic field in Cartesian coordinates
        """

        R = radius
        I = current
        if abs(radius) < 1e-10:
            R = 1e-10
        if abs(current) < 1e-10:
            I = 1e-10
        Lx = 20
        Ly = 20
        Lz = 20

        x, y, z = np.ogrid[-Lx:Lx:200j, -Ly:Ly:200j, -Lz:Lz:200j]
        rho = np.sqrt(x ** 2 + y ** 2)
        # theta = np.arctan(x/y)
        # theta[y==0] = 0

        mu = 4 * np.pi * 10.0 ** (-7)  # μ0 constant
        Bz_norm_factor = 1
        Brho_norm_factor = 1
        if normalise:
            Bz_norm_factor = mu / (2 * np.pi)
            Brho_norm_factor = Bz_norm_factor / rho

        # Special ellipse E and K
        E = special.ellipe((4 * R * rho) / ((R + rho) ** 2 + z ** 2))
        K = special.ellipk((4 * R * rho) / ((R + rho) ** 2 + z ** 2))
        Bz = (
            I
            * Bz_norm_factor
            / (np.sqrt((R + rho) ** 2 + z ** 2))
            * (K + (R ** 2 - rho ** 2 - z ** 2) / ((R - rho) ** 2 + z ** 2) * E)
        )
        Brho = (
            I
            * Brho_norm_factor
            * z
            / (rho * np.sqrt((R + rho) ** 2 + z ** 2))
            * (-K + (R ** 2 + rho ** 2 + z ** 2) / ((R - rho) ** 2 + z ** 2) * E)
        )

        # At origin we get division by zero which yields NaN, physically the
        # field is zero in that location
        Brho[np.isnan(Brho)] = 0
        Brho[np.isinf(Brho)] = 0
        Bz[np.isnan(Bz)] = 0
        Bz[np.isinf(Bz)] = 0

        # Bx, By = np.cos(theta) * Brho, np.sin(theta) * Brho
        Bx, By = (x / rho) * Brho, (y / rho) * Brho

        del Brho, E, K, x, y, z

        return Bx, By, Bz

    @staticmethod
    # @mlab.show
    def style(streamlines, **kwargs) -> None:
        sc = mlab.scalarbar(
            streamlines,
            title="Field\nStrength [T]",
            orientation="vertical",
            nb_labels=4,
        )
        # horizontal and vertical position from left->right, bottom->top
        sc.scalar_bar_representation.position = np.array([0.85, 0.1])
        # width and height of colourbar
        sc.scalar_bar_representation.position2 = np.array([0.1, 0.8])
        # The title of colourbar does not scale so we need to manually set it
        sc.scalar_bar.unconstrained_font_size = True
        sc.title_text_property.font_size = 20
        sc.label_text_property.font_size = 20
        ax = mlab.axes()
        mlab.view(azimuth=42, elevation=73, distance=104)


if __name__ == "__main__":
    MagneticField.line_el(1.0, 1.0)
