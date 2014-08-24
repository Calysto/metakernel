from __future__ import print_function

from jupyter_kernel import MagicKernel
import aiml
import os

class ChatbotKernel(MagicKernel):
    implementation = 'Chatbot'
    implementation_version = '1.0'
    language = 'text'
    language_version = '0.1'
    banner = "Chatbot kernel - a chatbot for IPython"

    def help_patterns(self):
        # Longest first:
        return [
            ("^\?\?(.*)$", 2,
             "??item - get detailed help on item"), # "??code"
            ("^\?(.*)$", 1,
             "?item - get help on item"),   # "?code"
        ]

    def __init__(self, *args, **kwargs):
        self.kernel = aiml.Kernel()
        os.chdir(os.path.join(os.path.dirname(aiml.__file__),
                              "standard"))
        self.kernel.learn("startup.xml")
        self.kernel.respond("load aiml b")
        os.chdir(os.path.join(os.path.dirname(aiml.__file__),
                              "alice"))
        self.kernel.learn("startup.xml")
        self.kernel.respond("load alice")
        super(ChatbotKernel, self).__init__(*args, **kwargs)

    def do_execute_direct(self, code):
        self.Print(self.kernel.respond(code))
        return None

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=ChatbotKernel)
