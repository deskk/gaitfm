# name: gait_event_mocap.py
# description: obtain gait parameters using mocap data
# author: Vu Phan
# date: 2024/04/07


import pandas as pd
import numpy as np

from tqdm import tqdm
from scipy import signal
from scipy.signal import find_peaks

import constants_meta

import sys, os
sys.path.append('/path/to/acl_work')

from utils import common, visualizer
from utils.mt import constants_mt
from utils.mocap import constants_mocap


# # --- Remove noisy peaks --- #
# def remove_noisy_peaks_mocap(raw_index, raw_value, task):
#     ''' Keeps peaks during walking only

#     Args:
#         + raw_index, raw_value (np.array): outputs from np.find_peaks

#     Returns:
#         + index, value (np.array): index and value of a specific gait event during walking
#     '''
#     # if task == 'treadmill_walking':
#     #     threshold_1 = np.mean(raw_value) + 0.1*np.std(raw_value)
#     #     threshold_2 = np.mean(raw_value) - 2*np.std(raw_value)
#     # elif task == 'walking':
#     #     threshold_1 = np.mean(raw_value) + 0.5*np.std(raw_value)
#     #     threshold_2 = np.mean(raw_value) - 2*np.std(raw_value)
#     #
#     # id1         = np.where(raw_value < threshold_1)[0]
#     # id2         = np.where(raw_value > threshold_2)[0]
#     # selected_id = np.intersect1d(id1, id2)
#     # index       = 1*raw_index[selected_id]
#     # value       = 1*raw_value[selected_id]

#     alpha = 0.5

#     value_sorted = 1*raw_value
#     value_sorted.sort()
#     upper_bound  = np.mean(value_sorted[::20])
#     lower_bound  = np.mean(value_sorted[-20::])

#     threshold   = alpha*upper_bound + (1 - alpha)*lower_bound
#     selected_id = np.where(raw_value < threshold)[0]
#     index       = 1*raw_index[selected_id]
#     value       = 1*raw_value[selected_id]

#     return index, value

# --- Calculate the angle between two vectors --- #
def angle_between_vectors(v1, v2):
    ''' Calculate the angle between two vectors

    Args:
        + v1, v2 (np.array): two vectors

    Returns:
        + angle (float): angle between two vectors
    '''
    angle = np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
    angle = np.degrees(angle)
    angle = np.abs(angle)

    return angle


# --- Identify heel-contact and toe-off events from the mocap data --- #
# Method using the height of heel and toe markers
def ge_heel_toe_height(marker_traj, fs = 100, correction = None, vis = False):
    ''' Obtain gait events from the height of heel and toe markers
    '''
    min_peak_distance_hc = fs*0.6
    min_peak_distance_to = fs*0.6
    gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    heel_marker_y                = marker_traj['heel_marker_y']
    temp_hc_index, temp_hc_value = find_peaks(-1*heel_marker_y, height = [-1, 0], distance = min_peak_distance_hc)
    # hc_index                     = 1*temp_hc_index
    # hc_value                     = -1*temp_hc_value['peak_heights']
    # hc_index, hc_value           = remove_noisy_peaks_mocap(hc_index, hc_value, 'walking')

    for i in range(1, len(temp_hc_index)):
        prev_vec = np.array([marker_traj['sacrum_marker1_x'][temp_hc_index[i - 1]] - marker_traj['sacrum_marker2_x'][temp_hc_index[i - 1]], marker_traj['sacrum_marker1_z'][temp_hc_index[i - 1]] - marker_traj['sacrum_marker2_z'][temp_hc_index[i - 1]]])
        curr_vec = np.array([marker_traj['sacrum_marker1_x'][temp_hc_index[i]] - marker_traj['sacrum_marker2_x'][temp_hc_index[i]], marker_traj['sacrum_marker1_z'][temp_hc_index[i]] - marker_traj['sacrum_marker2_z'][temp_hc_index[i]]])
        angle    = angle_between_vectors(prev_vec, curr_vec)
        if angle < 90:
            gait_events['hc_index'].append(temp_hc_index[i])
        # gait_events['hc_index'].append(temp_hc_index[i])


    toe_marker_y                 = marker_traj['toe_marker_y']
    temp_to_index, temp_to_value = find_peaks(-1*toe_marker_y, height = [-1, 0], distance = min_peak_distance_to)

    for i in range(1, len(temp_to_index)):
        prev_vec = np.array([marker_traj['sacrum_marker1_x'][temp_to_index[i - 1]] - marker_traj['sacrum_marker2_x'][temp_to_index[i - 1]], marker_traj['sacrum_marker1_z'][temp_to_index[i - 1]] - marker_traj['sacrum_marker2_z'][temp_to_index[i - 1]]])
        curr_vec = np.array([marker_traj['sacrum_marker1_x'][temp_to_index[i]] - marker_traj['sacrum_marker2_x'][temp_to_index[i]], marker_traj['sacrum_marker1_z'][temp_to_index[i]] - marker_traj['sacrum_marker2_z'][temp_to_index[i]]])
        angle    = angle_between_vectors(prev_vec, curr_vec)
        if angle < 90:
            gait_events['to_index'].append(temp_to_index[i])
        # gait_events['to_index'].append(temp_to_index[i])

    if correction == 'eric_lauren_correction':
        to_index, to_value = eric_lauren_correction(temp_to_index, -1*temp_to_value['peak_heights'], toe_marker_y, fs)
    elif correction == 'vu_correction':
        to_index, to_value = vu_correction(temp_to_index, -1*temp_to_value['peak_heights'], toe_marker_y, fs)
    else:
        to_index = 1*temp_to_index
        to_value = -1*temp_to_value['peak_heights']
    # to_index, to_value = remove_noisy_peaks_mocap(to_index, to_value, 'walking')

    # gait_events['hc_index'] = hc_index
    # gait_events['hc_value'] = hc_value
    # gait_events['to_index'] = to_index
    # gait_events['to_value'] = to_value
    gait_events['hc_index'] = np.array(gait_events['hc_index'])
    gait_events['hc_value'] = np.array(gait_events['hc_value'])
    gait_events['to_index'] = np.array(gait_events['to_index'])
    gait_events['to_value'] = np.array(gait_events['to_value'])

    if vis:
        visualizer.plot_gait_events_mocap(heel_marker_y, toe_marker_y, gait_events)

    return gait_events

def eric_lauren_correction(near_to_index, temp_to_value, toe_marker_y, fs = 100):
    ''' Eric and Lauren correction when using metatarsal instead of toe markers
    '''
    toe_marker_y_vel = np.diff(toe_marker_y)/(1.0/fs)

    to_index = []
    to_value = []
    for m in range(len(near_to_index)):
        for g in range(near_to_index[m], len(toe_marker_y_vel)):
            if toe_marker_y_vel[g] > 0.2:
                to_index.append(g)
                to_value.append(temp_to_value[m])
                break

    to_index = np.array(to_index)
    to_value = np.array(to_value)

    return to_index, to_value

def vu_correction(near_to_index, temp_to_value, toe_marker_y, fs = 100):
    ''' Vu correction when using metatarsal instead of toe markers
    '''
    alpha = 1e2

    near_to_index = 1*near_to_index[:-1]
    toe_marker_y_vel = np.diff(toe_marker_y)/(1.0/fs)
    temp_to_index, _ = find_peaks(toe_marker_y_vel, height = 0)

    to_index = []
    to_value = []
    for i in range(len(near_to_index)):
        id = np.where(temp_to_index > near_to_index[i])[0][0]
        if (temp_to_index[id] - near_to_index[i]) < 0.2*fs:
            slope = (toe_marker_y_vel[temp_to_index[id]] - toe_marker_y_vel[near_to_index[i]])/(temp_to_index[id] - near_to_index[i])
            to_index.append(near_to_index[i] + int(alpha*slope))
        else:
            to_index.append(near_to_index[i])
        
        to_value.append(temp_to_value[i])

    to_index = np.array(to_index)
    to_value = np.array(to_value)

    return to_index, to_value

# Method using the height of heel markers and distance between toe/metatarsal markers to the sacrum
def ge_mix(marker_traj, fs = 100, vis = False, task = 'walking'):
    ''' Obtain gait events from the height of heel markers and distance between toe/metatarsal markers to the sacrum
    '''
    min_peak_distance_hc = fs*0.5
    min_peak_distance_to = fs*0.5
    gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    heel_marker_y                = marker_traj['heel_marker_y']
    temp_hc_index, temp_hc_value = find_peaks(-1*heel_marker_y, height = [-1, 0], distance = min_peak_distance_hc)
    # hc_index                     = 1*temp_hc_index
    # hc_value                     = -1*temp_hc_value['peak_heights']

    for i in range(1, len(temp_hc_index)):
        prev_vec = np.array([marker_traj['sacrum_marker1_x'][temp_hc_index[i - 1]] - marker_traj['sacrum_marker2_x'][temp_hc_index[i - 1]], marker_traj['sacrum_marker1_z'][temp_hc_index[i - 1]] - marker_traj['sacrum_marker2_z'][temp_hc_index[i - 1]]])
        curr_vec = np.array([marker_traj['sacrum_marker1_x'][temp_hc_index[i]] - marker_traj['sacrum_marker2_x'][temp_hc_index[i]], marker_traj['sacrum_marker1_z'][temp_hc_index[i]] - marker_traj['sacrum_marker2_z'][temp_hc_index[i]]])
        angle    = angle_between_vectors(prev_vec, curr_vec)
        if angle < 90:
            gait_events['hc_index'].append(temp_hc_index[i])

    toe_marker_z                 = marker_traj['toe_marker_z']
    sacrum_marker_z              = marker_traj['sacrum_marker_z']
    if task == 'treadmill_walking':
        toe_distance_z               = sacrum_marker_z - toe_marker_z
        temp_to_index, temp_to_value = find_peaks(toe_distance_z, height = [0, 1], distance = min_peak_distance_to)
    elif task == 'walking':
        toe_distance_z               = abs(sacrum_marker_z - toe_marker_z) # modification for overground walking
        temp_to_index, temp_to_value = find_peaks(toe_distance_z, height = [0.05, 0.2], distance = min_peak_distance_to)
    # to_index                     = 1*temp_to_index
    # to_value                     = 1*temp_to_value['peak_heights']

    for i in range(1, len(temp_to_index)):
        prev_vec = np.array([marker_traj['sacrum_marker1_x'][temp_to_index[i - 1]] - marker_traj['sacrum_marker2_x'][temp_to_index[i - 1]], marker_traj['sacrum_marker1_z'][temp_to_index[i - 1]] - marker_traj['sacrum_marker2_z'][temp_to_index[i - 1]]])
        curr_vec = np.array([marker_traj['sacrum_marker1_x'][temp_to_index[i]] - marker_traj['sacrum_marker2_x'][temp_to_index[i]], marker_traj['sacrum_marker1_z'][temp_to_index[i]] - marker_traj['sacrum_marker2_z'][temp_to_index[i]]])
        angle    = angle_between_vectors(prev_vec, curr_vec)
        if angle < 90:
            gait_events['to_index'].append(temp_to_index[i])

    # gait_events['hc_index'] = hc_index
    # gait_events['hc_value'] = hc_value
    # gait_events['to_index'] = to_index
    # gait_events['to_value'] = to_value
    gait_events['hc_index'] = np.array(gait_events['hc_index'])
    gait_events['hc_value'] = np.array(gait_events['hc_value'])
    gait_events['to_index'] = np.array(gait_events['to_index'])
    gait_events['to_value'] = np.array(gait_events['to_value'])

    if vis:
        visualizer.plot_gait_events_mocap(heel_marker_y, toe_distance_z, gait_events)

    return gait_events

# Method using the distance from heel and toe/metatarsal markers to the sacrum
def ge_heel_toe_sacrum(marker_traj, fs = 100, vis = False):
    ''' Obtain gait events from the distance between heel and toe/metatarsal markers to the sacrum
    '''
    min_peak_distance_hc = fs*0.5
    min_peak_distance_to = fs*0.5
    gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    heel_marker_z = marker_traj['heel_marker_z']
    toe_marker_z  = marker_traj['toe_marker_z']
    sacrum_marker_z = marker_traj['sacrum_marker_z']

    heel_distance_z = heel_marker_z - sacrum_marker_z
    temp_hc_index, temp_hc_value = find_peaks(heel_distance_z, height = [0, 1], distance = min_peak_distance_hc)
    hc_index                     = 1*temp_hc_index
    hc_value                     = 1*temp_hc_value['peak_heights']

    toe_distance_z = sacrum_marker_z - toe_marker_z
    temp_to_index, temp_to_value = find_peaks(toe_distance_z, height = [0, 1], distance = min_peak_distance_to)
    to_index                     = 1*temp_to_index
    to_value                     = 1*temp_to_value['peak_heights']

    gait_events['hc_index'] = hc_index
    gait_events['hc_value'] = hc_value
    gait_events['to_index'] = to_index
    gait_events['to_value'] = to_value

    if vis:
        visualizer.plot_gait_events_mocap(heel_distance_z, toe_distance_z, gait_events)

    return gait_events

# Method using foot velocity in the vertical direction
# Peak enhancement before detection
def foot_vel_peak_enhancement(foot_center_y_vel, vis = False):
    ''' Enhance toe-off peaks for detection
    '''
    INCREASE   = .05
    gain_arr   = []
    gain       = 1
    direction  = 1
    num_sample = len(foot_center_y_vel)

    foot_center_y_vel_enhanced = []
    for i in range(num_sample - 1):
        curr_vel = foot_center_y_vel[i]
        next_vel = foot_center_y_vel[i + 1]

        if curr_vel >= 0:
            gain += INCREASE*direction
            if next_vel - curr_vel >= 0:
                direction = 1
            else:
                direction = -1
        else:
            gain = 1.0

        foot_center_y_vel_enhanced.append(curr_vel*gain)
        gain_arr.append(gain)

    foot_center_y_vel_enhanced = np.array(foot_center_y_vel_enhanced)

    # if vis:
    #     visualizer.plot_foot_vel_enhancement(foot_center_y_vel_enhanced, foot_center_y_vel, gain_arr)

    return foot_center_y_vel_enhanced

def ge_foot_vel(marker_traj, fs = 100, vis = False):
    ''' Obtain gait events from foot velocity in the vertical direction
    '''
    min_peak_distance_hc = fs*0.1
    min_peak_distance_to = fs*0.5
    gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    heel_marker_y       = marker_traj['heel_marker_y']
    toe_marker_y        = marker_traj['toe_marker_y']
    foot_center_y       = (heel_marker_y + toe_marker_y)/2
    foot_center_y_vel_r = np.diff(foot_center_y)/(1.0/fs)
    foot_center_y_vel   = common.filter_signal(foot_center_y_vel_r, 7)
    foot_center_y_vel_  = foot_vel_peak_enhancement(foot_center_y_vel, vis)

    temp_hc_index, temp_hc_value = find_peaks(-1*foot_center_y_vel_, height = [0.1, 1], distance = min_peak_distance_hc)
    hc_index                     = 1*temp_hc_index
    hc_value                     = -1*temp_hc_value['peak_heights']
    # hc_index, hc_value           = remove_noisy_peaks_mocap(hc_index, hc_value, 'walking')

    temp_to_index, temp_to_value = find_peaks(foot_center_y_vel_, height = 0.1, distance = min_peak_distance_to)
    to_index                     = 1*temp_to_index
    to_value                     = 1*temp_to_value['peak_heights']

    for id in to_index:
        try:
            temp_id = np.where(hc_index < id)[0][-1]
            gait_events['hc_index'].append(hc_index[temp_id])
            gait_events['hc_value'].append(hc_value[temp_id])
        except:
            print('...mid swing with no stance following detected...')

    gait_events['hc_index'] = np.array(gait_events['hc_index'])
    gait_events['hc_value'] = np.array(gait_events['hc_value'])
    gait_events['to_index'] = to_index
    gait_events['to_value'] = to_value

    if vis:
        visualizer.plot_gait_events_mocap(foot_center_y_vel_, foot_center_y_vel, gait_events)

    return gait_events

# Method using heel and toe velocity
# TODO: Need validation
def ge_heel_toe_vel(marker_traj, fs = 100, vis = False):
    gait_events = {'hc_index': [], 'hc_value': [], 'to_index': [], 'to_value': []}

    threshold = 0.0
    window    = 20

    heel_marker_z     = marker_traj['heel_marker_z']
    heel_marker_z_vel = np.diff(heel_marker_z)/(1.0/fs)

    toe_marker_z      = marker_traj['toe_marker_z']
    toe_marker_z_vel  = np.diff(toe_marker_z)/(1.0/fs)

    for i in range(len(heel_marker_z_vel) - window):
        if (toe_marker_z_vel[i] < threshold) and (toe_marker_z_vel[i + 1:i + window] > threshold).all():
            gait_events['to_index'].append(i + 1 + 1)
            gait_events['to_value'].append(0)

        if (heel_marker_z_vel[i:i + window] > threshold).all() and (heel_marker_z_vel[i + window] < threshold):
            gait_events['hc_index'].append(i + window + 1)
            gait_events['hc_value'].append(0)

    gait_events['hc_index'] = np.array(gait_events['hc_index'])
    gait_events['hc_value'] = np.array(gait_events['hc_value'])
    gait_events['to_index'] = np.array(gait_events['to_index'])
    gait_events['to_value'] = np.array(gait_events['to_value'])


    if vis:
        visualizer.plot_gait_events_mocap(heel_marker_z_vel, toe_marker_z_vel, gait_events)

    return gait_events


def get_gait_event_mocap(marker_traj, task, ge_method, correction = None, fs = 100, vis = False):
    ''' Obtain heel contact and toe-off events

    Args:
        + marker_traj (dict of np.array): necessary markers for gait event identification
        + task (str): 'walking' or 'treadmill_walking'
        + ge_method (str): method for gait detection
        + correction (str): method for correction, None if no correction applied
        + fs (int): sampling rate
        + vis (boolean): set True to visualize peak detection

    Returns:
        + gait_events (dict of np.array): index and value arrays of heel strike and toe-offs
    '''
    if ge_method == constants_mocap.GE_METHOD_HEEL_TOE_HEIGHT:
        gait_events = ge_heel_toe_height(marker_traj, correction = None, fs = fs, vis = vis)
    elif ge_method == constants_mocap.GE_METHOD_MIX:
        gait_events = ge_mix(marker_traj, fs = fs, vis = vis, task = task)
    elif ge_method == constants_mocap.GE_METHOD_HEEL_TOE_SACRUM:
        gait_events = ge_heel_toe_sacrum(marker_traj, fs = fs, vis = vis)
    elif ge_method == constants_mocap.GE_METHOD_FOOT_VEL:
        gait_events = ge_foot_vel(marker_traj, fs = fs, vis = vis)
    elif ge_method == constants_mocap.GE_METHOD_HEEL_TOE_VEL:
        gait_events = ge_heel_toe_vel(marker_traj, fs = fs, vis = vis)
    elif ge_method == constants_mocap.GE_METHOD_HEEL_TOE_HEIGHT_C:
        gait_events = ge_heel_toe_height(marker_traj, correction = correction, fs = fs, vis = vis)

    return gait_events


# --- Method section (for our official analysis) --- #
# Use the height of heel and toe markers if the toe markers are available
# Otherwise, use the mix method
def select_ge_method(marker_list):
    ''' Select the method for gait event identification
    '''
    toe_available = False
    for marker in marker_list:
        if 'TOE' in marker:
            toe_available = True
            break

    if toe_available:
        ge_method = constants_mocap.GE_METHOD_HEEL_TOE_HEIGHT
    else:
        ge_method = constants_mocap.GE_METHOD_MIX

    return ge_method


# Get marker trajectory based on the selected ge method
def get_marker_traj(s_mocap_data, ge_method, id_target_leg, id_adjacent_leg):
    ''' Get marker trajectory for gait event detection 

    Args:
        + s_mocap_data (pd.DataFrame): synchronized mocap data
        + ge_method (int): selected method for gait event detection
        + id_target_leg (str): target leg
        + id_adjacent_leg (str): adjacent leg

    Returns:
        + marker_traj_target (dict of np.array): marker trajectory for gait event detection of the target leg
        + marker_traj_adjacent (dict of np.array): marker trajectory for gait event detection of the adjacent leg
    '''
    heel_y_target   = s_mocap_data[id_target_leg.upper() + 'CAL Y'].to_numpy()
    heel_y_adjacent = s_mocap_data[id_adjacent_leg.upper() + 'CAL Y'].to_numpy()

    sacrum_x_target = s_mocap_data[id_target_leg.upper() + 'PS2 X'].to_numpy()
    sacrum_z_target = s_mocap_data[id_target_leg.upper() + 'PS2 Z'].to_numpy()

    sacrum_x_adjacent = s_mocap_data[id_adjacent_leg.upper() + 'PS2 X'].to_numpy()
    sacrum_z_adjacent = s_mocap_data[id_adjacent_leg.upper() + 'PS2 Z'].to_numpy()

    if ge_method == constants_mocap.GE_METHOD_HEEL_TOE_HEIGHT:
        toe_y_target         = s_mocap_data[id_target_leg.upper() + 'TOE Y'].to_numpy()
        toe_y_adjacent       = s_mocap_data[id_adjacent_leg.upper() + 'TOE Y'].to_numpy()
        marker_traj_target   = {'heel_marker_y': heel_y_target,
                                'toe_marker_y': toe_y_target,
                                'sacrum_marker1_x': sacrum_x_target,
                                'sacrum_marker1_z': sacrum_z_target,
                                'sacrum_marker2_x': sacrum_x_adjacent,
                                'sacrum_marker2_z': sacrum_z_adjacent}
        marker_traj_adjacent = {'heel_marker_y': heel_y_adjacent,
                                'toe_marker_y': toe_y_adjacent,
                                'sacrum_marker1_x': sacrum_x_target,
                                'sacrum_marker1_z': sacrum_z_target,
                                'sacrum_marker2_x': sacrum_x_adjacent,
                                'sacrum_marker2_z': sacrum_z_adjacent}

    elif ge_method == constants_mocap.GE_METHOD_MIX:
        toe_z_target         = s_mocap_data[id_target_leg.upper() + 'MT2 Z'].to_numpy()
        toe_x_target         = s_mocap_data[id_target_leg.upper() + 'MT2 X'].to_numpy()
        toe_z_adjacent       = s_mocap_data[id_adjacent_leg.upper() + 'MT2 Z'].to_numpy()
        toe_x_adjacent       = s_mocap_data[id_adjacent_leg.upper() + 'MT2 X'].to_numpy()
        sacrum_z_target      = s_mocap_data[id_target_leg.upper() + 'PS2 Z'].to_numpy()
        sacrum_z_adjacent    = s_mocap_data[id_adjacent_leg.upper() + 'PS2 Z'].to_numpy()
        sacrum_z             = (sacrum_z_target + sacrum_z_adjacent)/2
        marker_traj_target   = {'heel_marker_y': heel_y_target,
                                'toe_marker_z': toe_z_target,
                                'sacrum_marker_z': sacrum_z,
                                'sacrum_marker1_x': sacrum_x_target,
                                'sacrum_marker1_z': sacrum_z_target,
                                'sacrum_marker2_x': sacrum_x_adjacent,
                                'sacrum_marker2_z': sacrum_z_adjacent}
        marker_traj_adjacent = {'heel_marker_y': heel_y_adjacent,
                                'toe_marker_z': toe_z_adjacent,
                                'sacrum_marker_z': sacrum_z,
                                'sacrum_marker1_x': sacrum_x_target,
                                'sacrum_marker1_z': sacrum_z_target,
                                'sacrum_marker2_x': sacrum_x_adjacent,
                                'sacrum_marker2_z': sacrum_z_adjacent}

    return marker_traj_target, marker_traj_adjacent




