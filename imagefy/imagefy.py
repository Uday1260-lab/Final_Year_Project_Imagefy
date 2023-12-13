"""
imagefy.py : abstract class for the processing of the data.
"""


class IMagefy:
    """ IMagefy is an abstract class for the processing of the data """
    EDSR_MODEL_X2_PATH = "static/models/EDSR/EDSR_x2.pb"
    EDSR_MODEL_X3_PATH = "static/models/EDSR/EDSR_x3.pb"
    EDSR_MODEL_X4_PATH = "static/models/EDSR/EDSR_x4.pb"

    def __init__(self) -> None:
        self.url = ""
