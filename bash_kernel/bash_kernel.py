from __future__ import print_function

from jupyter_kernel import MagicKernel
import os
import subprocess


class BashKernel(MagicKernel):
    implementation = 'Bash'
    implementation_version = '1.0'
    language = 'bash'
    language_version = '0.1'
    banner = "Bash kernel - interact with a bash prompt"

    def __init__(self, *args, **kwargs):
        super(BashKernel, self).__init__(*args, **kwargs)
        self.rfid, wpipe = os.pipe()
        rpipe, self.wfid = os.pipe()

        kwargs = dict(bufsize=0, stdin=rpipe,
                      stderr=wpipe, stdout=wpipe)

        self.proc = subprocess.Popen(['bash'], **kwargs)

    def get_usage(self):
        return "This is the bash kernel."

    def do_execute_direct(self, code):
        cmd = code.strip()
        os.write(self.wfid, cmd + '; echo "__done__"\n')

        buf = ''
        while not buf.rstrip().endswith('__done__'):
            buf += os.read(self.rfid, 1024)
        return buf[:buf.index('__done__')].rstrip()


if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=BashKernel)
