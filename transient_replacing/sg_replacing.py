"""
Synchronous generation replacement script.

This script replaces existing synchronous generation units in the active EMTP
design with the standard CEN SG thermal or hydro template, preserving the
original connection, position, name, load-flow data, transformer data and
selected synchronous machine parameters.

Only ordering and comments were added. The original execution logic is kept.
"""

from unit_extractor_v1 import *

library_path = "C:\\Users\\gonzalo.sanchez\\OneDrive - Coordinador Eléctrico Nacional\\C01. Simulación y Laboratorio en Tiempo Real\\04. EMTP Modelo Eléctrico\\09. Templates Reemplazo\\CEN Devices.clf"


if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # EMTP session and library initialization
    # -------------------------------------------------------------------------
    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    # if not emtp_object.currentDesign:
    #     Design.open_design(emtp_object=emtp_object)

    Library.open_library(emtp_object=emtp_object, library_path=library_path)

    # -------------------------------------------------------------------------
    # Unit extraction
    # -------------------------------------------------------------------------
    unit_extractor = UnitExtractor(emtp_object=emtp_object)
    unit_extractor.execute()

    units = unit_extractor.units.synchronous_units

    # -------------------------------------------------------------------------
    # Replacement loop
    # -------------------------------------------------------------------------
    i = 0
    unit = None
    for unit in units:

        device_name = unit.object.name

        if "TEMPLATE" in unit.object.getAttribute("LibType"):
            continue

        else:

            try:
                # ---------------------------------------------------------------------
                # Original synchronous machine data
                # ---------------------------------------------------------------------
                if not unit.unit_object.getAttribute("Script.DevObj"):
                    unit.unit_object.setAttribute("Script.DevObj", "machine_sm_d.dwj")

                attr_unit = Utils.get_params_to_dict_by_path(
                    emtp_object=emtp_object, device_path=unit.unit_path
                )

                # ---------------------------------------------------------------------
                # Original load-flow bus data
                # ---------------------------------------------------------------------
                if not unit.lf_object.getAttribute("Script.DevObj"):
                    unit.lf_object.setAttribute("Script.DevObj", "load_flow_bus_d.dwj")

                attr_lf = Utils.get_params_to_dict_by_path(
                    emtp_object=emtp_object, device_path=unit.lf_path
                )

                # ---------------------------------------------------------------------
                # Original transformer data
                # ---------------------------------------------------------------------
                if not unit.tf_object.getAttribute("Script.DevObj"):
                    unit.tf_object.setAttribute("Script.DevObj", "yy_d.dwj")

                attr_tf = Utils.get_params_to_dict_by_path(
                    emtp_object=emtp_object, device_path=unit.tf_path
                )

                # ---------------------------------------------------------------------
                # Original auxiliary load data, if available
                # ---------------------------------------------------------------------
                try:
                    if not unit.load_object.getAttribute("Script.DevObj"):
                        unit.load_object.setAttribute("Script.DevObj", "pqload_d.dwj")

                    attr_load = Utils.get_params_to_dict_by_path(
                        emtp_object=emtp_object, device_path=unit.load_path
                    )

                except Exception as e:
                    attr_load = {}
                    print(
                        f"Error setting Script.DevObj for load_object: {e} to {unit.object.name}"
                    )

                # ---------------------------------------------------------------------
                # Drawing data and connection reference
                # ---------------------------------------------------------------------
                attr_to_draw = {
                    "name": unit.object.name,
                    "posX": unit.object.posX,
                    "posY": unit.object.posY,
                    "orientation": unit.object.orientation,
                }

                # print(attr_to_draw["orientation"])
                if "TER_" in device_name:
                    if attr_to_draw["orientation"] == "E":
                        attr_to_draw["posX"] = attr_to_draw["posX"] - 2500

                    if attr_to_draw["orientation"] == "w":
                        attr_to_draw["posX"] = attr_to_draw["posX"] + 800

                else:
                    if attr_to_draw["orientation"] == "E":
                        attr_to_draw["posX"] = attr_to_draw["posX"] + 500

                    if attr_to_draw["orientation"] == "w":
                        attr_to_draw["posX"] = attr_to_draw["posX"] - 800

                pin = unit.object.pins[0]
                signal = pin.signal

                # ---------------------------------------------------------------------
                # Operating point and load-flow controls
                # ---------------------------------------------------------------------
                p_setpoint = float(attr_lf.get("P_set", ""))
                q_setpoint = float(attr_lf.get("Q_set", ""))
                v_setpoint = round(
                    float(attr_lf.get("Voltage_Slack", ""))
                    / float(attr_unit.get("Rating_V", "")),
                    2,
                )

                try:
                    if (
                        unit.object.getAttribute("Exclude") == ""
                        and unit.unit_object.getAttribute("Exclude") == ""
                    ):
                        in_service = ""
                    else:
                        in_service = "Ex"
                except:
                    pass

                bus_type = attr_lf.get("Voltage_Slack", "")
                if bus_type == "PQ":
                    bus_type = 1
                elif bus_type == "PV":
                    bus_type = 2
                elif bus_type == "Slack":
                    bus_type = 3
                else:
                    bus_type = 1

                # ---------------------------------------------------------------------
                # Mask setpoints
                # ---------------------------------------------------------------------
                if in_service == "Ex":
                    in_service = 0
                    p_setpoint = 0
                    q_setpoint = 0
                    v_setpoint = 1
                    bus_type = 1
                else:
                    in_service = 1
                    p_setpoint = float(p_setpoint)
                    q_setpoint = float(q_setpoint)
                    v_setpoint = v_setpoint
                    bus_type = int(bus_type)

                # ---------------------------------------------------------------------
                # Template selection and old object deletion
                # ---------------------------------------------------------------------
                if "TER_" in unit.object.name:
                    library_template_name = "SG_THERMAL_TEMPLATE"
                else:
                    library_template_name = "SG_HYDRO_TEMPLATE"
                    if attr_to_draw["orientation"] == "w":
                        attr_to_draw["orientation"] == "E"
                    else:
                        attr_to_draw["orientation"] = "w"

                unit.object.remove

                library_object = Library.find_type(
                    emtp_object=emtp_object,
                    library_name="CEN Devices",
                    type_name=library_template_name,
                )

                # ---------------------------------------------------------------------
                # Insert new synchronous generation template
                # ---------------------------------------------------------------------
                new_model_mask = Design.design(emtp_object).addDevice(
                    library_object,
                    attr_to_draw["posX"],
                    attr_to_draw["posY"] - 300,
                    attr_to_draw["orientation"],
                )

                try:
                    new_model_mask.makeUnique
                except Exception as e:
                    f"make unique doesn't work"

                # Reconnect the new model to the original signal.
                new_pin = new_model_mask.pins[0]
                new_pin.connectTo(signal, True)

                new_model_mask.setAttribute("Name", attr_to_draw["name"])
                new_model_subcc = new_model_mask.subCircuit
                devices = new_model_subcc.devices

                # ---------------------------------------------------------------------
                # Locate internal devices in the new template
                # ---------------------------------------------------------------------
                load = None

                for device in devices:
                    if device.getAttribute("Part") == "SM":
                        unit = device
                        unit.setAttribute("Name", attr_to_draw["name"])

                    if device.name == "LF_SG":
                        lf_name = "LF_" + attr_to_draw["name"]
                        lf = device
                        lf.setAttribute("Name", lf_name)

                    if device.getAttribute("Part") == "YgD_p30":
                        tf_name = "TR_" + attr_to_draw["name"]
                        tf = device
                        tf.setAttribute("Name", tf_name)

                    if device.getAttribute("Part") == "PQload":
                        load_name = "SSAA_" + attr_to_draw["name"]
                        load = device
                        load.setAttribute("Name", load_name)

                    if not load:
                        load = None

                new_device = SynchronousSource(
                    object=new_model_mask,
                    unit_object=unit,
                    lf_object=lf,
                    tf_object=tf,
                    load_object=load,
                )

                # ---------------------------------------------------------------------
                # Ensure internal device data scripts are available
                # ---------------------------------------------------------------------
                if not new_device.unit_object.getAttribute("Script.DevObj"):
                    new_device.unit_object.setAttribute(
                        "Script.DevObj", "machine_sm_d.dwj"
                    )

                if not new_device.lf_object.getAttribute("Script.DevObj"):
                    new_device.lf_object.setAttribute(
                        "Script.DevObj", "load_flow_bus_d.dwj"
                    )

                if not new_device.tf_object.getAttribute("Script.DevObj"):
                    new_device.tf_object.setAttribute("Script.DevObj", "yy_d.dwj")

                try:
                    if not new_device.load_object.getAttribute("Script.DevObj"):
                        new_device.load_object.setAttribute(
                            "Script.DevObj", "pqload_d.dwj"
                        )

                except Exception as e:
                    print(
                        f"Error setting Script.DevObj for load_object: {e} to {new_device.object.name}"
                    )

                # ---------------------------------------------------------------------
                # Preview treatment for synchronous machine outputs
                # ---------------------------------------------------------------------
                attr_unit["i_agline_o"] = "2"
                attr_unit["Efss_o"] = "2"
                attr_unit["vd_o"] = "2"
                attr_unit["id_o"] = "2"
                attr_unit["vq_o"] = "2"
                attr_unit["iq_o"] = "2"
                attr_unit["if_o"] = "2"
                attr_unit["Pe_o"] = "2"
                attr_unit["Pmss_o"] = "2"
                attr_unit["Mass_OSC_data"] = "2 3 0 0 0"

                if "TER_" in new_device.object.name:
                    attr_unit["npoles"] = "2"
                else:
                    attr_unit["npoles"] = "4"

                # ---------------------------------------------------------------------
                # Write original parameters into the new template internals
                # ---------------------------------------------------------------------
                Utils.set_params_from_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=new_device.unit_path,
                    params=attr_unit,
                )

                Utils.set_params_from_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=new_device.lf_path,
                    params=attr_lf,
                )

                Utils.set_params_from_dict_by_path(
                    emtp_object=emtp_object,
                    device_path=new_device.tf_path,
                    params=attr_tf,
                )

                if attr_load != {}:
                    if new_device.load_object:
                        Utils.set_params_from_dict_by_path(
                            emtp_object=emtp_object,
                            device_path=new_device.load_path,
                            params=attr_load,
                        )
                else:
                    new_device.load_object.remove

                # ---------------------------------------------------------------------
                # Apply mask values
                # ---------------------------------------------------------------------
                new_device.set_in_service(in_service)
                new_device.set_p(p_setpoint)
                new_device.set_q(q_setpoint)
                new_device.set_bus_type(bus_type)
                new_device.set_v(v_setpoint)

                # ---------------------------------------------------------------------
                # Temporary execution limiter
                # ---------------------------------------------------------------------
                unit = None
                print(f"unit: {device_name} complete the process")

            except:
                print(
                    f"unit: {device_name} couldn't be replacing completely. See the new device to ensure"
                )

        i += 1
        if i >= 10:
            # Design.save(emtp_object=emtp_object)
            # Design.open_design(emtp_object=emtp_object)
            break
