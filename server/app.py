import base64
import json
import logging
import sys
import traceback
from typing import Union, List

from fastapi import FastAPI
from fastapi.responses import JSONResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from groundstation import GroundStation

import models
from errors import InvalidRequestError, InvalidStateError, GeneralError, ServiceUnavailableError

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

with open("config.json", "r") as file:
    config = json.load(file)

app = FastAPI(
    title="TJUAV GroundStation Backend",
    description="""
#### TJUAV's custom GroundStation for the AUVSI SUAS Contest, with an awesome UI and an implementation of Telemetry, Image Processing/Submission, and Autonomous Flight Control!

## Documentation:
 - `/` [Overview](/) - Served using Swagger UI 

 - `/docs` [Interactive Docs](/docs) - Served using ReDoc

""",
    docs_url="/",
    redoc_url="/docs"
)


logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)-8s]  %(message)s")

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING)
console_handler.setFormatter(formatter)

file_handler = logging.FileHandler("log.txt", mode="w")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

debug_file_handler = logging.FileHandler("debug_log.txt", mode="w")
debug_file_handler.setLevel(logging.DEBUG)
debug_file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(debug_file_handler)

print("LOGGING STARTED")
logger.info("LOGGING STARTED")


origins = [
    "http://localhost:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

gs = GroundStation()


@app.exception_handler(InvalidRequestError)
def handle_400(r, e):
    logger.error(type(e).__name__)
    logger.info("Traceback of %s : ", type(e).__name__, exc_info=e)
    return JSONResponse(
        status_code=400,
        content={
            "title": "Invalid Request",
            "message": str(e),
            "exception": type(e).__name__,
            "traceback": traceback.format_tb(e.__traceback__)
        }
    )


@app.exception_handler(InvalidStateError)
def handle_409(r, e):
    logger.error(type(e).__name__)
    logger.info("Traceback of %s : ", type(e).__name__, exc_info=e)
    return JSONResponse(
        status_code=409,
        content={
            "title": "Invalid State",
            "message": str(e),
            "exception": type(e).__name__,
            "traceback": traceback.format_tb(e.__traceback__)
        }
    )


@app.exception_handler(RequestValidationError)
def handle_422(r, e):
    logger.error(type(e).__name__)
    logger.info("Traceback of %s : ", type(e).__name__, exc_info=e)
    return JSONResponse(
        status_code=422,
        content={
            "title": "Request Validation Failed",
            "message": str(e),
            "exception": type(e).__name__,
            "traceback": traceback.format_tb(e.__traceback__)
        }
    )


@app.exception_handler(ServiceUnavailableError)
def handle_503(r, e):
    logger.error(type(e).__name__)
    logger.info("Traceback of %s : ", type(e).__name__, exc_info=e)
    return JSONResponse(
        status_code=503,
        content={
            "title": "Service Unavailable",
            "message": str(e),
            "exception": type(e).__name__,
            "traceback": traceback.format_tb(e.__traceback__)
        }
    )


@app.exception_handler(GeneralError)
@app.exception_handler(Exception)
def handle_500(r, e):
    logger.error(type(e).__name__)
    logger.info("Traceback of %s : ", type(e).__name__, exc_info=e)
    return JSONResponse(
        status_code=500,
        content={
            "title": "Server Error",
            "message": str(e),
            "exception": type(e).__name__,
            "traceback": traceback.format_tb(e.__traceback__)
        }
    )


@app.post(
    "/interop/login",
    response_model=models.GeneralOut,
    responses={
        409: {"model": models.ExceptionHandler},  # InvalidStateError
        500: {"model": models.ExceptionHandler},  # GeneralError
        503: {"model": models.ExceptionHandler}  # ServiceUnavailableError
    },
    response_description="A successful login",
    description="Forces a login attempt to the Interop Server",
    status_code=201,
    tags=["Interoperability (interop)"]
)
def interop_login():
    return gs.call("i_login")


@app.get(
    "/interop/mission",
    response_model=models.MissionOut,
    responses={
        500: {"model": models.ExceptionHandler},  # GeneralError
        503: {"model": models.ExceptionHandler}  # ServiceUnavailableError
    },
    description="Retreives all mission data",
    status_code=200,
    tags=["Interoperability (interop)"]
)
def interop_mission():
    return gs.call("i_mission")


@app.get(
    "/interop/telemetry",
    response_model=models.TelemetryOut,
    responses={
        500: {"model": models.ExceptionHandler}  # GeneralError
    },
    status_code=200,
    tags=["Interoperability (interop)"]
)
def interop_telemetry():
    return gs.call("i_telemetry")


# @app.route("/interop/odlc/list")
# def odlc_list():
#     return gs.call("i_odlcget")
#
#
# @app.route("/interop/odlc/filter/<int:status>")  # 0: Not Reviewed, 1: Submitted, 2: Rejected
# def odlc_filter(status):
#     return gs.call("i_odlcget", status)
#
#
# @app.route("/interop/odlc/image/<int:id_>")
# def odlc_get_image(id_):
#     with open(f"assets/odlc_images/{id_}.jpg", "rb") as image_file:
#         encoded_string = base64.b64encode(image_file.read())
#     return {"image": encoded_string.decode("utf-8")}
#
#
# @app.route("/interop/odlc/add", methods=["POST"])
# def odlc_add():
#     f = request.form
#     if not all(field in f for field in ["image", "type", "lat", "lon"]):
#         raise InvalidRequestError("Missing required fields in request")
#     if f.get("type") == "standard":
#         if not all(field in f for field in ["orientation", "shape", "shape_color", "alpha", "alpha_color"]):
#             raise InvalidRequestError("Missing required fields for specific ODLC type")
#     else:
#         if not all(field in f for field in ["description"]):
#             raise InvalidRequestError("Missing required fields for specific ODLC type")
#     return gs.call("i_odlcadd",
#                    f.get("image"),
#                    f.get("type"),
#                    float(f.get("lat")),
#                    float(f.get("lon")),
#                    int(f.get("orientation")),
#                    f.get("shape"),
#                    f.get("shape_color"),
#                    f.get("alpha"),
#                    f.get("alpha_color"),
#                    f.get("description")
#                    )
#
#
# @app.route("/interop/odlc/edit/<int:id_>", methods=["POST"])
# def odlc_edit(id_):
#     f = request.form
#     if not all(field in f for field in ["type"]):
#         raise InvalidRequestError("Missing required fields in request")
#     return gs.call("i_odlcedit",
#                    id_,
#                    f.get("type"),
#                    float(f.get("lat")),
#                    float(f.get("lon")),
#                    int(f.get("orientation")),
#                    f.get("shape"),
#                    f.get("shape_color"),
#                    f.get("alpha"),
#                    f.get("alpha_color"),
#                    f.get("description")
#                    )
#
#
# @app.route("/interop/odlc/reject/<int:id_>", methods=["POST"])
# def odlc_reject(id_):
#     return gs.call("i_odlcreject", id_)
#
#
# @app.route("/interop/odlc/submit/<int:id_>", methods=["POST"])
# def odlc_submit(id_):
#     return gs.call("i_odlcsubmit", id_)
#
#
# @app.route("/interop/odlc/save", methods=["POST"])
# def odlc_save():
#     return gs.call("i_odlcsave")
#
#
# @app.route("/interop/odlc/load", methods=["POST"])
# def odlc_load():
#     return gs.call("i_odlcload")
#
#
# @app.route("/interop/map/add", methods=["POST"])
# def map_add():
#     f = request.form
#     if not all(field in f for field in ["name", "image"]):
#         raise InvalidRequestError("Missing required fields in request")
#     return gs.call("i_mapadd", f.get("name"), f.get("image"))
#
#
# @app.route("/interop/map/submit", methods=["POST"])
# def map_submit():
#     f = request.form
#     if not all(field in f for field in ["name"]):
#         raise InvalidRequestError("Missing required fields in request")
#     return gs.call("i_mapsubmit", f.get("name"))
#
#
# @app.route("/uav/connect", methods=["POST"])
# def connect():
#     return gs.call("m_connect")
#
#
# @app.route("/uav/update", methods=["POST"])
# def update():
#     return gs.call("m_update")
#
#
@app.get(
    "/uav/quick",
    response_model=models.QuickOut,
    status_code=200,
    tags=["Unmanned Aerial Vehicle (UAV)"]
)
def quick():
    return gs.call("m_quick")
#
#
# @app.route("/uav/stats")
# def stats():
#     return gs.call("m_stats")
#
#
# @app.route("/uav/mode/get")
# def get_mode():
#     return gs.call("m_getflightmode")
#
#
# @app.route("/uav/mode/set", methods=["POST"])
# def set_mode():
#     f = request.form
#     if not all(field in f for field in ["mode"]):
#         raise InvalidRequestError("Missing required fields in request")
#     return gs.call("m_setflightmode", f.get("mode"))
#
#
# @app.route("/uav/params/get/<key>")
# def get_param(key):
#     return gs.call("m_getparam", key)
#
#
# @app.route("/uav/params/getall")
# def get_params():
#     return gs.call("m_getparams")
#
#
# @app.route("/uav/params/set/<key>/<value>", methods=["POST"])
# def set_param(key, value):
#     return gs.call("m_setparam", key, value)
#
#
# @app.route("/uav/params/setmultiple", methods=["POST"])
# def set_params():
#     f = request.form
#     if not all(field in f for field in ["params"]):
#         raise InvalidRequestError("Missing required fields in request")
#     return gs.call("m_setparams", f.get("params"))  # {"param": "newvalue"}
#
#
# @app.route("/uav/params/save", methods=["POST"])
# def save_params():
#     return gs.call("m_saveparams")
#
#
# @app.route("/uav/params/load", methods=["POST"])
# def load_params():
#     return gs.call("m_loadparams")
#
#
# @app.route("/uav/commands/get")
# def get_commands():
#     return gs.call("m_getcommands")
#
#
# @app.route("/uav/commands/insert", methods=["POST"])
# def insert_command():
#     f = request.form
#     if not all(field in f for field in ["command", "lat", "lon", "alt"]):
#         raise InvalidRequestError("Missing required fields in request")
#     return gs.call("m_insertcommand",
#                    f.get("command"),
#                    f.get("lat"),
#                    f.get("lon"),
#                    f.get("alt")
#                    )
#
#
# @app.route("/uav/commands/clear", methods=["POST"])
# def clear_commands():
#     return gs.call("m_clearcommands")
#
#
# @app.route("/uav/getarmed")
# def armed():
#     return gs.call("m_getarmed")
#
#
# @app.route("/uav/arm", methods=["POST"])
# def arm():
#     return gs.call("m_arm")
#
#
# @app.route("/uav/disarm", methods=["POST"])
# def disarm():
#     return gs.call("m_disarm")
