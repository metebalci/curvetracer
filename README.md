# curvetracer

curvetracer is a small Python program that can trace and generate output and transfer characteristics (curves) of JFETs using an LXI capable power supply and DAQ. 

It is assumed that the power supply has at least 2 channels with programmable voltage and current, and DAQ has at least 4 channels of which 2 are for voltage, 1 is for current and 1 is for thermocouple.

Depending on the characteristic requested, Vgs and/or Vds supply is programmed and Vds, Vgs, Id and thermocouple is measured when the JFET is powered. The measured data from the DAQ, not the programmed data of the power supply, is used as the data. This is also a double check. If measured Vgs or Vds is not within +-5% of requested Vgs or Vds, the measurement for these values is repeated.

The temperature of JFET is monitored using a thermocouple and the upper bound is limited to a configurable value (tmax). Additionally, the temperature of JFET is waited to go below a configurable value (tcon) before the trace of a curve is started. This is to eliminate the difference among traces due to thermal drift. However, some curves are by nature increase the temperature of device more than others, this is not controlled (other than tmax check).

Each measurement is made 3 times and the median is selected. This is to eliminate outliers that can happen due to stabilization need. To maximize the lifetime of relays in the DAQ, the power is set to off between measurements.

## extending hardware support

Only Rohde & Schwarz NGE103B and Keithley DAQ6510 with a 7700 Card are supported. Because these are the units I use and it is impossible for me to verify other hardware, I do not plan to add support for anything I do not have and/or use. However, adding support is not difficult. The program consists of the following modules:

- `common.py` and `curvetracer.py` are the core program files that are independent of hardware support.
- `nge103b.py` and `daq6510.py` are the hardware implementations. You have to create and implement similar files for different hardware.
- `__main__.py` contains the entry point. When you add support for new hardware, you need to add proper support to use your implementation.

In the existing implementation, all DAQ6510 channels are configured with:

- NPLCYCLES 1
- LINE SYNC ON
- AUTOZERO ON
- AVERAGE COUNT 10
- AVERAGE TYPE REPEAT

and the INTERNAL reference junction is used for thermocouple channel.

# requirements

```
pip install python-vxi11 matplotlib scipy

```

# usage

First clone the repo and install the requirements.

Run as a module with `python -m curvetracer`.

## config file

A config file is required to generate output and transfer characteristic. A [sample.config](https://github.com/metebalci/curvetracer/blob/main/sample.config) is provided with comments.

## output characteristic (Id vs. Vds)

Using a config file, the output characteristic data is generated with:

```
python -m curvetracer -c <config_file> oc
```

On a successful run, this creates <device_name_in_config>.oc file containing the data.

## transfer characteristic (Id vs. Vgs)

Similar to output characteristic:

```
python -m curvetracer -c <config_file> oc
```

On a successful run, this creates <device_name_in_config>.tc file containing the data.

## plot

oc and tc data files can be plotted with this command:

```
python -m curvetracer -i <oc_or_tc_file_name> plot
```

The files already contain the device name and the type of data. 

If `-o <output_file>` option is given, the plot is saved to output file rather than displaying it.

If `-t` option is given, the temperature measurements are also shown on the transfer characteristic plot in the same color with a dotted line.

# example: InterFET J212

![J212 Setup](https://raw.githubusercontent.com/metebalci/curvetracer/main/J212.setup.jpg)

Data generated with an InterFET J212 (J212.config is not part of the repository):

```
python -m curvetracer -c J212.config tc
python -m curvetracer -c J212.config oc
```

Transfer characteristic at Vds=15V:

```
python -m curvetracer -i J212.tc -o J212.tc.png plot
```

![J212 Transfer Characteristic](https://raw.githubusercontent.com/metebalci/curvetracer/main/J212.tc.png)

with temperature data:

```
python -m curvetracer -i J212.tc -t -o J212.tc.temp.png plot
```

![J212 Transfer Characteristic](https://raw.githubusercontent.com/metebalci/curvetracer/main/J212.tc.temp.png)

Output characteristic at different Vgs values:

```
python -m curvetracer -i J212.oc -o J212.oc.png plot
```

![J212 Output Characteristic](https://raw.githubusercontent.com/metebalci/curvetracer/main/J212.oc.png)
