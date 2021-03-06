# -*- coding: UTF-8 -*-
'''
structure property.py
Script to compute the structure property of the whole system.
Use conditions: [1] Cuboid sample
                [2] Aperiodic boundary
                [3] Monosize sample
Usage: python structure-property.py -scenario 1000
'''
# Reference:
# [1] Qi Wang* & Anubhav Jain*. A transferable machine learning framework linking interstice distribution and plastic heterogeneity in metallic glasses.
# [2] E.D.Cubuk* R.J.S.Ivancic* S.S.Schoenholz*.Structure-property relationships from universal signatures of plasticity in disordered solids.
# [3] E. D. Cubuk,1,∗ S. S. Schoenholz (Equal contribution),2,† J. M. Rieser. Identifying structural ﬂow defects in disordered solids using machine learning methods.
from __future__ import division
import re
import math
import os
import pyvoro
import boo
import requests
import openpyxl
import pandas as pd
import numpy as np
from numba import jit
from sys import argv, exit
from scipy.spatial import KDTree, ConvexHull


def mkdir(path_write):
    # 判断目录是否存在
    # 存在：True
    # 不存在：False
    folder = os.path.exists(path_write)
    # 判断结果
    if not folder:
        # 如果不存在，则创建新目录
        os.makedirs(path_write)
        print('-----创建成功-----')
    else:
        # 如果目录已存在，则不创建，提示目录已存在
        print('目录已存在')


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@jit(nopython=True)
def compute_cos_ijk(posi, posj, posk):
    # 计算向量ij与ik的夹角的cos值
    eij = np.array([posj[0] - posi[0], posj[1] - posi[1], posj[2] - posi[2]])
    eik = np.array([posk[0] - posi[0], posk[1] - posi[1], posk[2] - posi[2]])
    cos = np.dot(eij, eik) / (np.linalg.norm(eij) * np.linalg.norm(eik))
    return cos


@jit(nopython=True)
def compute_dis(posj, posk):
    # 计算三维空间中两点的距离
    ejk = np.array([posk[0] - posj[0], posk[1] - posj[1], posk[2] - posj[2]])
    dis = np.linalg.norm(ejk)
    return dis


@jit(nopython=True)
def compute_tetrahedron_volume(vertice1, vertice2, vertice3, vertice4):
    # 计算四面体的体积，通过给定四面体的四个顶点
    eij = np.array([vertice2[0] - vertice1[0], vertice2[1] - vertice1[1], vertice2[2] - vertice1[2]])
    eik = np.array([vertice3[0] - vertice1[0], vertice3[1] - vertice1[1], vertice3[2] - vertice1[2]])
    eil = np.array([vertice4[0] - vertice1[0], vertice4[1] - vertice1[1], vertice4[2] - vertice1[2]])
    return abs(np.dot(eil, np.cross(eij, eik))) / 6


@jit(nopython=True)
def compute_solide_angle(vertice1, vertice2, vertice3, vertice4):
    # 计算固体角
    eij = np.array([vertice2[0] - vertice1[0], vertice2[1] - vertice1[1], vertice2[2] - vertice1[2]])
    eik = np.array([vertice3[0] - vertice1[0], vertice3[1] - vertice1[1], vertice3[2] - vertice1[2]])
    eil = np.array([vertice4[0] - vertice1[0], vertice4[1] - vertice1[1], vertice4[2] - vertice1[2]])
    len_eij = np.linalg.norm(eij)
    len_eik = np.linalg.norm(eik)
    len_eil = np.linalg.norm(eil)
    return 2 * math.atan2(abs(np.dot(eij, np.cross(eik, eil))),
                          (len_eij * len_eik * len_eil + np.dot(eij, eik) * len_eil
                           + np.dot(eij, eil) * len_eik + np.dot(eik, eil) * len_eij))


@jit(nopython=True)
def compute_simplice_area(vertice1, vertice2, vertice3):
    # 计算三角形的面积，通过给定的三个顶点
    # problem1: compute error -> eij = eik causes error.
    # neglect
    eij = np.array([vertice2[0] - vertice1[0], vertice2[1] - vertice1[1], vertice2[2] - vertice1[2]])
    eik = np.array([vertice3[0] - vertice1[0], vertice3[1] - vertice1[1], vertice3[2] - vertice1[2]])
    h = (np.dot(eij, eij) - (np.dot(eij, eik) / (np.linalg.norm(eik))) ** 2) ** 0.5
    return (np.linalg.norm(eik)) * h / 2


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@jit(nopython=True)
def compute_angular_element(neigh_id_input, distance_input, points_input, a_list, b_list, c_list, radius, like_input,
                            neigh_id_length_index_input):
    angular_value_in = np.empty_like(like_input)
    for a in range(len(neigh_id_length_index_input)):
        value1 = 0.0
        value2 = 0.0
        value3 = 0.0
        value4 = 0.0
        value5 = 0.0
        value6 = 0.0
        value7 = 0.0
        value8 = 0.0
        value9 = 0.0
        value10 = 0.0
        value11 = 0.0
        value12 = 0.0
        value13 = 0.0
        value14 = 0.0
        value15 = 0.0
        value16 = 0.0
        value17 = 0.0
        value18 = 0.0
        value19 = 0.0
        value20 = 0.0
        value21 = 0.0
        value22 = 0.0
        for b in range(neigh_id_length_index_input[a]):
            for k_ in range(neigh_id_length_index_input[a] - b - 1):
                k = k_ + b + 1
                rij = distance_input[a][b]
                rik = distance_input[a][k]
                posi = points_input[a]
                posj = points_input[neigh_id_input[a][b]]
                posk = points_input[neigh_id_input[a][k]]
                rjk = compute_dis(posj, posk)
                cos_ijk = compute_cos_ijk(posi, posj, posk)
                r_2 = rij ** 2 + rik ** 2 + rjk ** 2
                value1 += math.exp(-(r_2 / (radius * a_list[0]) ** 2)) * (1 + b_list[0] * cos_ijk) ** c_list[0]
                value2 += math.exp(-(r_2 / (radius * a_list[1]) ** 2)) * (1 + b_list[1] * cos_ijk) ** c_list[1]
                value3 += math.exp(-(r_2 / (radius * a_list[2]) ** 2)) * (1 + b_list[2] * cos_ijk) ** c_list[2]
                value4 += math.exp(-(r_2 / (radius * a_list[3]) ** 2)) * (1 + b_list[3] * cos_ijk) ** c_list[3]
                value5 += math.exp(-(r_2 / (radius * a_list[4]) ** 2)) * (1 + b_list[4] * cos_ijk) ** c_list[4]
                value6 += math.exp(-(r_2 / (radius * a_list[5]) ** 2)) * (1 + b_list[5] * cos_ijk) ** c_list[5]
                value7 += math.exp(-(r_2 / (radius * a_list[6]) ** 2)) * (1 + b_list[6] * cos_ijk) ** c_list[6]
                value8 += math.exp(-(r_2 / (radius * a_list[7]) ** 2)) * (1 + b_list[7] * cos_ijk) ** c_list[7]
                value9 += math.exp(-(r_2 / (radius * a_list[8]) ** 2)) * (1 + b_list[8] * cos_ijk) ** c_list[8]
                value10 += math.exp(-(r_2 / (radius * a_list[9]) ** 2)) * (1 + b_list[9] * cos_ijk) ** c_list[9]
                value11 += math.exp(-(r_2 / (radius * a_list[10]) ** 2)) * (1 + b_list[10] * cos_ijk) ** c_list[10]
                value12 += math.exp(-(r_2 / (radius * a_list[11]) ** 2)) * (1 + b_list[11] * cos_ijk) ** c_list[11]
                value13 += math.exp(-(r_2 / (radius * a_list[12]) ** 2)) * (1 + b_list[12] * cos_ijk) ** c_list[12]
                value14 += math.exp(-(r_2 / (radius * a_list[13]) ** 2)) * (1 + b_list[13] * cos_ijk) ** c_list[13]
                value15 += math.exp(-(r_2 / (radius * a_list[14]) ** 2)) * (1 + b_list[14] * cos_ijk) ** c_list[14]
                value16 += math.exp(-(r_2 / (radius * a_list[15]) ** 2)) * (1 + b_list[15] * cos_ijk) ** c_list[15]
                value17 += math.exp(-(r_2 / (radius * a_list[16]) ** 2)) * (1 + b_list[16] * cos_ijk) ** c_list[16]
                value18 += math.exp(-(r_2 / (radius * a_list[17]) ** 2)) * (1 + b_list[17] * cos_ijk) ** c_list[17]
                value19 += math.exp(-(r_2 / (radius * a_list[18]) ** 2)) * (1 + b_list[18] * cos_ijk) ** c_list[18]
                value20 += math.exp(-(r_2 / (radius * a_list[19]) ** 2)) * (1 + b_list[19] * cos_ijk) ** c_list[19]
                value21 += math.exp(-(r_2 / (radius * a_list[20]) ** 2)) * (1 + b_list[20] * cos_ijk) ** c_list[20]
                value22 += math.exp(-(r_2 / (radius * a_list[21]) ** 2)) * (1 + b_list[21] * cos_ijk) ** c_list[21]
        angular_value_in[0][a] = value1
        angular_value_in[1][a] = value2
        angular_value_in[2][a] = value3
        angular_value_in[3][a] = value4
        angular_value_in[4][a] = value5
        angular_value_in[5][a] = value6
        angular_value_in[6][a] = value7
        angular_value_in[7][a] = value8
        angular_value_in[8][a] = value9
        angular_value_in[9][a] = value10
        angular_value_in[10][a] = value11
        angular_value_in[11][a] = value12
        angular_value_in[12][a] = value13
        angular_value_in[13][a] = value14
        angular_value_in[14][a] = value15
        angular_value_in[15][a] = value16
        angular_value_in[16][a] = value17
        angular_value_in[17][a] = value18
        angular_value_in[18][a] = value19
        angular_value_in[19][a] = value20
        angular_value_in[20][a] = value21
        angular_value_in[21][a] = value22
    return angular_value_in


@jit(nopython=True)
def compute_radial_value(delta_radius_input, distance_length_index_input, distance_input,
                         like_input, delta_r_input):
    radial_value_in = np.empty_like(like_input)
    for a in range(len(delta_radius_input)):
        delta_radius_now = delta_radius_input[a]
        for b in range(len(distance_input)):
            value = 0.0
            for c in range(distance_length_index_input[b]):
                value += math.exp(-0.5 * ((distance_input[b][c] - delta_radius_now) / delta_r_input) ** 2)
            radial_value_in[a][b] = value
    return radial_value_in


def compute_symmetry_functions(points, radius):
    # Compute symmetry function values of the whole granular system.
    # Reference: [1] Structure-property relationships from universal signatures of plasticity in disordered solids.
    #            [2] Identifying structural ﬂow defects in disordered solids using machine learning methods.
    # step1. set the constant
    particle_number = len(points)
    radius_for_input = radius[0]
    a_list_for_input = np.array([14.638, 14.638, 14.638, 14.638, 2.554, 2.554, 2.554, 2.554, 1.648, 1.648, 1.204, 1.204,
                                 1.204, 1.204, 0.933, 0.933, 0.933, 0.933, 0.695, 0.695, 0.695, 0.695])
    b_list_for_input = np.array([-1, 1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    c_list_for_input = np.array([1, 1, 2, 2, 1, 1, 2, 2, 1, 2, 1, 2, 4, 16, 1, 2, 4, 16, 1, 2, 4, 16])
    like_for_angular = np.empty(shape=[22, particle_number])
    like_for_radial = np.empty(shape=[50, particle_number])
    single_radius = radius[0]
    delta_r = 0.1 * single_radius
    delta_radius = np.array([np.linspace(0.1, 5.0, 50)[i] * single_radius for i in range(50)])
    # step2. compute neighbour information by KDTree
    # 2.1 kd tree
    max_distance = 5.0 * radius[0]
    kd_tree = KDTree(points)
    pairs = list(kd_tree.query_pairs(max_distance))
    # 2.2 distance for every pairs
    dis_use = []
    for x in range(len(pairs)):
        dis = ((points[pairs[x][0]][0] - points[pairs[x][1]][0]) ** 2
               + (points[pairs[x][0]][1] - points[pairs[x][1]][1]) ** 2
               + (points[pairs[x][0]][2] - points[pairs[x][1]][2]) ** 2) ** 0.5
        if dis <= max_distance:
            dis_use.append(dis)
    # 2.3 bonds of every particle
    bonds = []
    for x in range(particle_number):
        bonds.append([])
    for x in range(len(pairs)):
        bonds[pairs[x][0]].append(pairs[x][1])
        bonds[pairs[x][1]].append(pairs[x][0])
    # step3. modify neighbour information for next compute
    # 3.1 number of neighbours of every particle
    neigh_id_length_index = []
    for i in range(len(bonds)):
        neigh_id_length_index.append(len(bonds[i]))
    # 3.2 neighbour id array
    neigh_id = np.zeros(shape=[particle_number, max(neigh_id_length_index)], dtype=int)
    for i in range(len(bonds)):
        for j in range(len(bonds[i])):
            neigh_id[i][j] = bonds[i][j]
    neigh_id_length_index_array = np.array(neigh_id_length_index)
    # 3.3 neighbour distance information
    distance = []
    for x in range(particle_number):
        distance.append([])
    for x in range(len(dis_use)):
        distance[pairs[x][0]].append(dis_use[x])
        distance[pairs[x][1]].append(dis_use[x])
    distance_length_index = []
    for i in range(len(distance)):
        distance_length_index.append(len(distance[i]))
    distance_array = np.zeros(shape=[particle_number, max(distance_length_index)])
    for i in range(len(distance)):
        for j in range(len(distance[i])):
            distance_array[i][j] = distance[i][j]
    distance_length_index_array = np.array(distance_length_index)
    # step4. compute
    # 4.1 angular value
    angular_value = compute_angular_element(neigh_id, distance_array, points, a_list_for_input, b_list_for_input,
                                            c_list_for_input, radius_for_input, like_for_angular,
                                            neigh_id_length_index_array).T
    # 4.2 radial value
    radial_value = compute_radial_value(delta_radius, distance_length_index_array, distance_array, like_for_radial,
                                        delta_r).T
    # 4.3 stack
    symmetry_function_value = np.hstack((angular_value, radial_value))
    return symmetry_function_value


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def compute_interstice_distance(voronoi_neighbour_use_input, distance_input, radius_input):
    interstice_distance_in = []
    for a in range(len(voronoi_neighbour_use_input)):
        interstice_distance_now = []
        for b in range(len(voronoi_neighbour_use_input[a])):
            interstice = (distance_input[a][b] - (radius_input[voronoi_neighbour_use_input[a][b]] + radius_input[a])) / \
                         distance_input[a][b]
            interstice_distance_now.append(interstice)
        interstice_distance_in.append([np.min(interstice_distance_now),
                                       np.max(interstice_distance_now),
                                       np.mean(interstice_distance_now),
                                       np.std(interstice_distance_now)])
    return np.array(interstice_distance_in)


'''
def compute_interstice_area_polysize(voronoi_neighbour_use_input, points_input, radius_input):
    interstice_area_in = []
    for a in range(len(voronoi_neighbour_use_input)):
        if len(voronoi_neighbour_use_input[a]) >= 4:
            points_now = []
            radius_now = []
            for b in range(len(voronoi_neighbour_use_input[a])):
                points_now.append(points_input[voronoi_neighbour_use_input[a][b]])
                radius_now.append(radius_input[voronoi_neighbour_use_input[a][b]])
            ch = ConvexHull(points_now)
            simplice = np.array(ch.simplices)
            interstice_area_mid = np.zeros(shape=[len(simplice), ])
            interstice_area_x = compute_interstice_area_polysize_single_particle(simplice,
                                                                                 np.array(points_now),
                                                                                 np.array(radius_now),
                                                                                 interstice_area_mid)
            interstice_area_in.append([np.min(interstice_area_x),
                                       np.max(interstice_area_x),
                                       np.mean(interstice_area_x),
                                       np.std(interstice_area_x, ddof=1)])
        else:
            interstice_area_in.append([0.0, 0.0, 0.0, 0.0])
    return interstice_area_in


@jit(nopython=True)
def compute_interstice_area_polysize_single_particle(simplice, points_now, radius_now, interstice_area_mid):
    interstice_area_x = interstice_area_mid
    for a in range(len(simplice)):
        area_triangle = compute_simplice_area(points_now[simplice[a][0]],
                                              points_now[simplice[a][1]], points_now[simplice[a][2]])
        area_pack = (math.acos(compute_cos_ijk(points_now[simplice[a][0]],
                                               points_now[simplice[a][1]], points_now[simplice[a][2]]))
                     * radius_now[simplice[a][0]] ** 2 +
                     math.acos(compute_cos_ijk(points_now[simplice[a][2]],
                                               points_now[simplice[a][0]], points_now[simplice[a][1]]))
                     * radius_now[simplice[a][2]] ** 2 +
                     math.acos(compute_cos_ijk(points_now[simplice[a][1]],
                                               points_now[simplice[a][2]], points_now[simplice[a][0]]))
                     * radius_now[simplice[a][1]] ** 2) / 2
        interstice_area_x[a] = (area_triangle - area_pack) / area_triangle
    return interstice_area_x
'''


def compute_interstice_area_monosize(voronoi_neighbour_use_input, points_input, radius_input):
    interstice_area_in = []
    for a in range(len(voronoi_neighbour_use_input)):
        if len(voronoi_neighbour_use_input[a]) >= 4:
            points_now = []
            for b in range(len(voronoi_neighbour_use_input[a])):
                points_now.append(points_input[voronoi_neighbour_use_input[a][b]])
            ch = ConvexHull(points_now)
            simplice = np.array(ch.simplices)
            interstice_area_mid = np.zeros(shape=[len(simplice), ])
            interstice_area_x = compute_interstice_area_monosize_single_particle(simplice,
                                                                                 np.array(points_now),
                                                                                 radius_input,
                                                                                 interstice_area_mid)
            interstice_area_in.append([np.min(interstice_area_x),
                                       np.max(interstice_area_x),
                                       np.mean(interstice_area_x),
                                       np.std(interstice_area_x, ddof=1)])
        else:
            interstice_area_in.append([0.0, 0.0, 0.0, 0.0])
    return np.array(interstice_area_in)


@jit(nopython=True)
def compute_interstice_area_monosize_single_particle(simplice, points_now, radius_input, interstice_area_mid):
    interstice_area_x = interstice_area_mid
    for a in range(len(simplice)):
        area_triangle = compute_simplice_area(points_now[simplice[a][0]],
                                              points_now[simplice[a][1]], points_now[simplice[a][2]])
        area_pack = (math.pi * radius_input ** 2) / 4
        interstice_area_x[a] = (area_triangle - area_pack) / area_triangle
    return interstice_area_x


def compute_interstice_volume(voronoi_neighbour_use_input, points_input, radius_input):
    interstice_volume_in = []
    for a in range(len(voronoi_neighbour_use_input)):
        if len(voronoi_neighbour_use_input[a]) >= 4:
            points_now = []
            radius_now = []
            origin_particle = points_input[a]
            origin_radius = radius_input[a]
            for b in range(len(voronoi_neighbour_use_input[a])):
                points_now.append(points_input[voronoi_neighbour_use_input[a][b]])
                radius_now.append(radius_input[voronoi_neighbour_use_input[a][b]])
            ch = ConvexHull(points_now)
            simplice = np.array(ch.simplices)
            interstice_volume_mid = np.zeros(shape=[len(simplice), ])
            interstice_volume_x = compute_interstice_volume_single_particle(simplice,
                                                                            np.array(points_now),
                                                                            np.array(radius_now),
                                                                            interstice_volume_mid,
                                                                            origin_particle,
                                                                            origin_radius)

            interstice_volume_in.append([np.min(interstice_volume_x),
                                         np.max(interstice_volume_x),
                                         np.mean(interstice_volume_x),
                                         np.std(interstice_volume_x, ddof=1)])
        else:
            interstice_volume_in.append([0.0, 0.0, 0.0, 0.0])
    return np.array(interstice_volume_in)


@jit(nopython=True)
def compute_interstice_volume_single_particle(simplice, points_now, radius_now, interstice_volume_mid,
                                              origin_particle, origin_radius):
    interstice_volume_x = interstice_volume_mid
    for a in range(len(simplice)):
        volume_triangle = compute_tetrahedron_volume(points_now[simplice[a][0]],
                                                     points_now[simplice[a][1]], points_now[simplice[a][2]],
                                                     origin_particle)
        if volume_triangle == 0:
            # 处于边界上的颗粒计算时会触发错误，在此随机赋予一个值，因为边界上的颗粒不参与到以后的计算中
            interstice_volume_x[a] = 0
        else:
            volume_pack = (compute_solide_angle(origin_particle, points_now[simplice[a][0]], points_now[simplice[a][1]],
                                                points_now[simplice[a][2]])
                           * origin_radius ** 3 +
                           compute_solide_angle(points_now[simplice[a][2]], origin_particle,
                                                points_now[simplice[a][0]], points_now[simplice[a][1]])
                           * radius_now[simplice[a][2]] ** 3 +
                           compute_solide_angle(points_now[simplice[a][1]],
                                                points_now[simplice[a][2]], origin_particle, points_now[simplice[a][0]])
                           * radius_now[simplice[a][1]] ** 3 +
                           compute_solide_angle(points_now[simplice[a][0]], points_now[simplice[a][1]],
                                                points_now[simplice[a][2]], origin_particle) * radius_now[
                               simplice[a][0]] ** 3) \
                          / 3
            interstice_volume_x[a] = (volume_triangle - volume_pack) / volume_triangle
    return interstice_volume_x


@jit(nopython=True)
def interstice_distribution_MRO(interstice_distance, interstice_area, interstice_volume,
                                MRO_array, f_use_array, voronoi_neighbour, neigh_id_length_index):
    feature_MRO = np.empty_like(MRO_array)
    for aa in range(4):
        a = 5 * aa
        feature_now = interstice_distance[:, aa]
        for b in range(len(voronoi_neighbour)):
            f_use_not = np.zeros_like(f_use_array)
            for c in range(neigh_id_length_index[b]):
                f_use_not[c] = feature_now[voronoi_neighbour[b][c]]
            f_use = f_use_not[0: neigh_id_length_index[b]]
            feature_MRO[a][b] = feature_now[b]
            feature_MRO[a + 1][b] = np.min(f_use)
            feature_MRO[a + 2][b] = np.max(f_use)
            feature_MRO[a + 3][b] = np.mean(f_use)
            mean = np.mean(f_use)
            square = 0.0
            for c in range(len(f_use)):
                square += (f_use[c] - mean) ** 2
            sqrt = math.sqrt((square / len(f_use)))
            feature_MRO[a + 4][b] = sqrt
    for aa in range(4):
        a = 5 * aa + 20
        feature_now = interstice_area[:, aa]
        for b in range(len(voronoi_neighbour)):
            f_use_not = np.zeros_like(f_use_array)
            for c in range(neigh_id_length_index[b]):
                f_use_not[c] = feature_now[voronoi_neighbour[b][c]]
            f_use = f_use_not[0: neigh_id_length_index[b]]
            feature_MRO[a][b] = feature_now[b]
            feature_MRO[a + 1][b] = np.min(f_use)
            feature_MRO[a + 2][b] = np.max(f_use)
            feature_MRO[a + 3][b] = np.mean(f_use)
            mean = np.mean(f_use)
            square = 0.0
            for c in range(len(f_use)):
                square += (f_use[c] - mean) ** 2
            sqrt = math.sqrt((square / len(f_use)))
            feature_MRO[a + 4][b] = sqrt
    for aa in range(4):
        a = 5 * aa + 40
        feature_now = interstice_volume[:, aa]
        for b in range(len(voronoi_neighbour)):
            f_use_not = np.zeros_like(f_use_array)
            for c in range(neigh_id_length_index[b]):
                f_use_not[c] = feature_now[voronoi_neighbour[b][c]]
            f_use = f_use_not[0: neigh_id_length_index[b]]
            feature_MRO[a][b] = feature_now[b]
            feature_MRO[a + 1][b] = np.min(f_use)
            feature_MRO[a + 2][b] = np.max(f_use)
            feature_MRO[a + 3][b] = np.mean(f_use)
            mean = np.mean(f_use)
            square = 0.0
            for c in range(len(f_use)):
                square += (f_use[c] - mean) ** 2
            sqrt = math.sqrt((square / len(f_use)))
            feature_MRO[a + 4][b] = sqrt
    return feature_MRO.T


def compute_interstice_distribution(neighbour, points, radius):
    # compute interstice distribution of the whole granular system, include SRO(short range order), MRO(medium range order)
    # Reference: [1] Structure-property relationships from universal signatures of plasticity in disordered solids.
    # step1. set constant
    particle_number = len(neighbour)
    # step2. modify origin voronoi neighbour
    voronoi_neighbour = []
    for x in range(len(neighbour)):
        voronoi_neighbour_now = []
        for value in neighbour[x]:
            if value >= 0:
                voronoi_neighbour_now.append(value)
        voronoi_neighbour.append(voronoi_neighbour_now)
    bonds = []
    for x in range(len(voronoi_neighbour)):
        for y in range(len(voronoi_neighbour[x])):
            if voronoi_neighbour[x][y] > x:
                bonds.append([x, voronoi_neighbour[x][y]])
    bonds = np.array(bonds)
    voronoi_neighbour_use = []
    for x in range(particle_number):
        voronoi_neighbour_use.append([])
    for x in range(len(bonds)):
        voronoi_neighbour_use[bonds[x][0]].append(bonds[x][1])
        voronoi_neighbour_use[bonds[x][1]].append(bonds[x][0])
    neigh_id_length_index = []
    for x in range(len(voronoi_neighbour_use)):
        neigh_id_length_index.append(len(voronoi_neighbour_use[x]))
    neigh_id = np.zeros(shape=[particle_number, max(neigh_id_length_index)], dtype=int)
    for x in range(len(voronoi_neighbour_use)):
        for y in range(len(voronoi_neighbour_use[x])):
            neigh_id[x][y] = int(voronoi_neighbour_use[x][y])
    neigh_id_length_index = np.array(neigh_id_length_index)
    # step3. distance for every pairs
    dis_use = []
    for x in range(len(bonds)):
        dis = ((points[bonds[x][0]][0] - points[bonds[x][1]][0]) ** 2
               + (points[bonds[x][0]][1] - points[bonds[x][1]][1]) ** 2
               + (points[bonds[x][0]][2] - points[bonds[x][1]][2]) ** 2) ** 0.5
        dis_use.append(dis)
    # step4. neighbour distance of every particle
    distance = []
    for x in range(particle_number):
        distance.append([])
    for x in range(len(bonds)):
        distance[bonds[x][0]].append(dis_use[x])
        distance[bonds[x][1]].append(dis_use[x])
    # step5. compute
    # 5.1 compute interstice distance
    interstice_distance = compute_interstice_distance(voronoi_neighbour_use, distance, radius)
    # 5.2 compute interstice area
    interstice_area = compute_interstice_area_monosize(voronoi_neighbour_use, points, radius[0])
    # 5.3 compute interstice volume
    interstice_volume = compute_interstice_volume(voronoi_neighbour_use, points, radius)
    # 5.4 MRO, compute the medium range order feature of interstice_distance, interstice_area and interstice_volume
    MRO_array = np.empty(shape=[60, particle_number])
    f_use_array = np.empty(shape=[particle_number, ])
    MRO_interstice_distribution = interstice_distribution_MRO(interstice_distance, interstice_area, interstice_volume,
                                                              MRO_array, f_use_array, neigh_id, neigh_id_length_index)
    return MRO_interstice_distribution


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def compute_coordination_number_by_cutoff_distance(points_input, radius_input):
    maxdistance = 3.0 * radius_input[0]
    kdtree = KDTree(points_input)
    pairs = list(kdtree.query_pairs(maxdistance))
    cutoff_bonds = []
    for a in range(len(points_input)):
        cutoff_bonds.append([])
    for a in range(len(pairs)):
        cutoff_bonds[pairs[a][0]].append(pairs[a][1])
        cutoff_bonds[pairs[a][1]].append(pairs[a][0])
    coordination_number_by_cutoff_distance_in = np.zeros(shape=[len(points_input), ])
    for a in range(len(cutoff_bonds)):
        coordination_number_by_cutoff_distance_in[a] = len(cutoff_bonds[a])
    return coordination_number_by_cutoff_distance_in


def compute_cellfraction(voro_input, radius_input):
    volume = []
    for a in range(len(voro_input)):
        volume.append(voro_input[a]['volume'])
    ball_volume = (np.max(radius_input) ** 3) * 4 * math.pi / 3
    cellfraction_in = [ball_volume / volume[a] for a in range(len(voro_input))]
    return cellfraction_in


def compute_weight_i_fold_symm(voro_input, area_all_input):
    # Reference: [1] Structure-property relationships from universal signatures of plasticity in disordered solids.
    particle_number = len(voro_input)
    area_weight_i_fold_symm = {}
    area_weight_i_fold_symm3_in = np.zeros(shape=[particle_number, ])
    area_weight_i_fold_symm4_in = np.zeros(shape=[particle_number, ])
    area_weight_i_fold_symm5_in = np.zeros(shape=[particle_number, ])
    area_weight_i_fold_symm6_in = np.zeros(shape=[particle_number, ])
    area_weight_i_fold_symm7_in = np.zeros(shape=[particle_number, ])
    for a in range(len(voro_input)):
        faces_in = voro_input[a]['faces']
        vertices_id_length = []
        for b in range(len(faces_in)):
            vertices_id_length.append(len(faces_in[b]['vertices']))
        id3 = [c for c, b in enumerate(vertices_id_length) if b == 3]
        id4 = [c for c, b in enumerate(vertices_id_length) if b == 4]
        id5 = [c for c, b in enumerate(vertices_id_length) if b == 5]
        id6 = [c for c, b in enumerate(vertices_id_length) if b == 6]
        id7 = [c for c, b in enumerate(vertices_id_length) if b == 7]
        area3, area4, area5, area6, area7 = 0, 0, 0, 0, 0
        for b in range(len(id3)):
            area3 += area_all_input[a][id3[b]]
        for b in range(len(id4)):
            area4 += area_all_input[a][id4[b]]
        for b in range(len(id5)):
            area5 += area_all_input[a][id5[b]]
        for b in range(len(id6)):
            area6 += area_all_input[a][id6[b]]
        for b in range(len(id7)):
            area7 += area_all_input[a][id7[b]]
        area_total = area3 + area4 + area5 + area6 + area7
        area_weight_i_fold_symm3_in[a] = area3 / area_total
        area_weight_i_fold_symm4_in[a] = area4 / area_total
        area_weight_i_fold_symm5_in[a] = area5 / area_total
        area_weight_i_fold_symm6_in[a] = area6 / area_total
        area_weight_i_fold_symm7_in[a] = area7 / area_total
    area_weight_i_fold_symm['3'] = area_weight_i_fold_symm3_in
    area_weight_i_fold_symm['4'] = area_weight_i_fold_symm4_in
    area_weight_i_fold_symm['5'] = area_weight_i_fold_symm5_in
    area_weight_i_fold_symm['6'] = area_weight_i_fold_symm6_in
    area_weight_i_fold_symm['7'] = area_weight_i_fold_symm7_in
    return area_weight_i_fold_symm


def compute_voronoi_idx(voro_input):
    # Reference: [1] Structure-property relationships from universal signatures of plasticity in disordered solids.
    #            [2] H.L.Peng M.Z.Li* and W.H.Wang. Structural signature of plastic deformation in metallic glasses.
    particle_number = len(voro_input)
    voronoi_idx = {}
    i_fold_symm = {}
    voronoi_idx3_in = np.zeros(shape=[particle_number, ])
    voronoi_idx4_in = np.zeros(shape=[particle_number, ])
    voronoi_idx5_in = np.zeros(shape=[particle_number, ])
    voronoi_idx6_in = np.zeros(shape=[particle_number, ])
    voronoi_idx7_in = np.zeros(shape=[particle_number, ])
    i_fold_symm3_in = np.zeros(shape=[particle_number, ])
    i_fold_symm4_in = np.zeros(shape=[particle_number, ])
    i_fold_symm5_in = np.zeros(shape=[particle_number, ])
    i_fold_symm6_in = np.zeros(shape=[particle_number, ])
    i_fold_symm7_in = np.zeros(shape=[particle_number, ])
    for a in range(len(voro_input)):
        faces_in = voro_input[a]['faces']
        vertices_id_length = []
        for b in range(len(faces_in)):
            vertices_id_length.append(len(faces_in[b]['vertices']))
        count_all = vertices_id_length.count(3) + vertices_id_length.count(4) \
                    + vertices_id_length.count(5) + vertices_id_length.count(6) \
                    + vertices_id_length.count(7)
        voronoi_idx3_in[a] = vertices_id_length.count(3)
        voronoi_idx4_in[a] = vertices_id_length.count(4)
        voronoi_idx5_in[a] = vertices_id_length.count(5)
        voronoi_idx6_in[a] = vertices_id_length.count(6)
        voronoi_idx7_in[a] = vertices_id_length.count(7)
        i_fold_symm3_in[a] = vertices_id_length.count(3) / count_all
        i_fold_symm4_in[a] = vertices_id_length.count(4) / count_all
        i_fold_symm5_in[a] = vertices_id_length.count(5) / count_all
        i_fold_symm6_in[a] = vertices_id_length.count(6) / count_all
        i_fold_symm7_in[a] = vertices_id_length.count(7) / count_all
    voronoi_idx['3'] = voronoi_idx3_in
    voronoi_idx['4'] = voronoi_idx4_in
    voronoi_idx['5'] = voronoi_idx5_in
    voronoi_idx['6'] = voronoi_idx6_in
    voronoi_idx['7'] = voronoi_idx7_in
    i_fold_symm['3'] = i_fold_symm3_in
    i_fold_symm['4'] = i_fold_symm4_in
    i_fold_symm['5'] = i_fold_symm5_in
    i_fold_symm['6'] = i_fold_symm6_in
    i_fold_symm['7'] = i_fold_symm7_in
    return voronoi_idx, i_fold_symm


def compute_boop(voronoi_neighbour, points, radius):
    # compute boo based on voronoi neighbour and cutoff neighbour
    # Reference: [1] Structure-property relationships from universal signatures of plasticity in disordered solids.
    #            [2] https://pyboo.readthedocs.io/en/latest/intro.html
    # step1. compute boo based on voronoi neighbour
    bonds1 = []
    for x in range(len(voronoi_neighbour)):
        # 使用这种方法剔除了邻域不互相对称的颗粒，由剔除面积小于平均面积百分之五的邻域点所造成的不对称
        for y in range(len(voronoi_neighbour[x])):
            if voronoi_neighbour[x][y] > x:
                bonds1.append([x, voronoi_neighbour[x][y]])
    bonds1 = np.array(bonds1)
    inside1 = np.array([True] * len(points))

    q2m_1 = boo.bonds2qlm(points, bonds1, l=2)
    q4m_1 = boo.bonds2qlm(points, bonds1, l=4)
    q6m_1 = boo.bonds2qlm(points, bonds1, l=6)
    q8m_1 = boo.bonds2qlm(points, bonds1, l=8)
    q10m_1 = boo.bonds2qlm(points, bonds1, l=10)

    Q2m_1, inside1_2_2 = boo.coarsegrain_qlm(q2m_1, bonds1, inside1)
    Q4m_1, inside1_2_4 = boo.coarsegrain_qlm(q4m_1, bonds1, inside1)
    Q6m_1, inside1_2_6 = boo.coarsegrain_qlm(q6m_1, bonds1, inside1)
    Q8m_1, inside1_2_8 = boo.coarsegrain_qlm(q8m_1, bonds1, inside1)
    Q10m_1, inside1_2_10 = boo.coarsegrain_qlm(q10m_1, bonds1, inside1)

    q2_1 = boo.ql(q2m_1)
    q4_1 = boo.ql(q4m_1)
    q6_1 = boo.ql(q6m_1)
    q8_1 = boo.ql(q8m_1)
    q10_1 = boo.ql(q10m_1)

    w2_1 = boo.wl(q2m_1)
    w4_1 = boo.wl(q4m_1)
    w6_1 = boo.wl(q6m_1)
    w8_1 = boo.wl(q8m_1)
    w10_1 = boo.wl(q10m_1)

    Q2_1 = boo.ql(Q2m_1)
    Q4_1 = boo.ql(Q4m_1)
    Q6_1 = boo.ql(Q6m_1)
    Q8_1 = boo.ql(Q8m_1)
    Q10_1 = boo.ql(Q10m_1)

    W2_1 = boo.wl(Q2m_1)
    W4_1 = boo.wl(Q4m_1)
    W6_1 = boo.wl(Q6m_1)
    W8_1 = boo.wl(Q8m_1)
    W10_1 = boo.wl(Q10m_1)
    # step2. compute boo based on cutoff neighbour
    max_distance = 3.0 * radius[0]
    kdtree = KDTree(points)
    bonds2 = np.array(list(kdtree.query_pairs(max_distance)))
    inside2 = np.array([True] * len(points))

    q2m_2 = boo.bonds2qlm(points, bonds2, l=2)
    q4m_2 = boo.bonds2qlm(points, bonds2, l=4)
    q6m_2 = boo.bonds2qlm(points, bonds2, l=6)
    q8m_2 = boo.bonds2qlm(points, bonds2, l=8)
    q10m_2 = boo.bonds2qlm(points, bonds2, l=10)

    Q2m_2, inside2_2_2 = boo.coarsegrain_qlm(q2m_2, bonds2, inside2)
    Q4m_2, inside2_2_4 = boo.coarsegrain_qlm(q4m_2, bonds2, inside2)
    Q6m_2, inside2_2_6 = boo.coarsegrain_qlm(q6m_2, bonds2, inside2)
    Q8m_2, inside2_2_8 = boo.coarsegrain_qlm(q8m_2, bonds2, inside2)
    Q10m_2, inside2_2_10 = boo.coarsegrain_qlm(q10m_2, bonds2, inside2)

    q2_2 = boo.ql(q2m_2)
    q4_2 = boo.ql(q4m_2)
    q6_2 = boo.ql(q6m_2)
    q8_2 = boo.ql(q8m_2)
    q10_2 = boo.ql(q10m_2)

    w2_2 = boo.wl(q2m_2)
    w4_2 = boo.wl(q4m_2)
    w6_2 = boo.wl(q6m_2)
    w8_2 = boo.wl(q8m_2)
    w10_2 = boo.wl(q10m_2)

    Q2_2 = boo.ql(Q2m_2)
    Q4_2 = boo.ql(Q4m_2)
    Q6_2 = boo.ql(Q6m_2)
    Q8_2 = boo.ql(Q8m_2)
    Q10_2 = boo.ql(Q10m_2)

    W2_2 = boo.wl(Q2m_2)
    W4_2 = boo.wl(Q4m_2)
    W6_2 = boo.wl(Q6m_2)
    W8_2 = boo.wl(Q8m_2)
    W10_2 = boo.wl(Q10m_2)

    boop_all = np.array(list(zip(q2_1, q4_1, q6_1, q8_1, q10_1,
                                 w2_1, w4_1, w6_1, w8_1, w10_1,
                                 q2_2, q4_2, q6_2, q8_2, q10_2,
                                 w2_2, w4_2, w6_2, w8_2, w10_2,
                                 Q2_1, Q4_1, Q6_1, Q8_1, Q10_1,
                                 W2_1, W4_1, W6_1, W8_1, W10_1,
                                 Q2_2, Q4_2, Q6_2, Q8_2, Q10_2,
                                 W2_2, W4_2, W6_2, W8_2, W10_2)))

    return boop_all


def compute_cluster_packing_efficiency(voronoi_neighbour_use_input, points_input, radius_input):
    # compute cluster packing efficiency
    # Reference: Yang, L. et al. Atomic-scale mechanisms of the glass-forming ability in metallic glasses. Phys. Rev. Lett. 109, 105502 (2012).
    cluster_packing_efficiency = np.zeros(shape=[len(voronoi_neighbour_use_input), ])
    for a in range(len(voronoi_neighbour_use_input)):
        if len(voronoi_neighbour_use_input[a]) >= 4:
            points_now = []
            radius_now = []
            origin_particle = points_input[a]
            origin_radius = radius_input[a]
            for b in range(len(voronoi_neighbour_use_input[a])):
                points_now.append(points_input[voronoi_neighbour_use_input[a][b]])
                radius_now.append(radius_input[voronoi_neighbour_use_input[a][b]])
            cpe_ch = ConvexHull(points_now)
            cpe_simplice = np.array(cpe_ch.simplices)
            interstice_volume_mid = np.zeros(shape=[len(cpe_simplice), ])
            cluster_packing_efficiency_x = compute_cluster_packing_efficiency_single_particle(cpe_simplice,
                                                                                              np.array(points_now),
                                                                                              np.array(radius_now),
                                                                                              interstice_volume_mid,
                                                                                              origin_particle,
                                                                                              origin_radius)

            cluster_packing_efficiency[a] = cluster_packing_efficiency_x
        else:
            cluster_packing_efficiency[a] = 0.0
    return cluster_packing_efficiency


@jit(nopython=True)
def compute_cluster_packing_efficiency_single_particle(simplice_input, points_now, radius_now, interstice_volume_mid,
                                                       origin_particle, origin_radius):
    triangle_volume_x = np.zeros_like(interstice_volume_mid)
    pack_volume_x = np.zeros_like(interstice_volume_mid)
    for b in range(len(simplice_input)):
        volume_triangle = compute_tetrahedron_volume(points_now[simplice_input[b][0]],
                                                     points_now[simplice_input[b][1]],
                                                     points_now[simplice_input[b][2]],
                                                     origin_particle)
        volume_pack = (compute_solide_angle(origin_particle, points_now[simplice_input[b][0]],
                                            points_now[simplice_input[b][1]],
                                            points_now[simplice_input[b][2]])
                       * origin_radius ** 3 +
                       compute_solide_angle(points_now[simplice_input[b][2]], origin_particle,
                                            points_now[simplice_input[b][0]], points_now[simplice_input[b][1]])
                       * radius_now[simplice_input[b][2]] ** 3 +
                       compute_solide_angle(points_now[simplice_input[b][1]],
                                            points_now[simplice_input[b][2]], origin_particle,
                                            points_now[simplice_input[b][0]])
                       * radius_now[simplice_input[b][1]] ** 3 +
                       compute_solide_angle(points_now[simplice_input[b][0]], points_now[simplice_input[b][1]],
                                            points_now[simplice_input[b][2]], origin_particle) * radius_now[
                           simplice_input[b][0]] ** 3) / 3
        triangle_volume_x[b] = volume_triangle
        pack_volume_x[b] = volume_pack
    return np.sum(pack_volume_x) / np.sum(triangle_volume_x)


@jit(nopython=True)
def MRO(old_feature_SRO_array_input, boop_SRO_array_input, cpe_SRO_array_input, MRO_array_input, f_use_array_input,
        voronoi_neighbour_input, neigh_id_length_index_input):
    feature_MRO = np.empty_like(MRO_array_input)
    for aa in range(18):
        a = 5 * aa
        feature_now = old_feature_SRO_array_input[:, aa]
        for b in range(len(voronoi_neighbour_input)):
            f_use_not = np.zeros_like(f_use_array_input)
            for c in range(neigh_id_length_index_input[b]):
                f_use_not[c] = feature_now[voronoi_neighbour_input[b][c]]
            f_use = f_use_not[0: neigh_id_length_index_input[b]]
            feature_MRO[a][b] = feature_now[b]
            feature_MRO[a + 1][b] = np.min(f_use)
            feature_MRO[a + 2][b] = np.max(f_use)
            feature_MRO[a + 3][b] = np.mean(f_use)
            mean = np.mean(f_use)
            square = 0.0
            for c in range(len(f_use)):
                square += (f_use[c] - mean) ** 2
            sqrt = math.sqrt((square / len(f_use)))
            feature_MRO[a + 4][b] = sqrt
    for aa in range(1):
        a = (18 + aa) * 5
        feature_now = cpe_SRO_array_input
        for b in range(len(voronoi_neighbour_input)):
            f_use_not = np.zeros_like(f_use_array_input)
            for c in range(neigh_id_length_index_input[b]):
                f_use_not[c] = feature_now[voronoi_neighbour_input[b][c]]
            f_use = f_use_not[0: neigh_id_length_index_input[b]]
            feature_MRO[a][b] = feature_now[b]
            feature_MRO[a + 1][b] = np.min(f_use)
            feature_MRO[a + 2][b] = np.max(f_use)
            feature_MRO[a + 3][b] = np.mean(f_use)
            mean = np.mean(f_use)
            square = 0.0
            for c in range(len(f_use)):
                square += (f_use[c] - mean) ** 2
            sqrt = math.sqrt((square / len(f_use)))
            feature_MRO[a + 4][b] = sqrt
    for aa in range(20):
        a = (19 + aa) * 5
        feature_now = boop_SRO_array_input[:, aa]
        for b in range(len(voronoi_neighbour_input)):
            f_use_not = np.zeros_like(f_use_array_input)
            for c in range(neigh_id_length_index_input[b]):
                f_use_not[c] = feature_now[voronoi_neighbour_input[b][c]]
            f_use = f_use_not[0: neigh_id_length_index_input[b]]
            feature_MRO[a][b] = feature_now[b]
            feature_MRO[a + 1][b] = np.min(f_use)
            feature_MRO[a + 2][b] = np.max(f_use)
            feature_MRO[a + 3][b] = np.mean(f_use)
            mean = np.mean(f_use)
            square = 0.0
            for c in range(len(f_use)):
                square += (f_use[c] - mean) ** 2
            sqrt = math.sqrt((square / len(f_use)))
            feature_MRO[a + 4][b] = sqrt
    for aa in range(20):
        a = aa + 195
        feature_now = boop_SRO_array_input[:, aa + 20]
        for b in range(len(voronoi_neighbour_input)):
            feature_MRO[a][b] = feature_now[b]
    return feature_MRO


def zip_feature(Coordination_number_by_Voronoi_tessellation, Coordination_number_by_cutoff_distance,
                Voronoi_idx, cellfraction, i_fold_symm, area_weight_i_fold_symm):
    feature_all = np.array(list(zip(Coordination_number_by_Voronoi_tessellation,
                                    Coordination_number_by_cutoff_distance,
                                    Voronoi_idx['3'], Voronoi_idx['4'], Voronoi_idx['5'], Voronoi_idx['6'],
                                    Voronoi_idx['7'],
                                    cellfraction,
                                    i_fold_symm['3'], i_fold_symm['4'], i_fold_symm['5'], i_fold_symm['6'],
                                    i_fold_symm['7'],
                                    area_weight_i_fold_symm['3'],
                                    area_weight_i_fold_symm['4'],
                                    area_weight_i_fold_symm['5'],
                                    area_weight_i_fold_symm['6'],
                                    area_weight_i_fold_symm['7'])))
    return feature_all


def compute_conventional_feature(points, area_all, neighbour, voronoi, radius):
    # step1. set constant
    particle_number = len(points)
    MRO_array = np.empty(shape=[215, particle_number])
    f_use_array = np.empty(shape=[particle_number, ])
    # step1. modify voronoi neighbour information
    voronoi_neighbour = []
    for x in range(len(neighbour)):
        voronoi_neighbour_now = []
        for value in neighbour[x]:
            if value >= 0:
                voronoi_neighbour_now.append(value)
        voronoi_neighbour.append(voronoi_neighbour_now)
    bonds = []
    for x in range(len(voronoi_neighbour)):
        for y in range(len(voronoi_neighbour[x])):
            if voronoi_neighbour[x][y] > x:
                bonds.append([x, voronoi_neighbour[x][y]])
    bonds = np.array(bonds)
    voronoi_neighbour_use = []
    for x in range(len(neighbour)):
        voronoi_neighbour_use.append([])
    for x in range(len(bonds)):
        voronoi_neighbour_use[bonds[x][0]].append(bonds[x][1])
        voronoi_neighbour_use[bonds[x][1]].append(bonds[x][0])
    neigh_id_length_index = []
    for x in range(len(voronoi_neighbour_use)):
        neigh_id_length_index.append(len(voronoi_neighbour_use[x]))
    neigh_id = np.zeros(shape=[particle_number, max(neigh_id_length_index)], dtype=int)
    for x in range(len(voronoi_neighbour_use)):
        for y in range(len(voronoi_neighbour_use[x])):
            neigh_id[x][y] = int(voronoi_neighbour_use[x][y])
    neigh_id_length_index = np.array(neigh_id_length_index)
    # step2. compute
    # 2.1 coordination number by voronoi tessellation
    Coordination_number_by_Voronoi_tessellation = np.zeros(shape=[len(points), ])
    for x in range(len(voronoi_neighbour_use)):
        Coordination_number_by_Voronoi_tessellation[x] = len(voronoi_neighbour_use[x])
    # 2.2 weighted i-fold symm
    area_weight_i_fold_symm = compute_weight_i_fold_symm(voronoi, area_all)
    # 2.3 coordination number by cutoff distance
    Coordination_number_by_cutoff_distance = compute_coordination_number_by_cutoff_distance(points, radius)
    # 2.4 cell fraction
    cellfraction = compute_cellfraction(voronoi, radius)
    # 2.5 voronoi index and i-fold symm
    Voronoi_idx, i_fold_symm = compute_voronoi_idx(voronoi)
    # 2.6 zip feature above
    feature_all = zip_feature(Coordination_number_by_Voronoi_tessellation, Coordination_number_by_cutoff_distance,
                              Voronoi_idx, cellfraction, i_fold_symm, area_weight_i_fold_symm)
    # 2.7 boop
    boop_all = compute_boop(voronoi_neighbour, points, radius)
    # 2.8 cluster packing efficiency
    Cpe = compute_cluster_packing_efficiency(voronoi_neighbour_use, points, radius)
    # 2.9 MRO
    old_feature_SRO_array = feature_all
    boop_SRO_array = boop_all
    cpe_SRO_array = Cpe
    feature_MRO_out = MRO(old_feature_SRO_array, boop_SRO_array, cpe_SRO_array, MRO_array, f_use_array, neigh_id,
                          neigh_id_length_index)
    return feature_MRO_out.T


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def read_position_information(dump_path, frame):
    # 读取颗粒位置信息
    particle_info = open(dump_path + '/dump-' + str(frame) + '.sample', 'r')
    lines = particle_info.readlines()
    particle_info.close()
    lines = lines[9:]
    Par_id = list(map(int, map(float, [re.findall(r'-?\d+\.?\d*e?[-+]?\d*', line)[0] for line in lines])))
    Par_id_read = list(map(int, map(float, [re.findall(r'-?\d+\.?\d*e?[-+]?\d*', line)[0] for line in lines])))
    Par_xcor_read = list(map(float, [re.findall(r'-?\d+\.?\d*e?[-+]?\d*', line)[3] for line in lines]))
    Par_ycor_read = list(map(float, [re.findall(r'-?\d+\.?\d*e?[-+]?\d*', line)[4] for line in lines]))
    Par_zcor_read = list(map(float, [re.findall(r'-?\d+\.?\d*e?[-+]?\d*', line)[5] for line in lines]))
    Par_radius_read = list(map(float, [re.findall(r'-?\d+\.?\d*e?[-+]?\d*', line)[2] for line in lines]))
    Par_id.sort()
    Par_xcor = [Par_xcor_read[Par_id_read.index(Par_id[x])] for x in range(len(Par_id))]
    Par_ycor = [Par_ycor_read[Par_id_read.index(Par_id[x])] for x in range(len(Par_id))]
    Par_zcor = [Par_zcor_read[Par_id_read.index(Par_id[x])] for x in range(len(Par_id))]
    Par_radius = [Par_radius_read[Par_id_read.index(Par_id[x])] for x in range(len(Par_id))]
    Par_coord = np.array(list(zip(Par_xcor, Par_ycor, Par_zcor)))
    x_min = float('%.4f' % (np.min(Par_xcor) - Par_radius[0]))
    x_max = float('%.4f' % (np.max(Par_xcor) + Par_radius[0]))
    y_min = float('%.4f' % (np.min(Par_ycor) - Par_radius[0]))
    y_max = float('%.4f' % (np.max(Par_ycor) + Par_radius[0]))
    z_min = float('%.4f' % (np.min(Par_zcor) - Par_radius[0]))
    z_max = np.max(Par_zcor) + Par_radius[0]
    boundary = [[x_min, x_max], [y_min, y_max], [z_min, z_max]]
    return Par_coord, Par_radius, boundary


def compute_area(vertices_input, adjacent_cell_input, vertices_id_input, simplice_input):
    area_judge_in = np.zeros(shape=[len(adjacent_cell_input), ], dtype=int)
    area_in = np.zeros(shape=[len(adjacent_cell_input), ])
    sing_area = np.zeros(shape=[len(simplice_input), ])
    for a in range(len(simplice_input)):
        sing_area[a] = compute_simplice_area(vertices_input[simplice_input[a][0]],
                                             vertices_input[simplice_input[a][1]],
                                             vertices_input[simplice_input[a][2]])
    for a in range(len(simplice_input)):
        for b in range(len(adjacent_cell_input)):
            if simplice_input[a][0] in vertices_id_input[b]:
                if simplice_input[a][1] in vertices_id_input[b]:
                    if simplice_input[a][2] in vertices_id_input[b]:
                        area_in[b] += sing_area[a]
    average_area = np.mean(area_in)
    for a in range(len(adjacent_cell_input)):
        if area_in[a] >= 0.05 * average_area:
            area_judge_in[a] = 1
    return area_judge_in, area_in


def eliminate_useless_adjacent_cell(voronoi):
    # 剔除面积小于平均面积百分之五的邻域点,这可能会造成互为邻域颗粒之间的不对称，后面的程序需要逐一处理
    adjacent_cell_all = []
    area_all_particle = []
    for x in range(len(voronoi)):
        vertices = voronoi[x]['vertices']
        ch = ConvexHull(vertices)
        simplice = np.array(ch.simplices)
        faces = voronoi[x]['faces']
        adjacent_cell = []
        for y in range(len(faces)):
            adjacent_cell.append(faces[y]['adjacent_cell'])
        vert_id = []
        for y in range(len(faces)):
            vert_id.append(faces[y]['vertices'])
        area_judge, area = compute_area(vertices, adjacent_cell, vert_id, simplice)
        adjacent_cell_use = []
        for y in range(len(adjacent_cell)):
            if area_judge[y] == 1:
                adjacent_cell_use.append(adjacent_cell[y])
        adjacent_cell_all.append(adjacent_cell_use)
        area_all_particle.append(area)
    return adjacent_cell_all, area_all_particle


def compute_voronoi_neighbour(points, radius, limits):
    dispersion = 5 * radius[0]
    voronoi = pyvoro.compute_voronoi(points, limits, dispersion, periodic=[False] * 3)
    neighbour, area = eliminate_useless_adjacent_cell(voronoi)
    return voronoi, neighbour, area


def main_function(path, path_output, scenario):
    # dump files
    mkdir(path_output)
    dump_path = path
    list_dir = os.listdir(dump_path)
    dump_frame = []
    file_prefix = 'dump-'
    file_suffix = '.sample'
    prefix_len = len(file_prefix)
    suffix_len = len(file_suffix)
    for file in list_dir:
        dump_frame.append(int(file[prefix_len:][:-suffix_len]))
    dump_frame = sorted(dump_frame)
    start_frame = np.min(dump_frame)
    end_frame = np.max(dump_frame)
    frame_interval = (end_frame - start_frame) / scenario
    frame_list = np.arange(start_frame, end_frame, frame_interval)
    frame_list = np.append(frame_list, end_frame)
    frame_list = frame_list.astype(int)
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # 循环开始，提取每一步数据
    #
    for idx, frame in enumerate(frame_list):
        if idx == 0: continue
        # step1. Gets the prepared coordinates information and neighborhood information
        Par_coord, Par_radius, boundary = read_position_information(path, frame)
        voronoi, voronoi_neighbour, area_all = compute_voronoi_neighbour(Par_coord, Par_radius, boundary)
        print(60 * '*')
        print('The %d th frame' % frame)
        print(60 * '*')
        # step2. Compute structure property(symmetry feature, interstice distribution and conventional feature)
        symmetry_feature = compute_symmetry_functions(points=Par_coord, radius=Par_radius)
        interstice_distribution = compute_interstice_distribution(neighbour=voronoi_neighbour, points=Par_coord,
                                                                  radius=Par_radius)
        conventional_feature = compute_conventional_feature(points=Par_coord, area_all=area_all,
                                                            neighbour=voronoi_neighbour, voronoi=voronoi,
                                                            radius=Par_radius)
        # step3. Output structure property
        writer = pd.ExcelWriter(path_output + '/feature_all-' + str(frame) + '.xlsx')
        pd.DataFrame(symmetry_feature).to_excel(writer, sheet_name='symmetry feature')
        pd.DataFrame(interstice_distribution).to_excel(writer, sheet_name='interstice distribution')
        pd.DataFrame(conventional_feature).to_excel(writer, sheet_name='conventional feature')
        writer.save()
        writer.close()


# ==================================================================
# S T A R T
#
if __name__ == '__main__':
    path_ = 'D:/循环剪切试验和机器学习/cyc5300fric01shearrate025/sort position'
    path_output_ = 'D:/循环剪切试验和机器学习/cyc5300fric01shearrate025'
    scenario = 1000
    argList = argv
    argc = len(argList)
    i = 0
    while (i < argc):
        if (argList[i][:2] == "-c"):
            i += 1
            case = str(argList[i])
        elif (argList[i][:2] == "-t"):
            i += 1
            test_id = int(argList[i])
        elif (argList[i][:4] == "-str"):
            i += 1
            shear_strain = float(argList[i])
        elif (argList[i][:2] == "-w"):
            i += 1
            strain_window = float(argList[i])
        elif (argList[i][:4] == "-rat"):
            i += 1
            shear_rate = float(argList[i])
        elif (argList[i][:2] == "-n"):
            i += 1
            neighborhood_size = float(argList[i])
        elif (argList[i][:4] == "-dis"):
            i += 1
            distance = str(argList[i])
        elif (argList[i][:3] == "-lb"):
            i += 1
            start_strain = float(argList[i])
        elif (argList[i][:3] == "-ub"):
            i += 1
            end_strain = float(argList[i])
        elif (argList[i][:4] == "-ran"):
            i += 1
            strain_interval = float(argList[i])
        elif (argList[i][:4] == "-sce"):
            i += 1
            scenario = int(argList[i])
        elif (argList[i][:2] == "-h"):
            print(__doc__)
            exit(0)
        i += 1

    print(path_)
    print("Running scenario:  %d" % scenario)
    main_function(path_, path_output_, scenario)
