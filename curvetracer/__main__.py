# SPDX-FileCopyrightText: 2024 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
import configparser
import sys
from typing import List, Type, Tuple

from .common import DAQChannel, PSChannel, VChannel, IChannel, TChannel
from .common import ConfigException
from .curvetracer import run_oc, run_tc
from .daq6510 import DAQ6510
from .nge103b import NGE103B

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import CubicSpline

def parse_config_for_device(config):
    return (config['device']['name'],
            float(config['device']['idmax']),
            float(config['device']['igmax']))

def parse_config_for_ps(config):
    if config['ps']['type'] == 'nge103b':
        ps = NGE103B('nge103.z54.org')

    else:
        raise ConfigException('unknown PowerSupply type')

    ps_vds = ps.get_channel(int(config['ps']['vds_chno']))
    ps_vgs = ps.get_channel(int(config['ps']['vgs_chno']))
    delay_after_ps_on = float(config['ps']['delay_after_ps_on'])

    print(ps.idn())

    return ps, ps_vds, ps_vgs, delay_after_ps_on

def parse_config_for_daq(config):
    if config['daq']['type'] == 'daq6510':
        daq = DAQ6510('daq6510.z54.org')

    else:
        raise ConfigException('unknown DAQ type')

    dmm_vds = daq.get_voltage_channel(int(config['daq']['vds_chno']))
    dmm_vgs = daq.get_voltage_channel(int(config['daq']['vgs_chno']))
    dmm_id = daq.get_current_channel(int(config['daq']['id_chno']))
    dmm_t = daq.get_temperature_channel(int(config['daq']['t_chno']),
                                        config['daq']['tc_type'])
    daq.watch(int(config['daq']['watch_chno']))

    print(daq.idn())

    return daq, dmm_vds, dmm_vgs, dmm_id, dmm_t

def command_oc(args):
    config = configparser.ConfigParser()
    config.read(args.config_file)

    dname, idmax, igmax = parse_config_for_device(config)
    ps, ps_vds, ps_vgs, delay_after_ps_on = parse_config_for_ps(config)
    daq, dmm_vds, dmm_vgs, dmm_id, dmm_t = parse_config_for_daq(config)

    vgs_range = config['test.oc']['vgs'].split(',')
    vgs_range = [float(x.strip()) for x in vgs_range]

    vds_range = config['test.oc']['vds'].split(',')
    vds_range = tuple([float(x.strip()) for x in vds_range])

    tmax = float(config['test.oc']['tmax'])
    tcon = float(config['test.oc']['tcon'])

    try:
        with open('%s.oc' % dname, 'w') as output_file:
            print('oc', file=output_file)
            print(dname, file=output_file)
            run_oc(output_file,
                   vgs_range, vds_range,
                   tmax, tcon, idmax, igmax,
                   ps_vds, ps_vgs, delay_after_ps_on,
                   dmm_vds, dmm_vgs, dmm_id, dmm_t)
    finally:
        if (hasattr(ps, 'turn_all_channels_off') and
            callable(ps.turn_all_channels_off)):
            ps.turn_all_channels_off()

def command_tc(args):
    config = configparser.ConfigParser()
    config.read(args.config_file)

    dname, idmax, igmax = parse_config_for_device(config)
    ps, ps_vds, ps_vgs, delay_after_ps_on = parse_config_for_ps(config)
    daq, dmm_vds, dmm_vgs, dmm_id, dmm_t = parse_config_for_daq(config)

    vds_range = config['test.tc']['vds'].split(',')
    vds_range = [float(x.strip()) for x in vds_range]

    vgs_range = config['test.tc']['vgs'].split(',')
    vgs_range = tuple([float(x.strip()) for x in vgs_range])

    tmax = float(config['test.tc']['tmax'])
    tcon = float(config['test.tc']['tcon'])

    try:
        with open('%s.tc' % dname, 'w') as output_file:
            print('tc', file=output_file)
            print(dname, file=output_file)
            run_tc(output_file,
                   vds_range, vgs_range,
                   tmax, tcon, idmax, igmax,
                   ps_vds, ps_vgs, delay_after_ps_on,
                   dmm_vds, dmm_vgs, dmm_id, dmm_t)
    finally:
        if (hasattr(ps, 'turn_all_channels_off') and
            callable(ps.turn_all_channels_off)):
            ps.turn_all_channels_off()

def command_plot_oc(f, output_file):
    dname = f.readline().strip()
    dataset = {}
    tmax = 0
    while True:
        line = f.readline()
        if len(line) == 0:
            break
        line = line.strip().split()
        line = [float(x) for x in line]
        vgs = line[0]
        if vgs not in dataset:
            dataset[vgs] = [list(), list()]
        vds = line[1]
        id_measured = line[2] * 1000
        vds_measured = line[3]
        vgs_measured = line[4]
        t_measured = line[5]
        dataset[vgs][0].append(vds_measured)
        dataset[vgs][1].append(id_measured)
        tmax = max(tmax, t_measured)

    fig, ax = plt.subplots()
    xmin = 0
    xmax = 0
    ymin = 0
    ymax = 0
    for vgs in sorted(dataset.keys()):
        X = dataset[vgs][0]
        Y = dataset[vgs][1]
        xmin = min(xmin, min(X))
        xmax = max(xmax, max(X))
        ymin = min(ymin, min(Y))
        ymax = max(ymax, max(Y))
        ax.plot(X, Y, label='Vgs=%gV' % vgs)

    ax.set_xlabel('Vds (V)')
    ax.set_xlim(xmin, xmax)
    ax.set_ylabel('Id (mA)')
    ax.set_ylim(ymin, ymax)
    ax.set_title('%s Output Characteristic' % dname)
    ax.legend()
    if output_file is None:
        plt.show()
    else:
        plt.savefig(output_file)

def command_plot_tc(f, output_file, with_temp):
    dname = f.readline().strip()
    dataset = {}
    tmax = 0
    while True:
        line = f.readline()
        if len(line) == 0:
            break
        line = line.strip().split()
        line = [float(x) for x in line]
        vds = line[0]
        if vds not in dataset:
            dataset[vds] = [list(), list(), list()]
        vgs = line[1]
        id_measured = line[2] * 1000
        vds_measured = line[3]
        vgs_measured = line[4]
        t_measured = line[5]
        dataset[vds][0].append(vgs_measured)
        dataset[vds][1].append(id_measured)
        dataset[vds][2].append(t_measured)
        tmax = max(tmax, t_measured)

    fig, ax = plt.subplots()
    ax2 = ax.twinx()
    xmin = 0
    xmax = 0
    ymin = 0
    ymax = 0
    colors = [
        'b', 'c', 'g', 'm', 'r', 'y'
    ]
    for i, vds in enumerate(sorted(dataset.keys())):
        X = dataset[vds][0]
        Y = dataset[vds][1]
        T = dataset[vds][2]
        xmin = min(xmin, min(X))
        xmax = min(xmax, max(X))
        ymin = min(ymin, min(Y))
        ymax = max(ymax, max(Y))
        if with_temp:
            ax.plot(X, T, color=colors[i], linestyle='dotted')
        ax2.plot(X, Y, label='Vds=%gV' % vds, color=colors[i])

    ax2.set_ylabel('Id (mA)')
    ax2.set_ylim(ymin, ymax)
    ax.set_xlabel('Vgs (V)')
    ax.set_xlim(xmin, xmax)
    ax.set_ylabel('Temperature (C)')
    ax.set_ylim(20, tmax)
    ax.set_title('%s Transfer Characteristic' % dname)
    ax.legend()
    if output_file is None:
        plt.show()
    else:
        plt.savefig(output_file)

def command_plot(args):
    with open(args.input_file, 'r') as f:
        line = f.readline().strip()
        if line == 'oc':
            command_plot_oc(f, args.output_file)

        elif line == 'tc':
            command_plot_tc(f, args.output_file, args.temp)

        else:
            return

def main():
    parser = argparse.ArgumentParser(
        prog='curvetracer',
        description='JFET curvetracer using LXI capable PowerSupply and DMM DAQ')
    parser.add_argument('-c', '--config-file',
                        help='config file')
    parser.add_argument('-i', '--input-file',
                        help='input file')
    parser.add_argument('-o', '--output-file',
                        help='output file')
    parser.add_argument('-t', '--temp',
                        default=False,
                        action='store_true',
                        help='show temperature data on the plot')
    parser.add_argument('command',
                        help='operation, use help command for more info')
    args = parser.parse_args()
    if args.command == 'oc':
        if args.config_file is None:
            print('oc requires config file')
            sys.exit(1)

        command_oc(args)

    elif args.command == 'tc':
        if args.config_file is None:
            print('tc requires config file')
            sys.exit(1)

        command_tc(args)

    elif args.command == 'plot':
        if args.input_file is None:
            print('plot requires input file')
            sys.exit(1)

        command_plot(args)

    elif args.command == 'help':
        print('Available commands are:')
        print('  - oc: measure output characteristic (vds vs. id)')
        print('  - tc: measure transfer characteristic (vgs vs. id)')
        print('  - plot: plot oc or tc data generated by oc and tc commands')

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == '__main__':
    main()
