from xonsh.main import main_context
try:
    from ipykernel.kernelapp import IPKernelApp
except ImportError:
    from IPython.kernel.zmq.kernelapp import IPKernelApp
from .kernel import XonshKernel

# must manually pass in args to avoid interfering w/ Jupyter arg parsing
with main_context(argv=['--shell-type=readline']):
    IPKernelApp.launch_instance(kernel_class=XonshKernel)
