A Jupyter/IPython kernel for Xonsh

This requires IPython 3.

To install::

    pip install xonsh_kernel
    python -m xonsh_kernel.install

To use it, run one of:

.. code:: shell

    ipython notebook
    # In the notebook interface, select Xonsh from the 'New' menu
    ipython qtconsole --kernel xonsh
    ipython console --kernel xonsh

This is based on `MetaKernel <http://pypi.python.org/pypi/metakernel>`_,
which means it features a standard set of magics.

A sample notebook is available online_.


.. _online: http://nbviewer.ipython.org/github/Calysto/xonsh_kernel/blob/master/xonsh_kernel.ipynb
