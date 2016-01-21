"""Example use of jupyter_kernel_test, with tests for IPython."""

import unittest
import jupyter_kernel_test as jkt


class XonshKernelTests(jkt.KernelTests):
    kernel_name = "calysto_xonsh"

    language_name = "xonsh"

    code_hello_world = "print('hello, world')"

    completion_samples = [
        {
            'text': 'frozense',
            'matches': {'frozenset'},
        },
    ]

    code_page_something = "print?"

if __name__ == '__main__':
    unittest.main()
