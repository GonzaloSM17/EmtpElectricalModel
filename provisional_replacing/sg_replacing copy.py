from unit_extractor_v1 import *

library_path = "C:\\Users\\gonzalo.sanchez\\OneDrive - Coordinador Eléctrico Nacional\\C01. Simulación y Laboratorio en Tiempo Real\\04. EMTP Modelo Eléctrico\\09. Templates Reemplazo\\CEN Devices.clf"

if __name__ == "__main__":

    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    if not emtp_object.currentDesign:
        Design.open_design(emtp_object=emtp_object)

    ## Loading Library
    Library.open_library(emtp_object=emtp_object, library_path=library_path)

    unit_extractor = UnitExtractor(emtp_object=emtp_object)
    unit_extractor.execute()

    units = unit_extractor.units.synchronous_units

    i = 0
    unit = None
    for unit in units:

        # print(
        #     f"{unit.object.name}/{unit.unit_object.name}/{.lf_object.name}/{unit.tf_object.name}"
        # )

        ## unit
        if not unit.unit_object.getAttribute("Script.DevObj"):
            unit.unit_object.setAttribute("Script.DevObj", "machine_sm_d.dwj")

        attr_unit = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.unit_path
        )

        ## lf
        if not unit.lf_object.getAttribute("Script.DevObj"):
            unit.lf_object.setAttribute("Script.DevObj", "load_flow_bus_d.dwj")

        attr_lf = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.lf_path
        )

        # tf
        if not unit.tf_object.getAttribute("Script.DevObj"):
            unit.tf_object.setAttribute("Script.DevObj", "yy_d.dwj")

        attr_tf = Utils.get_params_to_dict_by_path(
            emtp_object=emtp_object, device_path=unit.tf_path
        )

        ## load
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

        attr_to_draw = {
            "name": unit.object.name,
            "posX": unit.object.posX,
            "posY": unit.object.posY,
            "orientation": unit.object.orientation,
        }

        if attr_to_draw["orientation"] == "E":
            attr_to_draw["posX"] = attr_to_draw["posX"] - 2000
        if attr_to_draw["orientation"] == "w":
            attr_to_draw["posX"] = attr_to_draw["posX"] + 300

        pin = unit.object.pins[0]
        signal = pin.signal

        ## Calculate some attr
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

        ## attribute_to_mask
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

        ## AddObject
        if "TER_" in unit.object.name:
            library_template_name = "SG_THERMAL_TEMPLATE"
        else:
            library_template_name = "SG_HYDRO_TEMPLATE"
        ## Delete old object
        unit.object.remove

        library_object = Library.find_type(
            emtp_object=emtp_object,
            library_name="CEN Devices",
            type_name=library_template_name,
        )

        new_model_mask = Design.design(emtp_object).addDevice(
            library_object,
            attr_to_draw["posX"],
            attr_to_draw["posY"] - 300,
            attr_to_draw["orientation"],
        )

        try:
            new_model_mask.makeUnique()
        except Exception as e:
            new_model_mask.makeUnique

        # Connection
        new_pin = new_model_mask.pins[0]
        new_pin.connectTo(signal, True)

        new_model_mask.setAttribute("Name", attr_to_draw["name"])
        new_model_subcc = new_model_mask.subCircuit
        devices = new_model_subcc.devices

        load = None

        for device in devices:
            if device.name == "SG":
                unit = device
            if device.name == "LF_SG":
                lf = device
            if device.name == "TR_SG":
                tf = device
            if device.name == "SSAA":
                load = device

            if not load:
                load = None

        new_device = SynchronousSource(
            object=new_model_mask,
            unit_object=unit,
            lf_object=lf,
            tf_object=tf,
            load_object=load,
        )

        # SetAttribute
        if not new_device.unit_object.getAttribute("Script.DevObj"):
            unit.unit_object.setAttribute("Script.DevObj", "machine_sm_d.dwj")

        ## lf
        if not new_device.lf_object.getAttribute("Script.DevObj"):
            unit.lf_object.setAttribute("Script.DevObj", "load_flow_bus_d.dwj")

        # tf
        if not new_device.tf_object.getAttribute("Script.DevObj"):
            unit.tf_object.setAttribute("Script.DevObj", "yy_d.dwj")

        ## load
        try:
            if not new_device.load_object.getAttribute("Script.DevObj"):
                unit.load_object.setAttribute("Script.DevObj", "pqload_d.dwj")

        except Exception as e:
            print(
                f"Error setting Script.DevObj for load_object: {e} to {new_device.object.name}"
            )

        ## Preview treatment for SM
        attr_unit["i_agline_o"] = 2
        attr_unit["Efss_o"] = 2
        attr_unit["vd_o"] = 2
        attr_unit["id_o"] = 2
        attr_unit["vq_o"] = 2
        attr_unit["iq_o"] = 2
        attr_unit["if_o"] = 2
        attr_unit["Pe_o"] = 2
        attr_unit["Pmss_o"] = 2
        attr_unit["Mass_OSC_data"] = "2 3 0 0 0"

        if "TER_" in unit.object.name:
            attr_unit["npoles"] = 2
        else:
            attr_unit["npoles"] = 4

        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object,
            device_path=new_device.unit_path,
            params=attr_unit,
        )
        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object, device_path=new_device.lf_path, params=attr_lf
        )
        Utils.set_params_from_dict_by_path(
            emtp_object=emtp_object, device_path=new_device.tf_path, params=attr_tf
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

        new_device.set_in_service(in_service)
        new_device.set_p(p_setpoint)
        new_device.set_q(q_setpoint)
        new_device.set_bus_type(bus_type)
        new_device.set_v(v_setpoint)

        unit = None
        i += 1
        if i >= 1:
            for key, attr in attr_unit.items():
                print(f"{key}: {attr}")
            Design.save(emtp_object=emtp_object)
            # Simulation.run_load_flow(emtp_object=emtp_object)
            break
