# OS version 10.2

class Api:
    """

    endpoint: https://firewall/api
    """

    base: str = 'api/'

    def __init__(self):
        self.uri = f'{self.base}'

    def __str__(self):
        return f'{self.uri}'

    @property
    def keygen(self):
        """Generate API keys for authentication."""
        self.uri += f'?type=keygen'
        return self

    @property
    def config(self):
        """Modify the configuration."""
        self.uri += f'?type=config'
        return self

    @property
    def commit(self):
        """Commit firewall configuration, including partial commits."""
        self.uri += f'?type=commit'
        return self

    @property
    def op(self):
        """Perform operational mode commands, including checking system status and validating configurations."""
        self.uri += f'?type=op'
        return self

    @property
    def report(self):
        """Get reports, including predefined, dynamic, and custom reports."""
        self.uri += f'?type=report'
        return self

    @property
    def log(self):
        """Get logs, including traffic, threat, and event logs."""
        self.uri += f'?type=log'
        return self

    @property
    def import_(self):
        """Import files including configurations and certificates."""
        self.uri += f'?type=import'
        return self

    @property
    def export(self):
        """Export files including packet captures, certificates, and keys."""
        self.uri += f'?type=export'
        return self

    @property
    def user_id(self):
        """Update User-ID mappings."""
        self.uri += f'?type=user-id'
        return self

    @property
    def version(self):
        """Show the PAN-OS version, serial number, and model number."""
        self.uri += f'?type=version'
        return self
