from __future__ import print_function
import io
import builtins
from pprint import pformat
from tempfile import SpooledTemporaryFile

from metakernel import MetaKernel
from xonsh import __version__ as version
from xonsh.tools import redirect_stdout, redirect_stderr, swap

from . import __version__

MAX_SIZE = 8388608  # 8 Mb


class XonshKernel(MetaKernel):
    implementation = 'Calysto Xonsh Kernel'
    implementation_version = __version__
    language = 'xonsh'
    language_version = version
    banner = 'Calysto Xonsh - the Python-ish, BASHwards-looking shell'
    language_info = {'name': 'xonsh',
                     'pygments_lexer': 'xonsh',
                     'codemirror_mode': 'shell',
                     'mimetype': 'text/x-sh',
                     'file_extension': '.xsh',
                     'version': __version__
                     }

    def do_execute_direct(self, code, silent=False):
        out, err, interrupted = self._do_execute_direct(code)
        hist = builtins.__xonsh_history__
        if not silent:  # stdout response
            if out:
                self.Print(out)
            if err:
                self.Error(err)
            if len(hist) > 0 and out and not err:
                self.Print(hist.outs[-1])
                response = {'name': 'stdout', 'text': hist.outs[-1]}
                self.send_response(self.iopub_socket, 'stream', response)

        if interrupted:
            return

        rtn = 0 if len(hist) == 0 else hist.rtns[-1]
        if 0 < rtn:
            self.Error(rtn)

    def _do_execute_direct(self, code):
        shell = builtins.__xonsh_shell__
        env = builtins.__xonsh_env__
        out = io.StringIO()
        err = io.StringIO()
        enc = env.get('XONSH_ENCODING')
        out = SpooledTemporaryFile(max_size=MAX_SIZE, mode='w+t',
                                   encoding=enc, newline='\n')
        err = SpooledTemporaryFile(max_size=MAX_SIZE, mode='w+t',
                                   encoding=enc, newline='\n')
        try:
            with redirect_stdout(out), redirect_stderr(err), \
                 swap(builtins, '__xonsh_stdout_uncaptured__', out), \
                 swap(builtins, '__xonsh_stderr_uncaptured__', err), \
                 env.swap({'XONSH_STORE_STDOUT': False}):
                shell.default(code)
            interrupted = False
        except KeyboardInterrupt:
            interrupted = True
        output, error = '', ''
        if out.tell() > 0:
            out.seek(0)
            output = out.read()
        if err.tell() > 0:
            err.seek(0)
            error = err.read()
        return output, error, interrupted

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
        output, _, _ = self._do_execute_direct('man %s' % obj)
        if output.startswith('No manual entry for'):
            output, _, _ = self._do_execute_direct('help(%s)' % obj)
        return output
