when.events
-----------

when.events_ is a website collecting event and CfP dates. Currently, you can
add events by submitting them to the when.events API, but manual event addition
is planned for a later date.


Event submission
================

To submit an event, gather all relevant event metadata in the following format
(which is inspired by past experience and https://schema.org/Event), and put it
online in a stable location::

   {TBD}

Then send a POST request with your URL to the when.events API::

   curl --TBD

when.events will then retrieve the data and will continue to periodically check for updates.


This is a project by Tobias 'rixx' Kunze.

.. _when.events: https://when.events
