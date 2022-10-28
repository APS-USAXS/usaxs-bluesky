
"""
Configure matplotlib in interactive mode for Jupyter notebook
"""

__all__ = ['plt',]

import logging

logger = logging.getLogger(__name__)
logger.info(__file__)

# %matplotlib notebook
get_ipython().magic('matplotlib notebook')
import matplotlib.pyplot as plt
plt.ion()
