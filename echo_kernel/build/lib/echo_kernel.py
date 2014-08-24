from __future__ import print_function

from calico import MagicKernel

class EchoKernel(MagicKernel):
    implementation = 'Echo'
    implementation_version = '1.0'
    language = 'no-op'
    language_version = '0.1'
    banner = "Echo kernel - as useful as a parrot"

    def get_usage(self):
        return "This is the echo kernel."

    def do_execute_direct(self, code):
        return code

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=EchoKernel)
