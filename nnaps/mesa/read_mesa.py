import os
import warnings


from pathlib import Path
import numpy as np

from . import fileio


def read_mesa_output(filename=None, only_first=False):
    """
    Read star.log and .data files from MESA.

    This returns a record array with the global and local parameters (the latter
    can also be a summary of the evolutionary track instead of a profile if
    you've given a 'star.log' file.

    The stellar profiles are given from surface to center.

    Function writen by Pieter DeGroote

    @param filename: name of the log file
    @type filename: str
    @param only_first: read only the first model (or global parameters)
    @type only_first: bool
    @return: list of models in the data file (typically global parameters, local parameters)
    @rtype: list of rec arrays
    """
    models = []
    new_model = False
    header = None
    # -- open the file and read the data
    with open(filename, 'r') as ff:
        # -- skip first 5 lines when difference file
        if os.path.splitext(filename)[1] == '.diff':
            for i in range(5):
                line = ff.readline()
            models.append([])
            new_model = True
        while 1:
            line = ff.readline()
            if not line:
                break  # break at end-of-file
            line = line.strip().split()
            if not line:
                continue
            # -- begin a new model
            if all([iline == str(irange) for iline, irange in zip(line, range(1, len(line) + 1))]):
                # -- wrap up previous model
                if len(models):
                    model = np.array(models[-1], float).T
                    models[-1] = np.rec.fromarrays(model, names=header)
                    if only_first: break
                models.append([])
                new_model = True
                continue
            # -- next line is the header of the data, remember it
            if new_model:
                header = line
                new_model = False
                continue
            models[-1].append(line)
    if len(models) > 1:

        try:
            model = np.array(models[-1], float).T
        except:
            indices = []
            for i, l in enumerate(models[-1]):
                if len(l) != len(models[-1][0]):
                    indices.append(i)

            for i in reversed(indices):
                del models[-1][i]
            print("Found and fixed errors on following lines: ", indices)
            model = np.array(models[-1], float).T

        models[-1] = np.rec.fromarrays(model, names=header)

    return models


def get_end_log_file(logfile):
    if os.path.isfile(logfile):
        # case for models ran locally
        ifile = open(logfile)
        lines = ifile.readlines()
        ifile.close()

        return lines[-30:-1]
    else:
        return []


def convert2hdf5(modellist, star_columns=None, binary_columns=None, add_stopping_condition=True, skip_existing=True,
                 star1_history_file='LOGS/history1.data', star2_history_file='LOGS/history2.data',
                 binary_history_file='LOGS/binary_history.data', log_file='log.txt',
                 input_path_kw='path', input_path_prefix='', output_path=None, verbose=False):

    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    for i, model in modellist.iterrows():

        if not os.path.isdir(Path(input_path_prefix, model[input_path_kw])):
            continue

        if skip_existing and os.path.isfile(Path(output_path, model[input_path_kw]).with_suffix('.h5')):
            if verbose:
                print (i, model[input_path_kw], ': exists, skipping')
            continue

        if verbose:
            print(i, model[input_path_kw], ': processing')

        # store all columns of the input file in the hdf5 file
        data = {}
        for col in model.index:
            data[col] = model[col]

        # check if all history files that are requested are available and can be read. If there is an error,
        # skip to the next model
        history = {}
        if star1_history_file is not None:
            try:
                d1 = read_mesa_output(Path(input_path_prefix, model[input_path_kw], star1_history_file))[1]
                if star_columns is not None:
                    d1 = d1[star_columns]
                history['star1'] = d1
            except Exception as e:
                if verbose:
                    print("Error in reading star1: ", e)
                continue

        if star2_history_file is not None:
            try:
                d2 = read_mesa_output(Path(input_path_prefix, model[input_path_kw], star2_history_file))[1]
                if star_columns is not None:
                    d2 = d2[star_columns]
                history['star2'] = d2
            except Exception as e:
                if verbose:
                    print("Error in reading star2: ", e)
                continue

        if binary_history_file is not None:
            try:
                d3 = read_mesa_output(Path(input_path_prefix, model[input_path_kw], binary_history_file))[1]
                if star_columns is not None:
                    d3 = d3[binary_columns]
                history['binary'] = d3
            except Exception as e:
                if verbose:
                    print("Error in reading binary: ", e)
                continue

        data['history'] = history

        # obtain the termination code
        termination_code = 'uk'
        if add_stopping_condition:
            lines = get_end_log_file(Path(input_path_prefix, model[input_path_kw], log_file))
            for line in lines:
                if 'termination code' in line:
                    termination_code = line.split()[-1]

        data['termination_code']=termination_code

        fileio.write2hdf5(data, Path(output_path, model[input_path_kw]).with_suffix('.h5'), update=False)