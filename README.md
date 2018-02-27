find-the-bus
===================

A school bus image processing application that runs on raspberry pi

Overview
--------

Do you ever wonder if the bus is on it's way while you are getting your 6 year old ready for school?  Yes?  Great!  This program is built as part of a larger Raspberry PI project to monitor the outside road for any incoming school buses.  When found, it will notify you via Slack and post the picture to an S3 bucket.


Requirements and Installation
******************************

We recommend using `PyPI <https://pypi.python.org/pypi>`_ to install Slack Developer Kit for Python

.. code-block:: bash

	git clone https://github.com/tjtar12/xs-busfinder.gitt


Documentation
--------------

All documentation is contained in the comments of the source code

Getting Help
-------------

If you get stuck, I'm sorry.  I barely have time to get this done the way I want it.  Do what I do, Google your issue


Basic Usage
------------
There two methods to executing the script:
  1. With a video file:

.. code-block:: bash

    python find_the_bus.py --video samples/bus_trials.mp4

  2. With live streaming:

.. code-block:: bash

    python find_the_bus.py
