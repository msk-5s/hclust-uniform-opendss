# SPDX-License-Identifier: MIT

"""
This module contains enumerations for channels of a given monitor mode.
"""

import enum

#===================================================================================================
#===================================================================================================
class Load(enum.Enum):
    """
    Enums for the load monitor channels.

    These values are the channel indices to pass to the `IMonitors` COM
    interface.

    Notes
    -----
    These index values were obtained by looking at the order of the columns
    in the reports generated by `export`ing or `show`ing a monitor for the
    respective mode in the OpenDSS GUI software.
    """
    # Mode 0 channels (voltage magnitude and angle).
    MODE_0_V1 = 1