# SPDX-License-Identifier: BSD-3-Clause

"""
This script contains functions for creating metadata for the EPRI ckt5 test
circuit.
"""

import win32com.client

from typing import List, Sequence

import pandas as pd

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def _make_load_phase_labels(dss: win32com.client.CDispatch, load_names: Sequence[str]) -> List[int]:
    """
    Make the phase labels of the loads.

    Parameters
    ----------
    dss : win32com.client.CDispatch
        The OpenDSSEngine object.
    load_names : list of str, (n_loads,)
        The load names.

    Returns
    -------
    list of int, (n_loads,)
        The load phase labels.
    """
    load_buses = []

    for name in load_names:
        # The `ILoads` COM interface doesn't have a `Bus1` property.
        dss.Text.Command = f"? load.{name}.bus1"
        load_bus = str(dss.Text.Result)

        load_buses.append(load_bus)

    # Since these are Y-connected loads, there is only a single terminal
    # connected for the respective phase. Phase A = 1, B = 2, C = 3.
    # We subtract 1 so that the phases start at 0. Phase A = 0, etc.
    load_phases = [int(bus.split(sep=".")[1]) - 1 for bus in load_buses]

    return load_phases

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_metadata(dss: win32com.client.CDispatch) -> pd.DataFrame:
    """
    Make the metadata for the loads.

    Parameters
    ----------
    dss : win32com.client.CDispatch
        The OpenDSSEngine object.

    Returns
    -------
    pandas.DataFrame, (n_loads, n_fields)
        The load metadata.
    """
    #***************************************************************************
    # Make the various metadata pieces.
    #***************************************************************************
    load_names = list(dss.ActiveCircuit.Loads.AllNames)
    load_phases = _make_load_phase_labels(dss=dss, load_names=load_names)

    #***************************************************************************
    # Make the metadata data frame.
    #***************************************************************************
    metadata_df = pd.DataFrame(data={"load_name": load_names, "phase": load_phases})

    return metadata_df
