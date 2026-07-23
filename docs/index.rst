Bixi API Client
===============

Overview
--------

``bixi-sdk`` is a Python SDK for the BIXI Montréal bike-sharing system. It lets
you log into a Bixi account and query ride history and station information.

Installation
------------

Install the package from PyPI:

.. code-block:: console

   pip install bixi-sdk

Example
-------

.. code-block:: python

   from bixi.bixi import Bixi

   client = Bixi.login(username="my-username", password="my-password")

   for ride in client.rides():
       print(ride.start_station_name, "->", ride.end_station_name)

   for station in client.stations():
       print(station.name, station.lat, station.lng)

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
