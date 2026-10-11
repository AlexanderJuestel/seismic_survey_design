import pyproj
import pytest

from seismic_survey_design.survey3d import Survey3D


class TestSurvey3D:
    """Tests for the Survey3D class."""

    def test_default_initialization(self):
        """Optional parameters should accept None."""
        survey = Survey3D()

        assert survey.design_name is None
        assert survey.project_name is None
        assert survey.project_location is None
        assert survey.license_name is None
        assert survey.target_name_shallow is None
        assert survey.target_name_deep is None

        assert survey.z_min is None
        assert survey.z_max is None
        assert survey.x_min is None
        assert survey.x_max is None
        assert survey.x_max_to_z_max_ratio is None

        assert survey.theta_inline is None
        assert survey.theta_crossline is None
        assert survey.target_size is None

        assert survey.crs == pyproj.CRS.from_epsg(25832)

    def test_parameter_initialization(self):
        """Valid parameters should be stored correctly."""
        survey = Survey3D(
            design_name="Survey Design 1",
            project_name="Reallabor Geothermie Rheinland",
            project_location="Aachen-Weisweiler",
            license_name="Aachen-Weisweiler",
            target_name_shallow="Base Tertiary",
            target_name_deep="Kohlenkalk/Massenkalk",
            z_min=50,
            z_max=4000,
            theta_inline=30,
            theta_crossline=30,
            target_size=50,
            crs="EPSG:4647",
        )

        assert survey.design_name == "Survey Design 1"
        assert survey.project_name == "Reallabor Geothermie Rheinland"
        assert survey.project_location == "Aachen-Weisweiler"
        assert survey.license_name == "Aachen-Weisweiler"
        assert survey.target_name_shallow == "Base Tertiary"
        assert survey.target_name_deep == "Kohlenkalk/Massenkalk"

        assert survey.z_min == 50
        assert survey.z_max == 4000
        assert survey.x_min == 50
        assert survey.x_max == 4000
        assert survey.x_max_to_z_max_ratio == 1

        assert survey.theta_inline == 30
        assert survey.theta_crossline == 30
        assert survey.target_size == 50

        assert survey.crs == pyproj.CRS.from_epsg(4647)

    def test_explicit_x_max_initialization(self):
        """An explicitly provided x_max should override its default."""
        survey = Survey3D(
            z_min=50,
            z_max=4000,
            x_max=3000,
        )

        assert survey.z_min == 50
        assert survey.z_max == 4000
        assert survey.x_min == 50
        assert survey.x_max == 3000
        assert survey.x_max_to_z_max_ratio == pytest.approx(0.75)
        assert survey.crs == pyproj.CRS.from_epsg(25832)

    # ------------------------------------------------------------------
    # String parameters
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "parameter",
        [
            "design_name",
            "project_name",
            "project_location",
            "license_name",
            "target_name_shallow",
            "target_name_deep",
        ],
    )
    @pytest.mark.parametrize("value", [0, 0.0, True, False])
    def test_rejects_invalid_string_parameter_types(self, parameter, value):
        """String parameters should reject non-string values."""
        with pytest.raises(TypeError, match=parameter):
            Survey3D(**{parameter: value})

    # ------------------------------------------------------------------
    # z_min and z_max
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("parameter", ["z_min", "z_max"])
    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_depth_types(self, parameter, value):
        """Depth parameters should reject unsupported types."""
        with pytest.raises(TypeError, match=parameter):
            Survey3D(**{parameter: value})

    @pytest.mark.parametrize("parameter", ["z_min", "z_max"])
    @pytest.mark.parametrize("value", [0, 0.0, -1, -1.0])
    def test_rejects_nonpositive_depths(self, parameter, value):
        """Provided target depths must be greater than zero."""
        with pytest.raises(ValueError, match=parameter):
            Survey3D(**{parameter: value})

    def test_rejects_z_max_not_greater_than_z_min(self):
        """z_max must be greater than z_min when both are provided."""
        with pytest.raises(ValueError, match="z_max"):
            Survey3D(z_min=1000, z_max=500)

    def test_accepts_equal_z_min_and_z_max_only_when_unrelated(self):
        """A valid z_min can be set without specifying z_max."""
        survey = Survey3D(z_min=1000)

        assert survey.z_min == 1000
        assert survey.z_max is None

    # ------------------------------------------------------------------
    # x_max
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_x_max_types(self, value):
        """x_max should reject unsupported types."""
        with pytest.raises(TypeError, match="x_max"):
            Survey3D(x_max=value)

    @pytest.mark.parametrize("value", [0, 0.0, -1, -1.0])
    def test_rejects_nonpositive_x_max(self, value):
        """A provided x_max must be greater than zero."""
        with pytest.raises(ValueError, match="x_max"):
            Survey3D(x_max=value)

    def test_rejects_x_max_smaller_than_x_min(self):
        """x_max must not be smaller than x_min."""
        with pytest.raises(ValueError, match="x_max"):
            Survey3D(z_min=1000, x_max=500)

    def test_accepts_x_max_equal_to_x_min(self):
        """x_max may equal x_min."""
        survey = Survey3D(
            z_min=1000,
            z_max=2000,
            x_max=1000,
        )

        assert survey.x_max == survey.x_min == 1000

    def test_accepts_x_max_greater_than_x_min(self):
        """x_max may be greater than x_min."""
        survey = Survey3D(
            z_min=1000,
            z_max=2000,
            x_max=1500,
        )

        assert survey.x_max == 1500
        assert survey.x_min == 1000

    @pytest.mark.parametrize(
        ("z_max", "x_max", "expected_ratio"),
        [
            (4000, None, 1.0),
            (4000, 3000, 0.75),
            (2000, 1500, 0.75),
        ],
    )
    def test_calculates_x_max_to_z_max_ratio(self, z_max, x_max, expected_ratio):
        """The ratio should be calculated correctly."""
        survey = Survey3D(
            z_min=100,
            z_max=z_max,
            x_max=x_max,
        )

        assert survey.x_max_to_z_max_ratio == pytest.approx(expected_ratio)

    # ------------------------------------------------------------------
    # Target dipping angles
    # ------------------------------------------------------------------

    @pytest.mark.parametrize(
        "parameter",
        ["theta_inline", "theta_crossline"],
    )
    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_dipping_angle_types(self, parameter, value):
        """Dipping angles should reject unsupported types."""
        with pytest.raises(TypeError, match=parameter):
            Survey3D(**{parameter: value})

    @pytest.mark.parametrize(
        "parameter",
        ["theta_inline", "theta_crossline"],
    )
    @pytest.mark.parametrize(
        "value",
        [-5, 0, 0.0, 90, 90.0, 100],
    )
    def test_rejects_dipping_angle_outside_valid_range(self, parameter, value):
        """Dipping angles must be strictly between 0 and 90 degrees."""
        with pytest.raises(ValueError, match=parameter):
            Survey3D(**{parameter: value})

    @pytest.mark.parametrize(
        "parameter",
        ["theta_inline", "theta_crossline"],
    )
    @pytest.mark.parametrize("value", [0.1, 30, 89.9])
    def test_accepts_valid_dipping_angles(self, parameter, value):
        """Dipping angles inside the valid range should be accepted."""
        survey = Survey3D(**{parameter: value})

        assert getattr(survey, parameter) == value

    # ------------------------------------------------------------------
    # Target size
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", ["invalid", True, False])
    def test_rejects_invalid_target_size_types(self, value):
        """target_size should reject unsupported types."""
        with pytest.raises(TypeError, match="target_size"):
            Survey3D(target_size=value)

    @pytest.mark.parametrize("value", [0, 0.0, -1, -1.0])
    def test_rejects_nonpositive_target_size(self, value):
        """A provided target_size must be greater than zero."""
        with pytest.raises(ValueError, match="target_size"):
            Survey3D(target_size=value)

    @pytest.mark.parametrize("value", [0.1, 50, 1000])
    def test_accepts_positive_target_size(self, value):
        """Positive target sizes should be accepted."""
        survey = Survey3D(target_size=value)

        assert survey.target_size == value

    # ------------------------------------------------------------------
    # Coordinate reference system
    # ------------------------------------------------------------------

    @pytest.mark.parametrize("value", [0, 0.0, True, False, None])
    def test_rejects_invalid_crs_types(self, value):
        """CRS must be a string or a pyproj.CRS object."""
        with pytest.raises(TypeError, match="CRS"):
            Survey3D(crs=value)

    def test_accepts_pyproj_crs(self):
        """A pyproj.CRS object should be accepted."""
        crs = pyproj.CRS.from_epsg(25832)

        survey = Survey3D(crs=crs)

        assert survey.crs == crs
        assert isinstance(survey.crs, pyproj.CRS)

    def test_accepts_crs_string(self):
        """A valid CRS string should be converted to pyproj.CRS."""
        survey = Survey3D(crs="EPSG:25832")

        assert survey.crs == pyproj.CRS.from_epsg(25832)
        assert isinstance(survey.crs, pyproj.CRS)

    def test_rejects_invalid_crs_string(self):
        """An invalid CRS string should raise ValueError."""
        with pytest.raises(ValueError, match="Invalid CRS"):
            Survey3D(crs="kein-koordinatensystem")
