class CoreException(Exception):
    """Base exception for core module"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class SecurityException(CoreException):
    """Exception for security issues"""
    pass

class ConfigurationException(CoreException):
    """Exception for configuration issues"""
    pass

class SessionException(CoreException):
    """Exception for session issues"""
    pass