from pydantic import BaseModel


class SshCommand(BaseModel):
    """
    f"ssh -p {component_info['ssh_port']} {component_info['ssh_user']}@{self._get_endpoint_host(component_info)} {ssh_event.command}"
    """
    ssh_host: str
    ssh_port: int
    ssh_user: str
    command: str
