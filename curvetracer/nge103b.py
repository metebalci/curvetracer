# SPDX-FileCopyrightText: 2024 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Type, Tuple

import vxi11

from .common import WrongInstrumentException
from .common import PSChannel, ScpiCommonCommands

class NGE103BChannel(PSChannel):
    def __init__(self, device, chno:int)->None:
        self.device = device
        self.instrument = device.instrument
        if chno < 1 or chno > 3:
            raise ValueError()
        self.chno = chno

    def __get_vc(self)->Tuple[float, float]:
        self.instrument.write('INSTRUMENT:NSELECT %d' % self.chno)
        apply_answer = self.instrument.ask('APPLY?')
        if apply_answer[0] == '"':
            apply_answer = apply_answer[1:]
        if apply_answer[-1] == '"':
            apply_answer = apply_answer[:-1]
        apply_answer = apply_answer.split(',')
        if len(apply_answer) == 2:
            voltage = float(apply_answer[0].strip())
            current = float(apply_answer[1].strip())
            return (voltage, current)
        else:
            return None

    def __set_vc(self, vc:Tuple[float, float])->None:
        voltage, current = vc
        self.instrument.write('INSTRUMENT:NSELECT %d' % self.chno)
        self.instrument.write('APPLY "%2.2f,%1.3f"' % (voltage, current))

    @property
    def voltage(self)->float:
        voltage, current = self.__get_vc()
        return voltage

    @voltage.setter
    def voltage(self, v:float)->None:
        voltage, current = self.__get_vc()
        self.__set_vc((v, current))
        self.device.wai()

    @property
    def current(self)->float:
        voltage, current = self.__get_vc()
        return current

    @current.setter
    def current(self, v:float)->None:
        voltage, current = self.__get_vc()
        self.__set_vc((voltage, v))
        self.device.wai()

    @property
    def state(self)->bool:
        self.instrument.write('INSTRUMENT:NSELECT %d' % self.chno)
        v = self.instrument.ask('OUTPUT:STATE?')
        if v == '1' or v == 'ON':
            return True
        else:
            return False

    @state.setter
    def state(self, v:bool)->None:
        self.instrument.write('INSTRUMENT:NSELECT %d' % self.chno)
        if v:
            self.instrument.write('OUTPUT:STATE ON')
        else:
            self.instrument.write('OUTPUT:STATE OFF')
        self.device.wai()

class NGE103B(ScpiCommonCommands):
    def __init__(self, addr)->None:
        self.instrument = vxi11.Instrument(addr)
        if not self.idn().startswith('Rohde&Schwarz,NGE103B'):
            raise WrongInstrumentException()
        self.rst()

    def get_channel(self, chno:int)->Type[NGE103BChannel]:
        return NGE103BChannel(self, chno)

    def turn_all_channels_off(self)->None:
        self.instrument.write('OUTPUT:GENERAL OFF')
