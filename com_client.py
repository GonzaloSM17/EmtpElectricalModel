"""
Este archivo concentra la integración de más bajo nivel con COM. Similar a emtp_window

Responsabilidad principal:
- manejar win32com.client,
- abrir la conexión con la aplicación EMTP,
- obtener el objeto principal,      # Com Object (o emtpApp)
- obtener el global_object,         # Global Object (o emtp_api)
- cerrar aplicación,                # Esto es con la api emtp

Toda la lógica específica de COM debería quedar encapsulada aquí
para que el resto del sistema no dependa directamente de detalles de win32com.

"""

import win32com.client as win32
import psutil

from dataclasses import dataclass
from typing import Any


@dataclass
class EmtpComClient:

    program_id: str = "EMTPWorks460.Application.Single"
    # program_id: str = "EMTPWorks460.Application"
    _app_emtp: Any = None
    _emtp_object: Any = None
    _pid: int | None = None
    visible: bool = True
    attach_existing: bool = (
        False  # True → attach to a running instance; False → launch new one
    )

    def __post_init__(self):
        self.connect()

    def connect(self) -> None:

        if self.attach_existing:
            self._connect_existing()
        else:
            self._connect_new()

        # Getting global object
        self._emtp_object = self._app_emtp.getGlobalObject
        if self._emtp_object is None:
            raise RuntimeError("Failed to obtain globalObject.")

        return self._emtp_object

    def _connect_existing(self) -> None:
        """Attach to an already-running EMTP instance using Dispatch (no .Single suffix)."""
        existing_program_id = "EMTPWorks460.Application"
        try:
            self._app_emtp = win32.Dispatch(existing_program_id)
        except Exception as exc:
            raise RuntimeError(
                f"Could not attach to a running EMTP instance ('{existing_program_id}'). "
                "Make sure EMTPWorks is open before connecting."
            ) from exc

        # Resolve the PID of the existing process
        emtp_procs = [
            p.pid
            for p in psutil.process_iter(["pid", "name"])
            if "emtpworks" in (p.info["name"] or "").lower()
        ]
        self._pid = emtp_procs[0] if emtp_procs else None

        # Make visible (no-op if already visible)
        self._app_emtp.ShowHide(self.visible)

    def _connect_new(self) -> None:
        """Launch a fresh EMTP instance."""
        before_pids = {p.pid for p in psutil.process_iter(["pid"])}
        self._app_emtp = win32.DispatchEx(self.program_id)
        # self._app_emtp = win32.Dispatch(self.program_id)
        after_pids = {
            p.pid
            for p in psutil.process_iter(["pid", "name"])
            if p.pid not in before_pids
            and "emtpworks" in (p.info["name"] or "").lower()
        }

        # PID detection is best-effort: the COM object is already valid even if
        # the process name doesn't match the filter (e.g. different exe name).
        if after_pids:
            self._pid = max(
                after_pids, key=lambda pid: psutil.Process(pid).create_time()
            )
        else:
            print(
                "⚠️  EMTPWorks launched via COM but its PID was not detected. "
                "disconnect() will fall back to the COM API."
            )
            self._pid = None

        # Make visible
        self._app_emtp.ShowHide(self.visible)

    def disconnect(self) -> None:
        if self._pid is not None:
            # Terminate by PID when we tracked the process
            try:
                proc = psutil.Process(self._pid)
                proc.terminate()
                proc.wait(timeout=3)
            except psutil.NoSuchProcess:
                pass
            except psutil.TimeoutExpired:
                proc.kill()
        elif self._app_emtp is not None:
            # Fallback: ask EMTP to quit via its own COM API
            try:
                self._app_emtp.quit()
            except Exception:
                pass
        else:
            raise RuntimeError("No active connection to disconnect.")
        self._app_emtp = self._emtp_object = self._pid = None

    @property
    def emtp_object(self):
        """GlobalObject — top-level COM context for this EMTP instance."""
        if self._emtp_object is None:
            raise RuntimeError("Not connected.")
        return self._emtp_object


if __name__ == "__main__":

    # Launch a new instance (default behaviour)
    # emtp_client = EmtpComClient()

    # Attach to an already-running instance
    emtp_client = EmtpComClient(attach_existing=True)

    emtp_object = emtp_client.emtp_object
    print(emtp_object)  # Just to verify we got the global object
