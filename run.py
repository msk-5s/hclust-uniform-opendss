# SPDX-License-Identifier: MIT

"""
This script generates a synthetic dataset from EPRI's ckt5 test feeder circuit.
"""

import os
import win32com.client

import numpy as np
import pandas as pd
import pyarrow.feather

import metadata_factory
import monitor_channel
import monitor_factory
import profile_factory

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(): # pylint: disable=too-many-locals
    """
    The main function.
    """
    # OpenDSS prefers full paths. Use the current directory of this script file.
    basepath = os.getcwd()

    #***********************************************************************************************
    # Get the OpenDSS engine object and load the circuit.
    #***********************************************************************************************
    print("Loading circuit...")

    dss = win32com.client.Dispatch("OpenDSSEngine.DSS")

    dss.Text.Command = "clearall"
    dss.Text.Command = f"redirect ({basepath}/ckt5-src/Master_ckt5.dss)"

    #***********************************************************************************************
    # Make monitors for the loads.
    #***********************************************************************************************
    load_object_names = [f"Load.{name}" for name in dss.ActiveCircuit.Loads.AllNames]

    load_monitors = monitor_factory.make_monitors(
        object_names=load_object_names, mode=0, terminal=1
    )

    # Add the monitors to the circuit.
    for monitor in load_monitors:
        dss.Text.Command = monitor.dss_command

    #***********************************************************************************************
    # Make synthetic load profiles.
    #***********************************************************************************************
    # Using a random generator allows us to recreate the same pseudorandom load profiles on each
    # run.
    rng = np.random.default_rng(seed=1337)

    timesteps_per_day = 96
    days = 7
    timestep_count = timesteps_per_day * days

    profiles = profile_factory.make_uniform_profiles(
        object_names=load_object_names, rng=rng, timestep_count=timestep_count
    )

    # Add the profiles and attach them to each load.
    for profile in profiles:
        for dss_command in profile.dss_commands:
            dss.Text.Command = dss_command

    #***********************************************************************************************
    # Save sythentic load profiles.
    #***********************************************************************************************
    print("Saving synthetic load profiles...")

    profile_df = pd.DataFrame(
        data = [profile.values for profile in profiles],
        columns = range(len(profiles[0].values)),
        index = [profile.element_name for profile in profiles]
    ).T

    pyarrow.feather.write_feather(df=profile_df, dest=f"{basepath}/data/load_profile.feather")

    # Free the profiles from memory since it can be a lot.
    del profiles
    del profile_df

    #***********************************************************************************************
    # Run simulation plan.
    #***********************************************************************************************
    print("Running simulation...")

    dss.Text.Command = f"set mode=yearly number={timestep_count}"
    dss.Text.Command = "solve"

    #***********************************************************************************************
    # Get data from monitors.
    #***********************************************************************************************
    load_voltage_df = monitor_factory.make_monitor_data(
        channel=monitor_channel.Load.MODE_0_V1.value, dss=dss, monitors=load_monitors
    )

    #***********************************************************************************************
    # Make the metadata.
    #***********************************************************************************************
    print("Making metadata...")

    metadata_df = metadata_factory.make_metadata(dss=dss)

    #***********************************************************************************************
    # Save data.
    #***********************************************************************************************
    print("Saving data...")

    pyarrow.feather.write_feather(df=load_voltage_df, dest=f"{basepath}/data/load_voltage.feather")
    pyarrow.feather.write_feather(df=metadata_df, dest=f"{basepath}/data/metadata.feather")

    print("...Done!")

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
