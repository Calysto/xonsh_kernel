from __future__ import print_function
import io
import builtins

from metakernel import MetaKernel
from xonsh import __version__ as version
from xonsh.tools import redirect_stdout, redirect_stderr

from . import __version__


class XonshKernel(MetaKernel):
    implementation = 'Xonsh Kernel'
    implementation_version = __version__
    language = 'xonsh'
    language_version = version
    banner = 'Xonsh - the Python-ish, BASHwards-looking shell'
    language_info = {'name': 'xonsh',
                     'pygments_lexer': 'xonsh',
                     'codemirror_mode': 'shell',
                     'mimetype': 'text/x-sh',
                     'file_extension': '.xsh',
                     }

    def do_execute_direct(self, code, silent=False):
        shell = builtins.__xonsh_shell__
        hist = builtins.__xonsh_history__
        out = io.StringIO()
        err = io.StringIO()
        self.Print(code)
        try:
            with redirect_stdout(out), redirect_stderr(err):
                shell.default(code)
            interrupted = False
        except KeyboardInterrupt:
            interrupted = True

        if not silent:  # stdout response
            if out.tell() > 0:
                out.seek(0)
                self.Print(out.read())
            if err.tell() > 0:
                err.seek(0)
                self.Error(err.read())
            if len(hist) > 0 and out.tell() == 0 and err.tell() == 0:
                self.Print(hist.outs[-1])
                response = {'name': 'stdout', 'text': hist.outs[-1]}
                self.send_response(self.iopub_socket, 'stream', response)

        if interrupted:
            return

        rtn = 0 if len(hist) == 0 else hist.rtns[-1]
        if 0 < rtn:
            self.Error(rtn)

    def do_complete(self, code, pos):
        """Get completions."""
        shell = builtins.__xonsh_shell__
        comps, beg, end = shell.completer.find_and_complete(code, pos, shell.ctx)
        message = {'matches': comps, 'cursor_start': beg, 'cursor_end': end+1,
                   'metadata': {}, 'status': 'ok'}
        return message

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
