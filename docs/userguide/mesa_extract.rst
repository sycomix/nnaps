
MESA extract
============

**nnaps-mesa** -extract <*model_directory*> -o <*output_file.csv*> [*options*]

.. program:: nnaps-mesa

.. option:: -extract model_directory

    The extract option, used to extract model parameters from MESA models stored in hdf5 format.

    **model_directory** mandatory argument. The directory containing all mesa models in hdf5 format.

.. option:: -o output

    The name of the csv file where nnaps-mesa will write the extracted parameters for all models.

.. option:: -setup setup_file

    yaml file containing the detailed setup for the compression.

    If not setup file is give, nnaps-mesa will look for one in the current directory or in the *<user>/.nnaps*
    directory. In that case the filename of the setup file needs to be *defaults_extract.yaml*.

    If no setup file can be found anywhere, nnaps-mesa will use the defaults stored in the mesa.defaults module.

Basic usage
-----------

The most simple way to run the extract command is to provide it with the folder where the compressed models are located
and the filename to store the extracted parameters in:

.. code-block:: bash

    nnaps-mesa -extract <input folder> -o <output csv filename>

Using the default settings this will for each model:

    1. check if the model is stable using the default criterion: max(lg_mstar_dot_1) < -2
    2. if the model is unstable, apply the CE formalism of Iben & Tutukov 1984
    3. check if a contact binary is formed during evolution
    4. extract the default parameters (see defaults)

The exact function will then save the default parameters for each model to a csv file.

Setup file
----------

Using a setup file allows you to set different parameters for the extraction including the stability criterion,
which parameters to extract and more.

The setup file has to be structured in yaml format, and can be provided using the *-setup* option.

.. code-block:: yaml

    stability_criterion: J_div_Jdot_div_P
    stability_limit: 10
    ce_formalism: 'dewi_tauris2000'
    ce_parameters: {'a_ce': 0.3, 'a_th': 0.5}
    ce_profile_name: 'profile_1_jdotp10.0'
    parameters: []
    phase_flags: []
    extra_info_parameters: []

.. option:: stability_criterion (str)

    The stability criterion to use when judging is the mass loss is stable. Has to be combined with
    :option:`stability_limit` to set the value above or below which the model is unstable.

.. option:: stability_limit (float)

    The value for the stability criterion above or below which the model is considered unstable. Use
    :option:`stability_criterion` to set which criterion to use.

.. option:: ce_formalism (str)

    The name of the CE formalism to use

.. option:: ce_parameters (dict)

    Custom parameters for the CE formalism

.. option:: ce_profile_name (str)

    If a CE formalism is chosen that needs a profile, you can use this argument to give the name of the profile to use.
    If no name is specified, the profile with the model number closest to when the stability criterion is trip will be
    used.

.. option:: parameters (list)

    Which parameters to extract from the models. See `Parameters`_ for an explanation on how to structure
    parameter names.

.. option:: phase_flags (list)

    Which phase flags to extract from the models.

.. option:: extra_info_parameters (list)

    Which extra info parameters to extract from the models.

Stability criteria
------------------

Current implemented stability criteria and how they are triggered are:

- Mdot: lg_mstar_dot_1 > value
- delta: mass_transfer_delta > value
- J_div_Jdot_div_P: 10**log10_J_div_Jdot_div_P < value
- M_div_Mdot_div_P: 10**log10_M_div_Mdot_div_P < value
- R_div_SMA: star_1_radius / binary_separation > value

An up to date list of all stability criteria can be obtained with:

.. code-block:: python

    from nnaps.mesa.common_envelope import STABILITY_CRITERIA
    print(STABILITY_CRITERIA)

For more info on the stability criteria see: :doc:`mesa_common_envelope`

CE formalisms
-------------

The different CE formalisms implemented in NNaPS-mesa are:

- iben_tutukov1984: `Iben & Tutukov 1984, ApJ, 284, 719 <https://ui.adsabs.harvard.edu/abs/1984ApJ...284..719I/abstract>`_
- webbink1984: `Webbink 1984, ApJ, 277, 355 <https://ui.adsabs.harvard.edu/abs/1984ApJ...277..355W/abstract>`_
- dewi_tauris2000: `Dewi and Tauris 2000, A&A, 360, 1043 <https://ui.adsabs.harvard.edu/abs/2000A%26A...360.1043D/abstract>`_
- demarco2011: `De Marco et al. 2011, MNRAS, 411, 2277 <https://ui.adsabs.harvard.edu/abs/2011MNRAS.411.2277D/abstract>`_

An up to date list of all recognized CE formalisms can be obtained with:

.. code-block:: python

    from nnaps.mesa.common_envelope import CE_FORMALISMS
    print(CE_FORMALISMS)

For more info on the common envelope formalisms see: :doc:`mesa_common_envelope`

Parameters
----------

To extract useful information from a MESA model you are likely interested in parameter values at a certain moment in
evolution, or during a certain evolutionary phase. *nnaps-mesa* allows you to easily extract parameters and apply
aggregate functions on a parameter during a specified phase.

A parameter to extract consists of 3 parts divided by a double underscore '__': the name of the parameter that you are
interested in, the phase or exact point in time and potentially the function to apply. Not all three parts need to be
present, both the evolution_phase and/or the agregate_function can be omitted:

    <parameter_name>__<evolution_phase>__<agregate_function>

Easiest way to demonstrate how this works is by example:

- *star_1_mass__init*: mass of the primary at the start of the run.
- *rl_1__max* : max of the roche lobe size of the primary star during the entire evolution.
- *age__HeCoreBurning__diff*: Difference in age between the start and end of the He core burning phase or in other words: the duration of He core burning.
- *T_effective__ML__min*: The minimum of the effective temperature during the mass loss phase.
- *he_core_mass__HeShellBurning__avg*: average He core mass during the He shell burning phase.
- *star_1_mass__ML__rate*: The average mass loss rate during the mass loss phase in Msol / yr.

If you don't like the long name that a parameter can get using this formalism, you can provide the parameter as a tuple
where the first item contains the parameter name following the formalism above, and the second the name that you want to
use in the csv file. You only have to provide an alternative name for the parameters that you want to rename. In the
yaml setup file this would look like:

.. code-block:: yaml

    ...
    parameters:
    - star_1_mass__init, M1_init
    - rl_1__max
    - age__HeCoreBurning__diff, HeCoreBurning_time
    ...

Evolution phases
^^^^^^^^^^^^^^^^

NNaPS MESA can recognize a many different evolution phases:

- init
- final
- ML
- MLstart
- MLend
- CE
- CEstart
- CEend
- HeIgnition
- HeCoreBurning
- HeShellBurning
- sdA
- sdB
- sdO
- He_WD

An overview of the different phases is given in :doc:`mesa_evolution_phases`, together with the parameters the MESA track
needs to contain to recognize the phase.

An up to date list of all recognized phases can be obtained with:

.. code-block:: python

    from nnaps.mesa.evolution_phases import EVOLUTION_PHASES
    print(EVOLUTION_PHASES)

Phase flags
^^^^^^^^^^^
The evolution phase can also be used as 'phase flags'. In that case NNaPS will check if the systems goes though
a phase or not. For each phase included in the :option:`phase_flags` option, NNaPS will add a column to the resulting
csv file containing True if that model had that phase, or False otherwise. You can use this to easily detect which
systems undergo which phases.

Example, if you want to check if your system becomes an sdB or a He-WD you can add:

.. code-block:: yaml

    ...
    phase_flags:
    - sdB
    - He-WD
    ...

Agregate functions
^^^^^^^^^^^^^^^^^^

The different agregate functions that NNaPS mesa recognizes are:

- *max*: maximum
- *min*: minimum
- *avg*: average
- *diff*: takes the difference between the end and start of the phase: diff = par_end - par_start
- *rate*: calculates the difference over time: rate = (par_end - par_start) / (age_end-age_start). Uses age in years.

An up to date list of all recognized agregate functions can be obtained with:

.. code-block:: python

    from nnaps.mesa.evolution_phases import AGREGATE_FUNCTIONS
    print(AGREGATE_FUNCTIONS)

Advanced phases
^^^^^^^^^^^^^^^

In some cases you will want to obtain the value of a parameters at a point in time that is not directly defined by one
of the included evolution phases, and which might not be a fixed phase in a stars evolution. NNaPS-mesa offers some
support to define points based on the value of a different parameter included in the run.

To use this functionality  replace the <evolution_phase> in the parameter name by the name of the parameter that you
want to base the moment on and combine that with either max or min to define the moment during the evolution that this
parameter reaches its minimum or maximum. For example, if you want to get the value of the He core mass at the time that
the mass loss will reach its maximum, you can define a parameter as follows:

    he_core_mass__lg_mstar_dot_1_max

The first part, *he_core_mass*, defines the parameter that you want the value of. The second part, *lg_mstar_dot_1_max*,
defines the point in time you want to use. In this case that time point is defined as when *lg_mstar_dot_1* reaches its
maximum value.