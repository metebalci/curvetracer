# SPDX-FileCopyrightText: 2024 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Type, Tuple

import vxi11

from .common import WrongInstrumentException
from .common import VChannel, IChannel, TChannel
from .common import ScpiCommonCommands

class DAQ6510VChannel(VChannel):
    def __init__(self, device, chno:int)->None:
        self.device = device
        self.instrument = device.instrument
        self.chno = chno
        # setup voltage measurement
        # precise but with 10 repeats not 100
        # these settings are saved per function
        self.instrument.write('SENSE:FUNCTION:ON "VOLTAGE:DC", (@%d)' % self.chno)
        self.instrument.write('SENSE:VOLTAGE:DC:NPLCYCLES 1, (@%d)' % self.chno)
        self.instrument.write('SENSE:VOLTAGE:DC:LINE:SYNC ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:VOLTAGE:DC:AZERO:STATE ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:VOLTAGE:DC:AVERAGE:COUNT 10, (@%d)' % self.chno)
        self.instrument.write('SENSE:VOLTAGE:DC:AVERAGE:TCONTROL REPEAT, (@%d)' % self.chno)
        self.instrument.write('SENSE:VOLTAGE:DC:AVERAGE:STATE ON, (@%d)' % self.chno)

    @property
    def voltage(self)->float:
        self.instrument.write('ROUTE:CHANNEL:CLOSE (@%d)' % self.chno)
        self.device.wai()
        return float(self.instrument.ask('MEASURE:VOLTAGE:DC?'))

class DAQ6510IChannel(IChannel):
    def __init__(self, device, chno:int)->None:
        self.device = device
        self.instrument = device.instrument
        self.chno = chno
        # setup current measurement
        # precise but with 10 repeats not 100
        # these settings are saved per function
        self.instrument.write('SENSE:FUNCTION:ON "CURRENT:DC", (@%d)' % self.chno)
        self.instrument.write('SENSE:CURRENT:DC:NPLCYCLES 1, (@%d)' % self.chno)
        self.instrument.write('SENSE:CURRENT:DC:LINE:SYNC ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:CURRENT:DC:AZERO:STATE ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:CURRENT:DC:AVERAGE:COUNT 10, (@%d)' % self.chno)
        self.instrument.write('SENSE:CURRENT:DC:AVERAGE:TCONTROL REPEAT, (@%d)' % self.chno)
        self.instrument.write('SENSE:CURRENT:DC:AVERAGE:STATE ON, (@%d)' % self.chno)

    @property
    def current(self)->float:
        self.instrument.write('ROUTE:CHANNEL:CLOSE (@%d)' % self.chno)
        self.device.wai()
        return float(self.instrument.ask('MEASURE:CURRENT:DC?'))

class DAQ6510TChannel(TChannel):
    def __init__(self, device, chno:int, sensor_type:str)->None:
        self.device = device
        self.instrument = device.instrument
        self.chno = chno
        # setup current measurement
        # precise but with 10 repeats not 100
        # these settings are saved per function
        self.instrument.write('SENSE:FUNCTION:ON "TEMPERATURE", (@%d)' % self.chno)
        if (sensor_type == 'B' or
            sensor_type == 'E' or
            sensor_type == 'J' or
            sensor_type == 'K' or
            sensor_type == 'N' or
            sensor_type == 'R' or
            sensor_type == 'S' or
            sensor_type == 'T'):
            self.instrument.write('SENSE:TEMPERATURE:TRANSDUCER TCOUPLE, (@%d)' % self.chno)
            self.instrument.write('SENSE:TEMPERATURE:TCOUPLE:TYPE %s, (@%d)' % (sensor_type,
                                                                                self.chno))
            self.instrument.write('SENSE:TEMPERATURE:TCOUPLE:RJUNCTION:RSELECT INTERNAL, (@%d)' % self.chno)
        else:
            raise ValueError()
        self.instrument.write('SENSE:TEMPERATURE:NPLCYCLES 1, (@%d)' % self.chno)
        self.instrument.write('SENSE:TEMPERATURE:LINE:SYNC ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:TEMPERATURE:AZERO:STATE ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:TEMPERATURE:ODETECTOR ON, (@%d)' % self.chno)
        self.instrument.write('SENSE:TEMPERATURE:AVERAGE:COUNT 10, (@%d)' % self.chno)
        self.instrument.write('SENSE:TEMPERATURE:AVERAGE:TCONTROL REPEAT, (@%d)' % self.chno)
        self.instrument.write('SENSE:TEMPERATURE:AVERAGE:STATE ON, (@%d)' % self.chno)

    @property
    def temperature(self)->float:
        self.instrument.write('ROUTE:CHANNEL:CLOSE (@%d)' % self.chno)
        self.device.wai()
        return float(self.instrument.ask('MEASURE:TEMPERATURE?'))

class DAQ6510(ScpiCommonCommands):
    def __init__(self, addr)->None:
        self.instrument = vxi11.Instrument(addr)
        if not self.idn().startswith('KEITHLEY INSTRUMENTS,MODEL DAQ6510'):
            raise WrongInstrumentException()
        self.rst()

    def watch(self, chno:int):
        self.instrument.write('DISPLAY:WATCH:CHANNELS (@%d)' % chno)

    def get_voltage_channel(self, chno:int):
        return DAQ6510VChannel(self, chno)

    def get_current_channel(self, chno:int):
        return DAQ6510IChannel(self, chno)

    def get_temperature_channel(self, chno:int, sensor_type:str):
        return DAQ6510TChannel(self, chno, sensor_type)
