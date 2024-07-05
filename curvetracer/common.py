# SPDX-FileCopyrightText: 2024 Mete Balci
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import List, Type, Tuple

class WrongInstrumentException(Exception):
    pass

class ConfigException(Exception):
    pass

class PSChannel:
    @property
    def voltage(self)->float:
        pass

    @voltage.setter
    def voltage(self, v:float)->None:
        pass

    @property
    def current(self)->float:
        pass

    @current.setter
    def current(self, v:float)->None:
        pass

    @property
    def state(self)->bool:
        pass

    @state.setter
    def state(self, v:bool)->None:
        pass

class DAQChannel:
    def open(self)->None:
        pass

    def close(self)->None:
        pass

class VChannel:
    @property
    def voltage(self)->float:
        pass

class IChannel:
    @property
    def current(self)->float:
        pass

class TChannel:
    @property
    def temperature(self)->float:
        pass

class ScpiCommonCommands:
    def idn(self)->str:
        return self.instrument.ask('*IDN?')

    def rst(self)->None:
        self.instrument.write('*RST')

    def wai(self)->None:
        self.instrument.write('*WAI')
