from __future__ import print_function
import io
import builtins
from pprint import pformat
import os
from tempfile import SpooledTemporaryFile

from metakernel import MetaKernel
from xonsh import __version__ as version
from xonsh.tools import redirect_stdout, redirect_stderr, swap
try:
    from xonsh.tools import ON_POSIX
except ImportError:
    ON_POSIX=None
    pass

from . import __version__

MAX_SIZE = 8388608  # 8 Mb

if ON_POSIX:
    os.environ['PAGER'] = 'cat'


class XonshKernel(MetaKernel):
    implementation = 'Calysto Xonsh Kernel'
    implementation_version = __version__
    language = 'xonsh'
    language_version = version
    banner = 'Xonsh - the Python-ish, BASHwards-looking shell'
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
                self._respond_in_chunks('stdout', out.strip())
            if err:
                self._respond_in_chunks('stderr', err.strip())
            if hasattr(builtins, '_') and builtins._ is not None:
                # rely on sys.displayhook functionality
                self._respond_in_chunks('stdout', pformat(builtins._))
                builtins._ = None
            if len(hist) > 0 and not out and not err:
                return hist.outs[-1]

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
        out.close()
        err.close()
        return output, error, interrupted

    def _respond_in_chunks(self, name, s, chunksize=1024):
        if s is None:
            return
        n = len(s)
        if n == 0:
            return
        lower = range(0, n, chunksize)
        upper = range(chunksize, n+chunksize, chunksize)
        for l, u in zip(lower, upper):
            if name == 'stderr':
                self.Error(s[l:u])
            else:
                self.Print(s[l:u])

    def get_kernel_help_on(self, info, level=0, none_on_fail=False):
        obj = info.get('help_obj', '')
        if not obj or len(obj.split()) > 1:
            if none_on_fail:
                return None
            else:
                return ""
        output = ''
        if ON_POSIX:
            output, _, _ = self._do_execute_direct('man %s' % obj)
            if output.startswith('No manual entry for'):
                output = ''
        else:
            output, _, _, = self._do_execute_direct('help %s' % obj)
            if output.startswith('This command is not supported'):
                output = ''
        if not output:
            output, _, _ = self._do_execute_direct('help(%s)' % obj)
        return output
