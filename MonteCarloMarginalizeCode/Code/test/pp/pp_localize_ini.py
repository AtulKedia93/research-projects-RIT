#! /usr/bin/env python
# Example
#   /scripts/localize_ini.py --ifo-classifier review_test_data/4s/all_networks.json --event 0 --ini proto_4s.ini --sim-xml scripts/mdc.xml.gz --mc-file-settings here_mc_ranges --guess-snr 20 --duration 4
import json
import sys
import argparse
import RIFT.lalsimutils as lalsimutils
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--ifos",help="Space-separated list of IFO names, eg 'H1 L1 V1', to use for this event ")
parser.add_argument("--event")
parser.add_argument("--ini")
parser.add_argument("--sim-xml")
parser.add_argument("--guess-snr",type=float)
parser.add_argument("--mc-range-limits")
parser.add_argument("--mc-range-limits-snr-safety",type=float,default=8)
parser.add_argument("--duration",type=int)
opts = parser.parse_args()

#
ifos =None

# Get IFOs for it
with open(opts.ifo_classifier,'r') as f:
    dat_ifos = json.load(f)
    ifos  = dat_ifos[opts.event] 

# Get event time from saved event object
# sim-xml only has one event remember
P=lalsimutils.xml_to_ChooseWaveformParams_array(opts.sim_xml)[0]

# open mc file
line = None
mc_range=eval(opts.mc_range.replace(' ', '')) # completely eliminate whitespace
snr_cut= float(snr_cut)

with open(opts.ini,'r') as f:
    line = f.readline()

    print_explode=False
    while line:
     if line.startswith('ifos='):
        print('ifos={}'.format(ifos))
     elif 'cip-explode-jobs' in line: #.startswith('cip-explode-jobs'):
        print(line.rstrip(), print_explode,file=sys.stderr)
        if not(print_explode):
           print('cip-explode-jobs-auto=True')  # basically always do this, override proto settings which were not well chosen
           print_explode=True
     elif opts.guess_snr > 37.5 and line.startswith('internal-ile-auto-logarithm-offset'):
         True # Don't use the logarithm offset when lnL is active for ILE
     elif line.startswith('internal-ile-sky-network-coordinates'):
        True # skip this line, set with IFO list at end
     else:
        clean_line = line.strip()
        if (clean_line):
          print(clean_line)
     line  = f.readline()

print("force-hint-snr={}".format(opts.guess_snr))
if opts.guess_snr<snr_cut:
    print("force-mc-range={}".format(mc_range))
else:
    print("limit-mc-range={}".format(mc_range))

sky_printed=False
# Try to set most of the high-SNR options here. Distance marginalization will be left to the top-level script
if opts.guess_snr>37.5:
    print("use-downscale-early=True")
    print("internal-ile-use-lnL=True")
    print("internal-ile-sky-network-coordinates=True")
    print("cip-sigma-cut=0.7")
    sky_printed=True
if opts.guess_snr>100:
    print("internal-cip-use-lnL=True")
    print("internal-ile-rotate-phase=True")
    print("ile-sampler-method=GMM")
if len(ifos) == 2 and not sky_printed:
    print("internal-ile-sky-network-coordinates=True")
print("event-time={}".format(P.tref))