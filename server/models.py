from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class ExceptionHandler(BaseModel):
    title: str = Field(..., description="The type of exception thrown.", example="GeneralError")
    message: str = Field(..., description="The exact syntax error that caused the exception.",
                         example="Attempted to distort spacetime continuum.")
    exception: str = Field(..., description="The base exception type.", example="SpaceTimeError")
    traceback: List[str] = Field(..., description="A list of traceback lines used for debugging.")


class LatLonDict(BaseModel):
    latitude: float = Field(..., description="Latitude of GPS position in degrees.", gt=-180,
                            le=180, example=38.908233)
    longitude: float = Field(..., description="Longitude of GPS position in degrees.", gt=-180,
                             le=180, example=-77.180142)


class LatLonAltDict(LatLonDict):
    altitude: int = Field(..., description="Altitude above mean sea level (MSL) in feet.",
                          example=150)


class TelemetryDict(LatLonAltDict):
    heading: int = Field(..., description="Heading relative to true north in degrees.", ge=0,
                         lt=360, example=270)


class ObstacleDict(LatLonDict):
    radius: int = Field(..., description="Radius of the obstacle cylinder in feet.", ge=0,
                        example=150)
    height: int = Field(
        ...,
        description="Height of the obstacle cylinder above mean sea level (MSL) in feet.", ge=0,
        example=650
    )


class FlyZoneDict(BaseModel):
    altitudeMin: int = Field(...,
                             description="Minimum altitude above mean sea level (MSL) in feet.",
                             ge=0, example=100)
    altitudeMax: int = Field(...,
                             description="Maximum altitude above mean sea level (MSL) in feet.",
                             ge=0, example=750)
    boundaryPoints: List[LatLonDict] = Field(
        ..., description="Boundary points which define a closed polygon.")


class OrientationDict(BaseModel):
    yaw: int = Field(..., description="Heading relative to true north in degrees.", ge=0, lt=360,
                     example=270)
    roll: int = Field(..., description="Roll relative to parallel position in degrees.", gt=-180,
                      le=180, example=24)
    pitch: int = Field(..., description="Pitch relative to parallel position in degrees.", gt=-180,
                       le=180, example=3)


class MissionDict(BaseModel):
    id: int = Field(..., description="Unique identifier for the mission.", example=1)
    lostCommsPos: LatLonDict = Field(
        ..., description="Lost comms position for RTH/RTL and flight termination.")
    flyZones: List[FlyZoneDict] = Field(
        ..., description="Valid areas to fly. A team is out of bounds if not contained within.")
    waypoints: List[LatLonAltDict] = Field(
        ..., description="Sequence of waypoints teams must fly.")
    searchGridPoints: List[LatLonDict] = Field(
        ..., description="Search grid containing ODLCs. Positions define a closed polygon.")
    offAxisOdlcPos: LatLonDict = Field(
        ..., description="Position of the off-axis ODLC.")
    emergentLastKnownPos: LatLonDict = Field(
        ..., description="Last known position of the emergent ODLC.")
    airDropBoundaryPoints: List[LatLonDict] = Field(
        ..., description="Boundary for the air drop and UGV drive.")
    airDropPos: LatLonDict = Field(..., description="Position of the air drop location.")
    ugvDrivePos: LatLonDict = Field(..., description="Position the UGV must drive to.")
    stationaryObstacles: List[ObstacleDict] = Field(..., description="Stationary obstacles.")
    mapCenterPos: LatLonDict = Field(..., description="Desired position of the generated map.")
    mapHeight: int = Field(..., description="Desired height of the generated map in feet.", ge=0,
                           example=1200)


class QuickDict(BaseModel):
    altitude: float = Field(..., description="Altitude above mean sea level (MSL) in feet.", ge=0,
                            example=150)
    orientation: OrientationDict = Field(..., description="Orientation values.")
    ground_speed: float = Field(..., description="Speed measured from the ground in mph.", ge=0,
                                example=56.829)
    air_speed: float = Field(..., description="Speed measured from the air in mph.", ge=0,
                             example=54.735)
    dist_to_wp: float = Field(..., description="Distance from the next waypoint in feet.", ge=0,
                              example=152.876)
    voltage: float = Field(..., description="Current voltage of the battery.", ge=0, lt=20,
                           example=14.358)  # Ideally 16V, but a 0-20V range is provided
    throttle: int = Field(..., description="Current throttle percentage.", ge=0, le=100, example=65)
    lat: float = Field(..., description="Latitude of GPS position in degrees.", gt=-180, le=180,
                       example=38.908233)
    lon: float = Field(..., description="Longitude of GPS position in degrees.", gt=-180, le=180,
                       example=-77.180142)


class MissionIn(str, Enum):
    mission = "mission"
    waypoints = "waypoints"
    obstacles = "obstacles"
    teams = "teams"
    search = "search"
    ugv = "ugv"
    odlc = "odlc"
    lost_comms = "lost_comms"


class GeneralOut(BaseModel):
    result: dict


class MissionOut(BaseModel):
    result: MissionDict = Field(..., description="Details for a mission.")


class TelemetryOut(BaseModel):
    result: TelemetryDict = Field(..., description="UAS telemetry teams must upload.")


class QuickOut(BaseModel):
    result: QuickDict = Field(..., description="Quick UAV Data.")

