from __future__ import with_statement, division

import pkg_resources
import warnings, time
import enthought.traits.api as traits

import motmot.fview.traited_plugin as traited_plugin
import motmot.fview_ext_trig.ttrigger as ttrigger
import numpy as np

# For a tutorial on Chaco and Traits, see
# http://code.enthought.com/projects/chaco/docs/html/user_manual/tutorial_2.html

from enthought.traits.ui.api import View, Item, Group
from enthought.chaco.chaco_plot_editor import ChacoPlotItem

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
        width=800, height=200,
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
