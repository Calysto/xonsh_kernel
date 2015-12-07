from __future__ import print_function

from metakernel import MetaKernel, ProcessMetaKernel, REPLWrapper, u
import builtins
import os
builtins.__xonsh_env__ = os.environ.copy()
builtins.aliases = []
from xonsh import completer
import re


__version__ = '0.2.0'


class XonshKernel(ProcessMetaKernel):
    implementation = 'Xonsh Kernel'
    implementation_version = __version__,
    language = 'xonsh'
    language_version = '0.1',
    banner = "Matlab Kernel"
    language_info = {
        'mimetype': 'text/x-bash',
        'name': 'xonsh_kernel',
        'file_extension': '.sh',
        'help_links': MetaKernel.help_links,
    }

    def makeWrapper(self):
        """Start an xonsh shell and return a :class:`REPLWrapper` object.
        Note that this is equivalent :function:`metakernel.pyexpect.bash`,
        but is used here as an example of how to be cross-platform.
        """
        if os.name == 'nt':
            prompt_regex = u('__repl_ready__')
            prompt_emit_cmd = u('echo __repl_ready__')
            prompt_change_cmd = None

        else:
            prompt_regex = re.compile('[$#]')
            prompt_change_cmd = u("$PROMPT='{0}'; $MULTILINE_PROMPT='{1}'")
            prompt_emit_cmd = None

        extra_init_cmd = "$PAGER='cat'"
        os.environ['PAGER'] = 'cat'
        self.completer = completer.Completer()
        return REPLWrapper('xonsh', prompt_regex, prompt_change_cmd,
                           prompt_emit_cmd=prompt_emit_cmd,
                           extra_init_cmd=extra_init_cmd)

    def do_execute_direct(self, code):
        output = super(XonshKernel, self).do_execute_direct(code)
        output = output.splitlines()
        return '\n'.join(output[:-1])

    def get_completions(self, info):
        start = info['column'] - len(info['obj'])
        comps = self.completer.complete(info['obj'], info['line'], start,
                                        info['column'])
        shell_magic = self.line_magics['shell']
        return comps + shell_magic.get_completions(info)

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        output = self.do_execute_direct('man %s' % obj)
        if output.startswith('No manual entry for'):
            output = self.do_execute_direct('help(%s)' % obj)
        return output

if __name__ == '__main__':
    from IPython.kernel.zmq.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=XonshKernel)
