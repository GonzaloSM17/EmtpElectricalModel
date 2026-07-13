"""
Synchronous generation replacement script.

This script replaces existing synchronous generation units in the active EMTP
design with the standard CEN SG thermal or hydro template, preserving the
original connection, position, name, load-flow data, transformer data and
selected synchronous machine parameters.

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

            # print(device_name)
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
            if not unit.loadflow_object.getAttribute("Script.DevObj"):
                unit.loadflow_object.setAttribute(
                    "Script.DevObj", "load_flow_bus_d.dwj"
                )

            attr_lf = Utils.get_params_to_dict_by_path(
                emtp_object=emtp_object, device_path=unit.loadflow_path
            )

            # ---------------------------------------------------------------------
            # Original transformer data
            # ---------------------------------------------------------------------
            if not unit.trf_object.getAttribute("Script.DevObj"):
                unit.trf_object.setAttribute("Script.DevObj", "yy_d.dwj")

            attr_trf_to_use = Utils.get_params_to_dict_by_path(
                emtp_object=emtp_object, device_path=unit.trf_path
            )

            v1 = attr_trf_to_use["V1"]
            v2 = attr_trf_to_use["V2"]

            if float(v1) > float(v2):
                pass

            elif float(v1) < float(v2):
                attr_trf_to_use["V1"] = str(v2)
                attr_trf_to_use["V2"] = str(v1)
                print(device_name)
                print(attr_trf_to_use["PreviousTransfoType"])
                print(v1)
                print(v2)
                if attr_trf_to_use["PreviousTransfoType"] == "DY_m30":
                    attr_trf_to_use["PreviousTransfoType"] == "YD_p30"

            attr_trf = {
                "S": attr_trf_to_use["S"],
                "V1": attr_trf_to_use["V1"],
                "V2": attr_trf_to_use["V2"],
                "R1": attr_trf_to_use["R1"],
                "R1units": attr_trf_to_use["R1units"],
                "X1": attr_trf_to_use["X1"],
                "X1units": attr_trf_to_use["X1units"],
                "PreviousTransfoType": attr_trf_to_use["PreviousTransfoType"],
                "tap_ratio": attr_trf_to_use["tap_ratio"],
            }
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

            # ---
            # Previus fixing
            #

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

            ##
            voltage_hv = signal.getAttribute("NominalVoltage")

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
                if unit.object.getAttribute("Exclude") == "Ex":
                    in_service = "Ex"

                elif (unit.object.getAttribute("Exclude") == "") and (
                    unit.unit_object.getAttribute("Exclude") == "Ex"
                ):
                    in_service = "Ex"

                elif (unit.object.getAttribute("Exclude") == "") and (
                    unit.unit_object.getAttribute("Exclude") == ""
                ):
                    in_service = ""

                else:
                    in_service = ""

            except:
                pass

            bus_type = attr_lf.get("Bus_Type", "")
            if bus_type == "PQ":
                bus_type = 1
            elif bus_type == "PV":
                bus_type = 2
            elif bus_type == "Slack":
                bus_type = 3
            else:
                bus_type = 1

            # Additional
            q_setpoint = q_setpoint
            q_max = float(attr_lf["Q_max"])
            q_min = float(attr_lf["Q_min"])
            s_machine = float(attr_unit["Rating_S"])

            if q_max > s_machine:
                q_max = round(1 * s_machine, 1)
                attr_lf["Q_max"] = str(q_max)
                print(f"{unit.object.name} q_max adjusted")

            if q_min < (-1) * s_machine:
                q_min = round((-1) * 1 * s_machine, 1)
                attr_lf["Q_min"] = str(q_min)
                print(f"{unit.object.name} q_min adjusted")

            if q_setpoint > q_max:
                q_setpoint = q_max

            if q_setpoint < q_min:
                q_setpoint = q_min

            attr_trf["Q_set"] = q_setpoint

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

                if "LF_" in device.name:
                    lf_name = "LF_" + attr_to_draw["name"]
                    lf = device
                    lf.setAttribute("Name", lf_name)

                if device.getAttribute("Part") == "YgD_p30":
                    trf_name = "TR_" + attr_to_draw["name"]
                    trf = device
                    trf.setAttribute("Name", trf_name)

                if device.getAttribute("Part") == "PQload":
                    load_name = "SSAA_" + attr_to_draw["name"]
                    load = device
                    load.setAttribute("Name", load_name)

                if not load:
                    load = None

            new_device = SynchronousSource(
                object=new_model_mask,
                unit_object=unit,
                loadflow_object=lf,
                trf_object=trf,
                load_object=load,
            )

            # ---------------------------------------------------------------------
            # Ensure internal device data scripts are available
            # ---------------------------------------------------------------------
            if not new_device.unit_object.getAttribute("Script.DevObj"):
                new_device.unit_object.setAttribute("Script.DevObj", "machine_sm_d.dwj")

            if not new_device.loadflow_object.getAttribute("Script.DevObj"):
                new_device.loadflow_object.setAttribute(
                    "Script.DevObj", "load_flow_bus_d.dwj"
                )

            if not new_device.trf_object.getAttribute("Script.DevObj"):
                new_device.trf_object.setAttribute("Script.DevObj", "yy_d.dwj")

            try:
                if not new_device.load_object.getAttribute("Script.DevObj"):
                    new_device.load_object.setAttribute("Script.DevObj", "pqload_d.dwj")

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
            attr_unit["Ef_c"] = "1"

            if "TER_" in new_device.object.name:
                attr_unit["npoles"] = "2"
            else:
                attr_unit["npoles"] = "4"

            # ---------------------------------------------------------------------
            # Write original parameters into the new template internals
            # ---------------------------------------------------------------------
            try:
                try:
                    Utils.set_params_from_dict_by_path(
                        emtp_object=emtp_object,
                        device_path=new_device.unit_path,
                        params=attr_unit,
                    )
                except:
                    print(f"machine setting problems")

                try:
                    Utils.set_params_from_dict_by_path(
                        emtp_object=emtp_object,
                        device_path=new_device.loadflow_path,
                        params=attr_lf,
                    )
                except:
                    print(f"lf setting problems")

                try:
                    Utils.set_params_from_dict_by_path(
                        emtp_object=emtp_object,
                        device_path=new_device.trf_path,
                        params=attr_trf,
                    )

                except:
                    print(f"trf setting problems")

                if attr_load != {}:
                    if new_device.load_object:
                        try:
                            Utils.set_params_from_dict_by_path(
                                emtp_object=emtp_object,
                                device_path=new_device.load_path,
                                params=attr_load,
                            )
                        except:
                            print(f"load setting problems")
                else:
                    new_device.load_object.remove

            except:
                print(f"problem trying to set params")

            # ---------------------------------------------------------------------
            # Apply mask values
            # ---------------------------------------------------------------------
            new_device.set_in_service(in_service)
            new_device.set_p(p_setpoint)
            new_device.set_q(q_setpoint)
            new_device.set_v(v_setpoint)

            # updating:
            new_device.set_bus_type(mode=1)
            new_device.set_bus_type(mode=bus_type)

            # ---------------------------------------------------------------------
            # Temporary execution limiter
            # ---------------------------------------------------------------------
            ## Addition
            subcct = new_device.object.subCircuit
            signals = subcct.signals

            voltage_mv = attr_unit["Rating_V"]
            for signal in signals:
                if "HV" in signal.name:
                    bus_hv = signal
                    bus_hv.setAttribute("NominalVoltage", voltage_hv)

                elif "MV" in signal.name:
                    bus_mv = signal
                    bus_mv.setAttribute("NominalVoltage", voltage_mv)

            unit = None
            print(f"unit: {device_name} complete the process")

        i += 1
        # if i >= 10:
    Design.save(emtp_object=emtp_object)
    Simulation.run_load_flow(emtp_object=emtp_object)
    # break
