from unit_extractor import *
import time

library_path_GS = "C:\\Users\\gonzalo.sanchez\\OneDrive - Coordinador Eléctrico Nacional\\C01. Simulación y Laboratorio en Tiempo Real\\04. EMTP Modelo Eléctrico\\09. Templates Reemplazo\\CEN Devices_v1.1.clf"
library_path_KA = "C:\\Users\\kelly.allendes\\Downloads\\CEN Devices.clf"


class ReplacingIBR:

    def __init__(self, emtp_object=Any, device: Any = None):

        self.device = device
        self.emtp_object = emtp_object

        try:
            if self.device:
                self.device_name = device.object.name
                if "PFV_" in device.object.name:
                    if "PMGD" in device.object.name:
                        self.type = "DER"

                    else:
                        self.type = "PV"

                elif "PE_" in device.object.name:
                    self.type = "WF"

                elif "BESS_" in device.object.name:
                    self.type = "BESS"

                elif "Solar" in device.object.name:
                    self.type = "PV"

                else:
                    self.type = None
                    print(
                        f"{self.device_name} couldn't be replace. The name doesn't containt any key to recongnize the type"
                    )
                    return

        except:
            print(f"The device is not and useful object")
            return

    def _saving_attr_object(self):

        if self.device:
            if self.device.object:
                self.attr_object = Utils.get_params_to_dict_by_path(
                    emtp_object=self.emtp_object, device_path=self.device.object
                )
            else:
                self.attr_object = None
        else:
            self.attr_to_draw = None

    def _saving_attr_unit(self):

        if self.device.unit_object:
            self.attr_unit = Utils.get_params_to_dict_by_path(
                emtp_object=self.emtp_object, device_path=self.device.unit_path
            )
        else:
            self.attr_unit = None

    def _get_setpoint(self):

        self.in_service = self.device.get_in_service()
        self.p_setpoint = self.device.get_p()
        self.q_setpoint = self.device.get_q()

    def _get_to_draw(self):

        if self.device:

            if self.device.object.orientation == "w":
                self.attr_to_draw = {
                    "name": self.device.object.name,
                    "posX": self.device.object.posX + 100,
                    "posY": self.device.object.posY,
                    "orientation": self.device.object.orientation,
                }

            else:
                self.attr_to_draw = {
                    "name": self.device.object.name,
                    "posX": self.device.object.posX - 100,
                    "posY": self.device.object.posY,
                    "orientation": self.device.object.orientation,
                }
        else:
            self.attr_to_draw = None

    def _get_signal(self):

        pin = self.device.object.pins[0]
        self.signal_to_connect = pin.signal

        try:
            self.signal_voltage = self.signal_to_connect.getAttribute("NominalVoltage")
            if self.signal_voltage != "":
                return
            else:
                self.signal_voltage = self.attr_unit.get("Vpoi_kVRMSLL", "220")
        except:
            print(f"For {self.device_name} there is not voltage for signal")
            self.signal_voltage = None

    def _open_lib(self):
        Library.open_library(emtp_object=self.emtp_object, library_path=library_path_GS)

    def _get_lib_type(self):

        if self.type == "PV":
            library_template = "PV_TEMPLATE"

        elif self.type == "WF":
            library_template = "WF_TEMPLATE"

        elif self.type == "BESS":
            library_template = "BESS_TEMPLATE"

        elif self.type == "DER":
            library_template = "DER_TEMPLATE"

        else:
            library_template = "PV"

        if library_template:
            self.library_object = Library.find_type(
                emtp_object=self.emtp_object,
                library_name="CEN Devices",
                type_name=library_template,
            )

    def _remove(self):

        self.device.object.remove
        # time.sleep(1)

    def _draw_new_device(self):

        try:
            self.new_device = Design.design(self.emtp_object).addDevice(
                self.library_object,
                self.attr_to_draw["posX"],
                self.attr_to_draw["posY"],
                self.attr_to_draw["orientation"],
            )

            # time.sleep(1)

            # self.new_device.makeUnique
            try:
                self.new_device.makeUnique()
            except Exception as e:
                self.new_device.makeUnique
            self.new_device.setAttribute("Name", self.device_name)

            # No read only
            subcct = self.new_device.subCircuit
            subcct.isReadOnly = "False"

            # Connect to grid
            new_pin = self.new_device.pins[0]
            new_pin.connectTo(self.signal_to_connect, True)

        except:
            print(f"model: {self.device_name} not posible to redraw")

        try:
            subcct = self.new_device.subCircuit
            unit_new_device = subcct.devices[0]

            # Naming new device
            unit_new_device.setAttribute("Name", self.new_device.name)

            # New Dataclass
            _new_device = RenewableEnergySource(
                object=self.new_device, unit_object=unit_new_device
            )
            self.new_device_object = _new_device

        except:
            print(
                f"new device from model: {self.device.object.name} not posible to redraw"
            )

    def _resetting_attribute(self):

        # for unit
        Utils.set_params_from_dict_by_path(
            emtp_object=self.emtp_object,
            device_path=self.new_device_object.unit_path,
            params=self.attr_unit,
        )

        # for mask
        self.new_device_object.set_in_service(int(self.in_service))
        self.new_device_object.set_p(float(self.p_setpoint))
        self.new_device_object.set_q(float(self.q_setpoint))

    def _signal_voltage(self):

        # try:
        subcct = self.new_device.subCircuit
        signals = subcct.signals

        if self.signal_to_connect:
            try:
                for signal in signals:
                    if "POI" in signal.name:
                        signal.setAttribute(
                            "NominalVoltage",
                            self.signal_voltage,
                        )
            except:
                print(f"Not possible to set voltage on signal")
                return

    def execute(self):

        self._saving_attr_object()
        self._saving_attr_unit()
        self._get_setpoint()
        self._get_signal()
        self._get_to_draw()

        self._open_lib()
        self._get_lib_type()

        self._remove()
        self._draw_new_device()

        self._resetting_attribute()
        self._signal_voltage()


if __name__ == "__main__":

    # -------------------------------------------------------------------------
    # EMTP session and library initialization
    # -------------------------------------------------------------------------
    emtp_client = EmtpComClient(attach_existing=True)
    emtp_object = emtp_client.emtp_object

    extractor = UnitExtractor(emtp_object=emtp_object)
    extractor.execute()

    i = 0

    for unit in (
        # extractor.units.pv_units +
        # extractor.units.wf_units +
        extractor.units.der_units
    ):

        # print(unit.object.name)
        print(unit.unit_object.name)

        # break

        replacing_operator = ReplacingIBR(emtp_object=emtp_object, device=unit)
        replacing_operator.execute()

        # i += 3
        # if i >= 10:
        #     break

    Design.save(emtp_object=emtp_object)
    # Design.open_design(emtp_object=emtp_object)
    # Simulation.run_load_flow(emtp_object=emtp_object)
