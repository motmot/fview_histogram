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
