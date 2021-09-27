# SPDX-License-Identifier: MIT

"""
The module contains functions for making load profiles.
"""

from typing import Any, List, NamedTuple, Sequence
from nptyping import NDArray

from rich.progress import track

import numpy as np

#===================================================================================================
#===================================================================================================
class Profile(NamedTuple):
    """
    A tuple for load profile information.

    Attributes
    ----------
    dss_commands : list of str
        The OpenDSS commands to create and add the load profile.
    element_name : str
        The name of the load element.
    values : numpy.ndarray of float, (n_timestep,)
        The time series values of the synthetic load profile.
    """
    dss_commands: Sequence[str]
    element_name: str
    values: NDArray[(Any,), float]

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def make_uniform_profiles(
    object_names: Sequence[str], rng: np.random.Generator, timestep_count: int
) -> List[Profile]:
    """
    Make a real power load profile for each OpenDSS object that follows a uniform distribution in
    the range [0, 1].

    Parameters
    ----------
    object_names : list of str
        The name of the OpenDSS objects to generate a load profile for.
    rng : numpy.random.Generator
        The random generator to use.
    timestep_count : int
        The number of timesteps to generate in each load profile.

    Returns
    -------
    list of profile_factory.Profile
        The new profiles for each object.
    """
    profiles = []

    for object_name in track(object_names, "Making sythethic profiles..."):
        element_name = object_name.split(".")[-1]
        profile_name = f"{element_name}_profile"

        # Generate uniform samples and convert them to a string of an OpenDSS array.
        new_profile = rng.uniform(low=0, high=1, size=timestep_count)
        values = [str(value) for value in new_profile]
        values = "[" + ", ".join(values) + "]"

        dss_commands = [
            f"new Loadshape.{profile_name} npts={timestep_count} interval=1 mult={values}",
            f"{object_name}.yearly={profile_name}"
        ]

        profile = Profile(dss_commands=dss_commands, element_name=element_name, values=new_profile)

        profiles.append(profile)

    return profiles
