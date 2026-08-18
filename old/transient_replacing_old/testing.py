"""
BESS replacement script.

This script replaces existing BESS units in the active EMTP design with the
standard CEN BESS template, preserving the original electrical connection,
positioning, name, operating point and selected sizing parameters.

Only ordering and comments were added. The original execution logic is kept.
"""

from unit_extractor import *

library_path = "C:\\Users\\gonzalo.sanchez\\OneDrive - Coordinador Eléctrico Nacional\\C01. Simulación y Laboratorio en Tiempo Real\\04. EMTP Modelo Eléctrico\\09. Templates Reemplazo\\CEN Devices.clf"


if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # EMTP session and library initialization
    # -------------------------------------------------------------------------
    emtp_client = EmtpComClient(attach_existing=True)
    self.emtp_object = emtp_client.emtp_object

    if not self.emtp_object.currentDesign:
        Design.open_design(emtp_object=self.emtp_object)

    Library.open_library(emtp_object=self.emtp_object, library_path=library_path)

    # -------------------------------------------------------------------------
    # Unit extraction
    # -------------------------------------------------------------------------
    unit_extractor = UnitClassificator(emtp_object=self.emtp_object)
    unit_extractor.execute()

    bess_units = unit_extractor.units.bess_units

    # -------------------------------------------------------------------------
    # Replacement loop
    # -------------------------------------------------------------------------
    i = 0
    for unit in bess_units:

        if unit.object.name == "BESS_Andes_Solar_IIA":
            posX_1 = unit.object.posX
            posY_1 = unit.object.posY
            orientation = unit.object.orientation

        if unit.object.name == "BESS_Andes_IV":
            posX_2 = unit.object.posX
            posY_2 = unit.object.posY

    print(f"posX_1: {posX_1}")
    print(f"posy_1: {posY_1}")
    print(f"posX_2: {posX_2}")
    print(f"posy_2: {posY_2}")
    print(orientation)

    Design.open_design(emtp_object=self.emtp_object)
