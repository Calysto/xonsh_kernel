A Calysto Jupyter kernel for Xonsh.

To install::

    pip install xonsh_kernel
    python -m xonsh_kernel.install

To use it, run one of:

.. code:: shell

    jupyter notebook
    # In the notebook interface, select 'Calysto Xonsh' from the 'New' menu
    ipython qtconsole --kernel calysto_xonsh
    ipython console --kernel calysto_xonsh

This is based on `MetaKernel <http://pypi.python.org/pypi/metakernel>`_,
which means it features a standard set of %%magics.  Note that this is
different from the kernel that is distributed with `Xonsh`.

A sample notebook is available online_.


.. _online: http://nbviewer.ipython.org/github/Calysto/xonsh_kernel/blob/master/xonsh_kernel.ipynb
