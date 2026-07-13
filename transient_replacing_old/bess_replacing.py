"""
BESS replacement script.

This script replaces existing BESS units in the active EMTP design with the
standard CEN BESS template, preserving the original electrical connection,
positioning, name, operating point and selected sizing parameters.

Only ordering and comments were added. The original execution logic is kept.
"""

from transient_replacing_old.unit_extractor_old import *

library_path = "C:\\Users\\gonzalo.sanchez\\OneDrive - Coordinador Eléctrico Nacional\\C01. Simulación y Laboratorio en Tiempo Real\\04. EMTP Modelo Eléctrico\\09. Templates Reemplazo\\CEN Devices.clf"


if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # EMTP session and library initialization
    # -------------------------------------------------------------------------
    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    if not emtp_object.currentDesign:
        Design.open_design(emtp_object=emtp_object)

    Library.open_library(emtp_object=emtp_object, library_path=library_path)

    # -------------------------------------------------------------------------
    # Unit extraction
    # -------------------------------------------------------------------------
    unit_extractor = UnitExtractor(emtp_object=emtp_object)
    unit_extractor.execute()

    bess_units = unit_extractor.units.bess_units

    # -------------------------------------------------------------------------
    # Replacement loop
    # -------------------------------------------------------------------------
    i = 0
    for unit in bess_units:

        # ---------------------------------------------------------------------
        # Original unit data extraction
        # ---------------------------------------------------------------------
        attr_unit = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_object.name
        )

        attr_to_draw = {
            "name": unit.unit_object.name,
            "posX": unit.unit_object.posX,
            "posY": unit.unit_object.posY,
            "orientation": unit.unit_object.orientation,
        }

        # Adjust insertion position according to original orientation.
        if attr_to_draw["orientation"] == "w":
            attr_to_draw["posX"] = attr_to_draw["posX"] + 1300

        if attr_to_draw["orientation"] == "E":
            attr_to_draw["posX"] = attr_to_draw["posX"] - 1300

        # ---------------------------------------------------------------------
        # Preserve AC and DC connection references before deleting old objects
        # ---------------------------------------------------------------------
        pin = unit.unit_object.pins[0]
        signal = pin.signal

        pin_dc_signal_1 = unit.unit_object.pins[1]
        pin_dc_signal_2 = unit.unit_object.pins[2]

        signal_dc_pin_1 = pin_dc_signal_1.signal
        signal_dc_pin_2 = pin_dc_signal_2.signal

        pin_dc = signal_dc_pin_1.pins[0]
        device_dc = pin_dc.device

        # ---------------------------------------------------------------------
        # Operating point and sizing values from original unit
        # ---------------------------------------------------------------------
        ngen = float(attr_unit.get("Ngen", 0))
        sgen = float(attr_unit.get("Sgen", 0))
        ngen_in_service = float(attr_unit.get("Ngen_in_service", ngen))
        pref_poi = float(attr_unit.get("Pref_poi", 0))
        qpoi_pu = float(attr_unit.get("Qref_pu", 0))
        in_service = unit.unit_object.getAttribute("Exclude")
        voltage_level = attr_unit.get("V1_WP", "220")

        attr_to_set = {"sgn": round(ngen * sgen, 2)}

        # ---------------------------------------------------------------------
        # Mask setpoints
        # ---------------------------------------------------------------------
        if in_service == "Ex":
            in_service = 0
            p_setpoint = 0
            q_setpoint = 0
        else:
            in_service = 1
            p_setpoint = round(pref_poi * sgen * ngen_in_service, 2)
            q_setpoint = round(qpoi_pu * sgen * ngen_in_service, 2)

        attr_to_mask = {
            "in_service": in_service,
            "p_setpoint": p_setpoint,
            "q_setpoint": q_setpoint,
        }

        # ---------------------------------------------------------------------
        # Template selection and old object deletion
        # ---------------------------------------------------------------------
        library_template_name = "BESS_TEMPLATE"

        unit.unit_object.remove
        time.sleep(1)
        device_dc.remove
        signal_dc_pin_1.remove
        signal_dc_pin_2.remove

        library_object = Library.find_type(
            emtp_object=emtp_object,
            library_name="CEN Devices",
            type_name=library_template_name,
        )

        # ---------------------------------------------------------------------
        # Insert new BESS template
        # ---------------------------------------------------------------------
        new_model_mask = Design.design(emtp_object).addDevice(
            library_object,
            attr_to_draw["posX"],
            attr_to_draw["posY"] - 100,
            attr_to_draw["orientation"],
        )

        try:
            new_model_mask.makeUnique
        except Exception as e:
            print(f"make unique not working")

        # Reconnect the new model to the original AC signal.
        new_pin = new_model_mask.pins[0]
        new_pin.connectTo(signal, True)

        # Preserve the original name at mask and internal model levels.
        new_model_mask.setAttribute("Name", attr_to_draw["name"])

        new_model_subcc = new_model_mask.subCircuit
        new_model = new_model_subcc.devices[0]
        new_model.setAttribute("Name", attr_to_draw["name"])

        new_model_path = new_model_mask.name + "/" + new_model.name

        # ---------------------------------------------------------------------
        # Apply initial mask values
        # ---------------------------------------------------------------------
        device = Bess(object=new_model_mask, unit_object=new_model)

        device.set_in_service(attr_to_mask["in_service"])
        device.set_p(attr_to_mask["p_setpoint"])
        device.set_q(attr_to_mask["q_setpoint"])

        # ---------------------------------------------------------------------
        # Recalculate and write internal template parameters
        # ---------------------------------------------------------------------
        new_attr = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object,
            device_path=new_model_path,
        )

        sgn = float(attr_to_set["sgn"])
        new_sgen = new_attr.get("Sgen", 0)

        new_ngen = str(int(round((sgn / float(new_sgen)), 0)))
        new_ngen_in_service = new_ngen

        new_params = {
            "Ngen": new_ngen,
            "Ngen_in_service": new_ngen_in_service,
            "S1_WP": str(float(sgn) * 1.1),
            "V1_WP": voltage_level,
        }

        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object,
            device_path=new_model_path,
            params=new_params,
        )

        # Re-apply mask values after parameter update.
        device.set_in_service(attr_to_mask["in_service"])
        device.set_p(attr_to_mask["p_setpoint"])
        device.set_q(attr_to_mask["q_setpoint"])

        # ---------------------------------------------------------------------
        # Temporary execution limiter
        # ---------------------------------------------------------------------
        i += 1
        if i >= 1:
            print(device.unit_object.name)
            Design.save(emtp_object=emtp_object)
            Design.open_design(emtp_object=emtp_object)
            # Simulation.run_load_flow(emtp_object=emtp_object)
            break
