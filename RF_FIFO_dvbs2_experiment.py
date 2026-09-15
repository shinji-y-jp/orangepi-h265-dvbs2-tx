#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: DVB-S2 Tx/Rx Simulation
# Description: DVB-S2 Loopback Tx/Rx Simulation
# GNU Radio version: 3.10.12.0

from gnuradio import blocks
import pmt
from gnuradio import dtv
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
from math import pi, sqrt
import dvbs2_tx_rx_epy_block_0 as epy_block_0  # embedded python block
import threading

class dvbs2_tx_rx(gr.top_block):

    def __init__(self, agc_gain=1, agc_rate=(1e-5), agc_ref=1, att=10.0, debug=0, frame_size='normal', freq=1298000000, freq_offset=1000, gold_code=0, in_file='data/out_800x480_av_mp2.ts', modcod='QPSK1/4', pl_freq_est_period=20, rolloff=0.2, rrc_delay=25, rrc_nfilts=128, snr=10, sps=4, sym_rate=333000, sym_sync_damping=1.0, sym_sync_loop_bw=0.0045):
        gr.top_block.__init__(self, "DVB-S2 Tx/Rx Simulation", catch_exceptions=True)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.agc_gain = agc_gain
        self.agc_rate = agc_rate
        self.agc_ref = agc_ref
        self.att = att
        self.debug = debug
        self.frame_size = frame_size
        self.freq = freq
        self.freq_offset = freq_offset
        self.gold_code = gold_code
        self.in_file = in_file
        self.modcod = modcod
        self.pl_freq_est_period = pl_freq_est_period
        self.rolloff = rolloff
        self.rrc_delay = rrc_delay
        self.rrc_nfilts = rrc_nfilts
        self.snr = snr
        self.sps = sps
        self.sym_rate = sym_rate
        self.sym_sync_damping = sym_sync_damping
        self.sym_sync_loop_bw = sym_sync_loop_bw

        ##################################################
        # Variables
        ##################################################
        self.esn0_db = esn0_db = snr
        self.code_rate = code_rate = modcod.upper().replace("8PSK", "").replace("QPSK", "")
        self.EsN0 = EsN0 = 10 ** (esn0_db / 10)
        self.Es = Es = 1
        self.samp_rate = samp_rate = (int(sym_rate * sps))
        self.plheader_len = plheader_len = 90
        self.plframe_len = plframe_len = 33282
        self.pilot_len = pilot_len = int((360-1)/16)*36
        self.n_rrc_taps = n_rrc_taps = int(2*rrc_delay*sps) + 1
        self.constellation = constellation = modcod.replace(code_rate, "")
        self.N0 = N0 = Es / EsN0
        modcod_map = {
            "QPSK1/4": (dtv.MOD_QPSK, dtv.C1_4),
            "QPSK1/2": (dtv.MOD_QPSK, dtv.C1_2),
            "QPSK3/4": (dtv.MOD_QPSK, dtv.C3_4),
            "8PSK3/5": (dtv.MOD_8PSK, dtv.C3_5),
            "8PSK2/3": (dtv.MOD_8PSK, dtv.C2_3),
        }

        mod, code = modcod_map.get(modcod.upper(), (dtv.MOD_QPSK, dtv.C1_4))

        ##################################################
        # Blocks
        ##################################################

        self.interp_fir_filter_xxx_0 = filter.interp_fir_filter_ccf((int(sps / 2)), firdes.root_raised_cosine(sps, samp_rate, sym_rate, rolloff, n_rrc_taps))
        self.interp_fir_filter_xxx_0.declare_sample_delay(0)
#        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('' if '' else iio.get_pluto_uri(), [True, True], 32768, False)
#        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('' if '' else iio.get_pluto_uri(192.168.2.1), [True, True], 32768, False)
        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32('usb:',[True, True],131072,False)
#        self.iio_pluto_sink_0 = iio.fmcomms2_sink_fc32(
#            iio.get_pluto_uri(),
#            [True, True],
#            32768,
#            False
#        )
        self.iio_pluto_sink_0.set_len_tag_key('')
        self.iio_pluto_sink_0.set_bandwidth(2000000)
#        self.iio_pluto_sink_0.set_frequency(freq)
#        self.iio_pluto_sink_0.set_frequency(float(freq))
        self.iio_pluto_sink_0.set_frequency(freq.real)
        self.iio_pluto_sink_0.set_samplerate(samp_rate)
        self.iio_pluto_sink_0.set_attenuation(0, 20.0)
        self.iio_pluto_sink_0.set_filter_params('Auto', '', 0, 0)
        self.epy_block_0 = epy_block_0.blk()        
        self.dtv_dvbs2_physical_cc_0 = dtv.dvbs2_physical_cc(
            dtv.FECFRAME_NORMAL,
            code,
            mod,
            dtv.PILOTS_ON,
# 20260725            dtv.PILOTS_OFF,
            0)
        self.dtv_dvbs2_modulator_bc_0 = dtv.dvbs2_modulator_bc(
            dtv.FECFRAME_NORMAL,
            code,
            mod,
            dtv.INTERPOLATION_OFF)
        self.dtv_dvbs2_interleaver_bb_0 = dtv.dvbs2_interleaver_bb(
            dtv.FECFRAME_NORMAL,
            code,
            mod)
        self.dtv_dvb_ldpc_bb_0 = dtv.dvb_ldpc_bb(
            dtv.STANDARD_DVBS2,
            dtv.FECFRAME_NORMAL,
            code,
            dtv.MOD_OTHER)
        self.dtv_dvb_bch_bb_0 = dtv.dvb_bch_bb(
            dtv.STANDARD_DVBS2,
            dtv.FECFRAME_NORMAL,
            code
            )
        self.dtv_dvb_bbscrambler_bb_0 = dtv.dvb_bbscrambler_bb(
            dtv.STANDARD_DVBS2,
            dtv.FECFRAME_NORMAL,
            code
            )
        self.dtv_dvb_bbheader_bb_0 = dtv.dvb_bbheader_bb(
        dtv.STANDARD_DVBS2,
        dtv.FECFRAME_NORMAL,
        code,
        dtv.RO_0_20,
        dtv.INPUTMODE_NORMAL,
        dtv.INBAND_OFF,
        168,
        4000000)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_char*1, '/tmp/in.ts', True, 0, 0)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_char*1, 'data/udp.out', False)
        self.blocks_file_sink_0.set_unbuffered(False)


        ##################################################
        # Connections
        ##################################################
# byte TS path
        self.connect((self.blocks_file_source_0, 0), (self.dtv_dvb_bbheader_bb_0, 0))

# DVB-S2 chain
        self.connect((self.dtv_dvb_bbheader_bb_0, 0), (self.dtv_dvb_bbscrambler_bb_0, 0))
        self.connect((self.dtv_dvb_bbscrambler_bb_0, 0), (self.dtv_dvb_bch_bb_0, 0))
        self.connect((self.dtv_dvb_bch_bb_0, 0), (self.dtv_dvb_ldpc_bb_0, 0))
        self.connect((self.dtv_dvb_ldpc_bb_0, 0), (self.dtv_dvbs2_interleaver_bb_0, 0))
        self.connect((self.dtv_dvbs2_interleaver_bb_0, 0), (self.dtv_dvbs2_modulator_bc_0, 0))
        self.connect((self.dtv_dvbs2_modulator_bc_0, 0), (self.dtv_dvbs2_physical_cc_0, 0))

# Pluto直前 monitor
        self.connect((self.dtv_dvbs2_physical_cc_0, 0), (self.interp_fir_filter_xxx_0, 0))
        self.connect((self.interp_fir_filter_xxx_0, 0), (self.epy_block_0, 0))
        self.connect((self.epy_block_0, 0), (self.iio_pluto_sink_0, 0))
       
    def get_agc_gain(self):
        return self.agc_gain

    def set_agc_gain(self, agc_gain):
        self.agc_gain = agc_gain

    def get_agc_rate(self):
        return self.agc_rate

    def set_agc_rate(self, agc_rate):
        self.agc_rate = agc_rate

    def get_agc_ref(self):
        return self.agc_ref

    def set_agc_ref(self, agc_ref):
        self.agc_ref = agc_ref

    def get_att(self):
        return self.att

    def set_att(self, att):
        self.att = att

    def get_debug(self):
        return self.debug

    def set_debug(self, debug):
        self.debug = debug

    def get_frame_size(self):
        return self.frame_size

    def set_frame_size(self, frame_size):
        self.frame_size = frame_size

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.iio_pluto_sink_0.set_frequency(self.freq)

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset

    def get_gold_code(self):
        return self.gold_code

    def set_gold_code(self, gold_code):
        self.gold_code = gold_code

    def get_in_file(self):
        return self.in_file

    def set_in_file(self, in_file):
        self.in_file = in_file

    def get_modcod(self):
        return self.modcod

    def set_modcod(self, modcod):
        self.modcod = modcod

    def get_pl_freq_est_period(self):
        return self.pl_freq_est_period

    def set_pl_freq_est_period(self, pl_freq_est_period):
        self.pl_freq_est_period = pl_freq_est_period

    def get_rolloff(self):
        return self.rolloff

    def set_rolloff(self, rolloff):
        self.rolloff = rolloff
        self.interp_fir_filter_xxx_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.rolloff, self.n_rrc_taps))

    def get_rrc_delay(self):
        return self.rrc_delay

    def set_rrc_delay(self, rrc_delay):
        self.rrc_delay = rrc_delay
        self.set_n_rrc_taps(int(2*self.rrc_delay*self.sps) + 1)

    def get_rrc_nfilts(self):
        return self.rrc_nfilts

    def set_rrc_nfilts(self, rrc_nfilts):
        self.rrc_nfilts = rrc_nfilts

    def get_snr(self):
        return self.snr

    def set_snr(self, snr):
        self.snr = snr
        self.set_esn0_db(self.snr)

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_n_rrc_taps(int(2*self.rrc_delay*self.sps) + 1)
        self.set_samp_rate(self.sym_rate * self.sps)
        self.interp_fir_filter_xxx_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate,      self.sym_rate, self.rolloff, self.n_rrc_taps))

    def get_sym_rate(self):
        return self.sym_rate

    def set_sym_rate(self, sym_rate):
        self.sym_rate = sym_rate
        self.set_samp_rate(self.sym_rate * self.sps)
        self.interp_fir_filter_xxx_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.rolloff, self.n_rrc_taps))

    def get_sym_sync_damping(self):
        return self.sym_sync_damping

    def set_sym_sync_damping(self, sym_sync_damping):
        self.sym_sync_damping = sym_sync_damping

    def get_sym_sync_loop_bw(self):
        return self.sym_sync_loop_bw

    def set_sym_sync_loop_bw(self, sym_sync_loop_bw):
        self.sym_sync_loop_bw = sym_sync_loop_bw

    def get_esn0_db(self):
        return self.esn0_db

    def set_esn0_db(self, esn0_db):
        self.esn0_db = esn0_db
        self.set_EsN0(10 ** (self.esn0_db / 10))

    def get_code_rate(self):
        return self.code_rate

    def set_code_rate(self, code_rate):
        self.code_rate = code_rate
        self.set_constellation(modcod.replace(self.code_rate, ""))

    def get_EsN0(self):
        return self.EsN0

    def set_EsN0(self, EsN0):
        self.EsN0 = EsN0
        self.set_N0(self.Es / self.EsN0)

    def get_Es(self):
        return self.Es

    def set_Es(self, Es):
        self.Es = Es
        self.set_N0(self.Es / self.EsN0)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.iio_pluto_sink_0.set_samplerate(self.samp_rate)
        self.interp_fir_filter_xxx_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.rolloff, self.n_rrc_taps))

    def get_plheader_len(self):
        return self.plheader_len

    def set_plheader_len(self, plheader_len):
        self.plheader_len = plheader_len

    def get_plframe_len(self):
        return self.plframe_len

    def set_plframe_len(self, plframe_len):
        self.plframe_len = plframe_len

    def get_pilot_len(self):
        return self.pilot_len

    def set_pilot_len(self, pilot_len):
        self.pilot_len = pilot_len

    def get_n_rrc_taps(self):
        return self.n_rrc_taps

    def set_n_rrc_taps(self, n_rrc_taps):
        self.n_rrc_taps = n_rrc_taps
        self.interp_fir_filter_xxx_0.set_taps(firdes.root_raised_cosine(self.sps, self.samp_rate, self.sym_rate, self.rolloff, self.n_rrc_taps))

    def get_constellation(self):
        return self.constellation

    def set_constellation(self, constellation):
        self.constellation = constellation

    def get_N0(self):
        return self.N0

    def set_N0(self, N0):
        self.N0 = N0



def argument_parser():
    description = 'DVB-S2 Loopback Tx/Rx Simulation'
    parser = ArgumentParser(description=description)
    parser.add_argument(
        "--agc-gain", dest="agc_gain", type=eng_float, default=eng_notation.num_to_str(float(1)),
        help="Set AGC gain [default=%(default)r]")
    parser.add_argument(
        "--agc-rate", dest="agc_rate", type=eng_float, default=eng_notation.num_to_str(float((1e-5))),
        help="Set AGC update rate [default=%(default)r]")
    parser.add_argument(
        "--agc-ref", dest="agc_ref", type=eng_float, default=eng_notation.num_to_str(float(1)),
        help="Set AGC's reference value [default=%(default)r]")
    parser.add_argument(
        "-j", "--att", dest="att", type=eng_float, default=eng_notation.num_to_str(float(10.0)),
        help="Set transmit attenation [default=%(default)r]")
    parser.add_argument(
        "-d", "--debug", dest="debug", type=intx, default=0,
        help="Set debugging level [default=%(default)r]")
    parser.add_argument(
        "-f", "--frame-size", dest="frame_size", type=str, default='normal',
        help="Set FECFRAME size [default=%(default)r]")
    parser.add_argument(
        "-z", "--freq", dest="freq", type=complex, default=1298000000,
        help="Set transmit frequency [default=%(default)r]")
    parser.add_argument(
        "--freq-offset", dest="freq_offset", type=eng_float, default=eng_notation.num_to_str(float(1000)),
        help="Set simulated carrier frequency offset in Hz [default=%(default)r]")
    parser.add_argument(
        "--gold-code", dest="gold_code", type=intx, default=0,
        help="Set Gold code [default=%(default)r]")
    parser.add_argument(
        "--in-file", dest="in_file", type=str, default='data/out_800x480_av_mp2.ts',
        help="Set path to input file containing an MPEG TS stream [default=%(default)r]")
    parser.add_argument(
        "-m", "--modcod", dest="modcod", type=str, default='QPSK1/4',
        help="Set MODCOD [default=%(default)r]")
    parser.add_argument(
        "--pl-freq-est-period", dest="pl_freq_est_period", type=intx, default=20,
        help="Set PL synchronizer's frequency estimation period in frames [default=%(default)r]")
    parser.add_argument(
        "-r", "--rolloff", dest="rolloff", type=eng_float, default=eng_notation.num_to_str(float(0.2)),
        help="Set rolloff factor [default=%(default)r]")
    parser.add_argument(
        "--rrc-delay", dest="rrc_delay", type=intx, default=25,
        help="Set RRC filter delay in symbol periods [default=%(default)r]")
    parser.add_argument(
        "--rrc-nfilts", dest="rrc_nfilts", type=intx, default=128,
        help="Set number of branches on the polyphase RRC filter [default=%(default)r]")
    parser.add_argument(
        "--snr", dest="snr", type=eng_float, default=eng_notation.num_to_str(float(10)),
        help="Set starting SNR in dB [default=%(default)r]")
    parser.add_argument(
        "-o", "--sps", dest="sps", type=eng_float, default=eng_notation.num_to_str(float(4)),
        help="Set oversampling ratio in samples per symbol [default=%(default)r]")
    parser.add_argument(
        "-s", "--sym-rate", dest="sym_rate", type=intx, default=333000,
        help="Set symbol rate in bauds [default=%(default)r]")
    parser.add_argument(
        "--sym-sync-damping", dest="sym_sync_damping", type=eng_float, default=eng_notation.num_to_str(float(1.0)),
        help="Set symbol synchronizer's damping factor [default=%(default)r]")
    parser.add_argument(
        "--sym-sync-loop-bw", dest="sym_sync_loop_bw", type=eng_float, default=eng_notation.num_to_str(float(0.0045)),
        help="Set symbol synchronizer's loop bandwidth [default=%(default)r]")
    return parser

import datetime
from datetime import timezone
import platform
import os

FREQ_MHZ = 1298.000
TX_ON_SEC = 180
TX_OFF_SEC = 60


def print_beacon_header():
    print("=" * 60)
    print("DVB-S2 EXPERIMENTAL BEACON")
    print("=" * 60)


def print_beacon_status_tx(options):
    now = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print_beacon_header()
    print(f"TIME (UTC)        : {now}")
    print(f"HOST              : {platform.node()}")
    print("-" * 60)
#    print(f"FREQUENCY         : {options.freq:.3f} MHz")
#    print(f"FREQUENCY         : {options.freq/1e6:.6f} MHz")
    print(f"FREQUENCY        : {float(getattr(options.freq, 'real', options.freq))/1e6:.6f} MHz")
    print(f"SYMBOL RATE       : {options.sym_rate} baud")
    print(f"MODCOD            : {options.modcod}")
    print(f"FRAME SIZE        : {options.frame_size}")
    print(f"ROLLOFF           : {options.rolloff}")
    print(f"SPS               : {options.sps}")
    print(f"AGC GAIN          : {options.agc_gain:.3f}")
    print(f"AGC RATE          : {options.agc_rate:.6f}")
    print("-" * 60)
    print("MODE              : HEADLESS CLI TX")
    print(f"TX CYCLE          : {TX_ON_SEC}s ON / {TX_OFF_SEC}s OFF")
    print("STATUS            : TRANSMIT")
    print("=" * 60)
    print()


def print_beacon_status_off():
    now = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print("=" * 60)
    print("DVB-S2 EXPERIMENTAL BEACON")
    print("=" * 60)
    print(f"TIME (UTC)        : {now}")
    print("-" * 60)
#    print(f"FREQUENCY         : {FREQ_MHZ:.3f} MHz")
    print("STATUS            : IDLE (TX OFF)")
    print(f"NEXT TX IN        : {TX_OFF_SEC} seconds")
    print("=" * 60)
    print()


def main(top_block_cls=dvbs2_tx_rx, options=None):
    if options is None:
        options = argument_parser().parse_args()

    tb = top_block_cls(agc_gain=options.agc_gain, agc_rate=options.agc_rate, agc_ref=options.agc_ref, att=options.att, debug=options.debug, frame_size=options.frame_size, freq=options.freq, freq_offset=options.freq_offset, gold_code=options.gold_code, in_file=options.in_file, modcod=options.modcod, pl_freq_est_period=options.pl_freq_est_period, rolloff=options.rolloff, rrc_delay=options.rrc_delay, rrc_nfilts=options.rrc_nfilts, snr=options.snr, sps=options.sps, sym_rate=options.sym_rate, sym_sync_damping=options.sym_sync_damping, sym_sync_loop_bw=options.sym_sync_loop_bw)

    # これで File Source が EOF になったら自然終了する
    try:
        print_beacon_status_tx(options)
        tb.run()
    finally:
        print_beacon_status_off()
        tb.stop()
        tb.wait()
        del tb
        
if __name__ == '__main__':
    main()
