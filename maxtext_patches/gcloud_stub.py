import logging
_TENSORBOARDX_AVAILABLE = False
_ML_DIAGNOSTICS_AVAILABLE = False
def is_decoupled(): return True
def gcs_storage(): return None

class StackTraceConfig:
    def __init__(self, *args, **kwargs): pass

class DebugConfig:
    def __init__(self, *args, **kwargs): pass
    @staticmethod
    def from_dict(*args, **kwargs): return DebugConfig()

class DiagnosticConfig:
    def __init__(self, *args, **kwargs): pass

class StackTraceContainer:
    StackTraceConfig = StackTraceConfig

class DebugContainer:
    DebugConfig = DebugConfig
    def __init__(self, *args, **kwargs): pass

class DiagnosticContainer:
    DiagnosticConfig = DiagnosticConfig
    def __init__(self, *args, **kwargs): pass

debug_configuration = DebugContainer
stack_trace_configuration = StackTraceContainer
diagnostic_configuration = DiagnosticContainer

class DummyWriter:
    def __init__(self, *args, **kwargs): pass
    def __call__(self, *args, **kwargs): return self
    def __getattr__(self, name): return lambda *a, **k: self

writer = DummyWriter()
diagnostic = None
monitoring = None
goodput = None

def vertex_tensorboard_modules(): return (DummyWriter, DummyWriter)
def mldiagnostics_modules(): return (DummyWriter, DummyWriter)
def workload_monitor(): return (DummyWriter, True)
def cloud_diagnostics(*args, **kwargs): return (None, DebugContainer, DiagnosticContainer, StackTraceContainer)
def goodput_modules(*args, **kwargs): return (None, None, None)
