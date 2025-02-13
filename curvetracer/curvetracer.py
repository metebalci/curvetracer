# SPDX-FileCopyrightText: 2024 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse
from contextlib import contextmanager
import math
import sys
import time
from typing import List, Type, Tuple

from .common import PSChannel, VChannel, IChannel, TChannel

def median(f):
    v = []
    v.append(f())
    v.append(f())
    v.append(f())
    return sorted(v)[1]

def run_oc(output_file,
           vgs_range:List[float],
           vds_range:Tuple[float, float, float, float, float],
           tmax:float,
           tcon:float,
           max_id:float,
           max_ig:float,
           ps_vds:Type[PSChannel],
           ps_vgs:Type[PSChannel],
           delay_after_ps_on:float,
           dmm_vds:Type[VChannel],
           dmm_vgs:Type[VChannel],
           dmm_id:Type[IChannel],
           dmm_t:Type[TChannel])->None:

    vds_start, vds_fine_stop, vds_fine_step, vds_stop, vds_step = vds_range

    def ps_off():
        ps_vgs.state = False
        ps_vds.state = False

    def ps_on():
        ps_vgs.state = True
        ps_vds.state = True

    ps_off()
    ps_vds.current = max_id
    ps_vgs.current = max_ig
    try:
        for vgs in vgs_range:
            ps_vgs.voltage = vgs
            while True:
                t_value = median(lambda: dmm_t.temperature)
                if t_value < tcon:
                    break
                else:
                    print('%fC' % t_value, file=sys.stderr)
                    time.sleep(2)

            vds = vds_start
            while vds <= vds_stop:
                ps_vds.voltage = vds

                ps_on()
                id_value = median(lambda: dmm_id.current)
                vds_value = median(lambda: dmm_vds.voltage)
                vgs_value = median(lambda: dmm_vgs.voltage)
                t_value = median(lambda: dmm_t.temperature)
                ps_off()

                print('%g %g %g %g %g %g' % (-vgs,
                                             vds,
                                             id_value,
                                             vds_value,
                                             vgs_value,
                                             t_value))

                # if measured value is not +-5% retry
                if ((vds != 0) and
                    ((vds_value > 1.05 * vds) or
                     (vds_value < 0.95 * vds))):
                    # retry
                    continue

                # if measured value is not +-5% retry
                if ((vgs != 0) and
                    ((math.fabs(vgs_value) > math.fabs(1.05 * vgs)) or
                     (math.fabs(vgs_value) < math.fabs(0.95 * vgs)))):
                    # retry
                    continue

                print('%g %g %g %g %g %g' % (-vgs,
                                             vds,
                                             id_value,
                                             vds_value,
                                             vgs_value,
                                             t_value),
                      file=output_file)

                if t_value > tmax:
                    print('powering off to cool down...', file=sys.stderr)
                    while t_value > tcon:
                        t_value = dmm_t.temperature
                        print('%fC' % t_value, file=sys.stderr)
                        time.sleep(2)

                if vds < vds_fine_stop:
                    vds = vds + vds_fine_step

                else:
                    vds = vds + vds_step

    finally:
        ps_off()

def run_tc(output_file,
           vds_range:List[float],
           vgs_range:Tuple[float, float, float],
           tmax:float,
           tcon:float,
           max_id:float,
           max_ig:float,
           ps_vds:Type[PSChannel],
           ps_vgs:Type[PSChannel],
           delay_after_ps_on:float,
           dmm_vds:Type[VChannel],
           dmm_vgs:Type[VChannel],
           dmm_id:Type[IChannel],
           dmm_t:Type[TChannel])->None:

    vgs_start, vgs_fine_stop, vgs_fine_step, vgs_stop, vgs_step = vgs_range

    def ps_off():
        ps_vgs.state = False
        ps_vds.state = False

    def ps_on():
        ps_vgs.state = True
        ps_vds.state = True
        time.sleep(delay_after_ps_on)

    ps_off()
    ps_vds.current = max_id
    ps_vgs.current = max_ig
    try:
        for vds in vds_range:
            ps_vds.voltage = vds
            while True:
                t_value = median(lambda: dmm_t.temperature)
                if t_value < tcon:
                    break
                else:
                    print('%fC' % t_value, file=sys.stderr)
                    time.sleep(2)

            vgs = vgs_start
            while vgs >= vgs_stop:
                ps_vgs.voltage = vgs

                ps_on()
                id_value = median(lambda: dmm_id.current)
                vds_value = median(lambda: dmm_vds.voltage)
                vgs_value = median(lambda: dmm_vgs.voltage)
                t_value = median(lambda: dmm_t.temperature)
                ps_off()

                print('%g %g %g %g %g %g' % (vds,
                                             -vgs,
                                             id_value,
                                             vds_value,
                                             vgs_value,
                                             t_value))

                # if measured value is not +-5% retry
                if ((vds != 0) and
                    ((vds_value > 1.05 * vds) or
                     (vds_value < 0.95 * vds))):
                    # retry
                    continue

                # if measured value is not +-5% retry
                if ((vgs != 0) and
                    ((math.fabs(vgs_value) > math.fabs(1.05 * vgs)) or
                     (math.fabs(vgs_value) < math.fabs(0.95 * vgs)))):
                    # retry
                    continue

                print('%g %g %g %g %g %g' % (vds,
                                             -vgs,
                                             id_value,
                                             vds_value,
                                             vgs_value,
                                             t_value),
                      file=output_file)

                if t_value > tmax:
                    print('powering off to cool down...', file=sys.stderr)
                    while t_value > tcon:
                        t_value = median(dmm_t.temperature)
                        print('%fC' % t_value, file=sys.stderr)
                        time.sleep(2)

                if vgs > vgs_fine_stop:
                    vgs = vgs - vgs_fine_step

                else:
                    vgs = vgs - vgs_step

    finally:
        ps_off()
