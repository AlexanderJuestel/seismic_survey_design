import pyproj

from seismic_survey_design.io import _validate_float_int, _validate_string


class Survey3D:
    def __init__(
        self,
        design_name: str | None = None,
        project_name: str | None = None,
        project_location: str | None = None,
        license_name: str | None = None,
        target_name_shallow: str | None = None,
        target_name_deep: str | None = None,
        z_min: float | None = None,
        z_max: float | None = None,
        x_max: float | None = None,
        target_size: float | None = None,
        theta_inline: float | None = None,
        theta_crossline: float | None = None,
        crs: str | pyproj.CRS = "EPSG:25832",
    ):
        #################################################
        # General
        #################################################
        self.design_name = _validate_string(arg=design_name, name="design_name")

        self.project_name = _validate_string(arg=project_name, name="project_name")

        self.project_location = _validate_string(
            arg=project_location, name="project_location"
        )

        self.license_name = _validate_string(arg=license_name, name="license_name")

        if not isinstance(crs, (str, pyproj.CRS)):
            raise TypeError("The CRS must be provided as a string or pyproj CRS object")

        try:
            self.crs = pyproj.CRS.from_user_input(crs)
        except (pyproj.exceptions.CRSError, ValueError) as exc:
            raise ValueError(f"Invalid CRS: {crs!r}") from exc

        #################################################
        # Target
        #################################################
        # Target Depths
        self.target_name_shallow = _validate_string(
            arg=target_name_shallow, name="target_name_shallow"
        )

        self.target_name_deep = _validate_string(
            arg=target_name_deep, name="target_name_deep"
        )

        self.z_min = _validate_float_int(arg=z_min, name="z_min", greater_than=0)

        self.z_max = _validate_float_int(arg=z_max, name="z_max", greater_than=0)

        if (
            self.z_min is not None
            and self.z_max is not None
            and self.z_max <= self.z_min
        ):
            raise ValueError("'z_max' must be greater than 'z_min'")

        validated_x_max = _validate_float_int(
            arg=x_max,
            name="x_max",
            greater_than=0,
        )

        # Target Offsets
        self.x_min = self.z_min
        self.x_max = self.z_max if validated_x_max is None else validated_x_max

        if (
            self.x_max is not None
            and self.x_min is not None
            and self.x_max < self.x_min
        ):
            raise ValueError("'x_max' must be greater than or equal to 'x_min'")

        self.x_max_to_z_max_ratio = (
            self.x_max / self.z_max
            if self.x_max is not None and self.z_max is not None
            else None
        )

        # Target Dipping Angle
        self.theta_inline = _validate_float_int(
            arg=theta_inline, name="theta_inline", greater_than=0, smaller_than=90
        )

        self.theta_crossline = _validate_float_int(
            arg=theta_crossline, name="theta_crossline", greater_than=0, smaller_than=90
        )

        # Target Size
        self.target_size = _validate_float_int(
            arg=target_size, name="target_size", greater_than=0
        )
