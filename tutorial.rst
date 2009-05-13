.. _fview-plugin-tutorial-histogram:

***************************************************************
FView plugin tutorial: live histogram of image intensity values
***************************************************************

This tutorial illustrates the steps necessary to compute and display a
live histogram of image intensity values.

A working copy of this code can be found at
http://github.com/motmot/fview_histogram/

Prerequisites
=============

 * Chaco_ installed (see the `Chaco docs`_ for more information).

.. _Chaco: http://code.enthought.com/projects/chaco/
.. _Chaco docs: http://code.enthought.com/projects/chaco/docs/html/index.html

Step 1 - Build the file layout
==============================

Your plugin will be a standard Python package. Create the following
directories (``base`` should be your base directory, such as
"fview_histogram")::

  base
  base/motmot
  base/motmot/fview_histogram

And create the following empty files::

  base/motmot/__init__.py
  base/motmot/fview_histogram/__init__.py

Step 2 - Create setup.py
========================

Now, edit ``base/setup.py`` to contain the following (modify as necessary)::

  from setuptools import setup, find_packages
  import sys,os

  setup(name='motmot.fview_histogram',
      description='live histogram plugin for FView',
      version='0.0.1',
      packages = find_packages(),
      author='Andrew Straw',
      author_email='strawman@astraw.com',
      url='http://code.astraw.com/projects/motmot',
      entry_points = {
    'motmot.fview.plugins':'fview_histogram = motmot.fview_histogram.fview_histogram:FviewHistogram',
    },
      )

This is a standard setuptools__ file for distributing and installing
Python packages that tells Python which files to install and some
associated meta-data.

__ http://pypi.python.org/pypi/setuptools

The ``packages = find_packages()`` line tells setuptools to look for
standard Python packages (directories with an __init__.py
file). Because you just created these directories and files in Step 1,
setuptools automatically knows these directories contain the files to
be installed.

The ``entry_points`` line tells setuptools that we want to register a
plugin. Our plugin is registered under the ``motmot.fview.plugins``
key. FView inquires for any plugins under this key. This particular
plugin is called ``fview_histogram``. It is defined in the
module ``motmot.fview_histogram.fview_histogram`` and
the class ``FviewHistogram``, which we create below.

Step 3 - Create a do-nothing plugin
===================================

Now we're going to create the module
``motmot.fview_histogram.fview_histogram`` with our new class
``FviewHistogram``. Open a new file named::

  base/motmot/fview_histogram/fview_histogram.py

The contents of this file::

  import motmot.fview.traited_plugin as traited_plugin

  class FviewHistogram(traited_plugin.HasTraits_FViewPlugin):
      plugin_name = 'image histogram'

      def camera_starting_notification(self,cam_id,
                                       pixel_format=None,
                                       max_width=None,
                                       max_height=None):

          # This function gets called from FView when a camera is
          # initialized.

          return

      def process_frame(self,cam_id,buf,buf_offset,timestamp,framenumber):
          draw_points = []
          draw_linesegs = []

          # This function gets called from FView immediately after
          # acquisition of each frame. Implement your image processing
          # logic here.

          return draw_points, draw_linesegs


Step 4 - Create the plugin logic
================================

From here, we're going to fill in the relevant parts with the code
that our plugin executes. The most important function is
**process_frame()**. This function is called by FView immediately
after every frame is acquired from the camera. The arguments to the
function contain information about this latest frame, and the return
values are used to plot points and line segments on the main FView
display. For the live histogram, we don't need to display anything, so
we just return empty lists.

The contents of this file::

  import warnings, time
  import enthought.traits.api as traits
  import motmot.fview.traited_plugin as traited_plugin
  import numpy as np
  from enthought.traits.ui.api import View, Item, Group
  from enthought.chaco.chaco_plot_editor import ChacoPlotItem

  # For a tutorial on Chaco and Traits, see
  # http://code.enthought.com/projects/chaco/docs/html/user_manual/tutorial_2.html

  class FviewHistogram(traited_plugin.HasTraits_FViewPlugin):
      plugin_name = 'image histogram'
      update_interval_msec = traits.Int(100)

      # The following traits are "transient" -- do not attempt to make
      # state persist across multiple runs of the application.

      intensity = traits.Array(dtype=np.float,transient=True)
      data = traits.Array(dtype=np.float,transient=True)

      pixel_format = traits.String(None,transient=True)

      last_update_time = traits.Float(-np.inf,transient=True)

      # Define the view using Traits UI

      traits_view = View(
          Group(
                  ChacoPlotItem('intensity','data',
                                x_label = 'intensity',
                                y_label = '',
                                show_label=False,
                                y_auto=True,
                                resizable=True,
                                title = 'Image intensity histogram',
                                ),
                  ),
          resizable=True,
          )

      def camera_starting_notification(self,cam_id,
                                       pixel_format=None,
                                       max_width=None,
                                       max_height=None):
          self.pixel_format = pixel_format
          self.intensity = np.linspace(0,255,50) # 50 bins from 0-255

      def process_frame(self,cam_id,buf,buf_offset,timestamp,framenumber):
          draw_points = []
          draw_linesegs = []

          if self.frame.IsShown():
              now = time.time()

              # Throttle the computation and display to happen only
              # occasionally. The display of the histogram, especially,
              # is computationally intensive.

              if (now - self.last_update_time)*1000.0 > self.update_interval_msec:
                  npbuf = np.array(buf)
                  if self.pixel_format == 'MONO8':
                      self.data, edges = np.histogram(npbuf,
                                                      bins=self.intensity,
                                                      new=True)
                  else:
                      warnings.warn("histogram for %s format not implemented"%(
                          self.pixel_format,))
                  self.last_update_time = now

          return draw_points, draw_linesegs

Afterward: optional improvements
================================

As implemented above, the live plot of the histogram is automatically
updated whenever the ``self.data`` attribute changes. While this is
convenient, there's a problem with this. The ``process_frame()``
method is called in the camera acquisition and processing thread, and
any computationally expensive process will slow down this
thread. Drawing auto-scaled plots certainly qualifies as
computationally intensive. Therefore, it would be better to calculate
the histogram values as done here, but then to send them to another
thread for display in the GUI. This would allow the image acquisition
thread to operate unimpeded, but would require multi-threaded
programming, which is beyond the scope of this tutorial.
