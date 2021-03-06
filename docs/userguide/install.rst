 
Installation
============

The simplest way to install NNaPS is using pip from the terminal. This will install the latest stable release.

.. code-block:: bash
   
   pip install nnaps

If you want install the current development version you can also use pip:

.. code-block:: bash

   pip install git+https://github.com/vosjo/nnaps.git#egg=nnaps

To uninstall NNaPS, run:

.. code-block:: bash

   pip uninstall nnaps
   
.. _source:
   
From source
-----------   

NNaPS is hosted on github. If you want to make changes, clone the repository and install localy:

.. code-block:: bash
   
    python -m pip install -U pip
    python -m pip install -U setuptools
    git https://github.com/vosjo/nnaps.git
    cd nnaps
    pip install -e .


Test the installation
---------------------

To make sure that the installation went alright, you can execute some unit and integration tests.
To do this, you'll need to install from the source (see :ref:`source` above) and you need
`py.test <https://docs.pytest.org>`_:

.. code-block:: bash

    pip install -U pytest
    pytest -v nnaps/tests

This might take a few minutes but you should not get any errors if all went well.
