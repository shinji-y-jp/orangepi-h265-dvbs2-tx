# Orange Pi 3B H.265 DVB-S2 Transmitter

A simple, low-cost experimental **H.265 / HEVC DVB-S2 transmitter** using:

- Orange Pi 3B
- Rockchip RK3566
- Rockchip VPU H.265 hardware encoding
- FFmpeg / RKMPP
- GNU Radio
- gr-dvbs2
- Pluto / Pluto Plus
- Logitech C920

The goal of this project is simple:

> Build an affordable and reproducible H.265 DATV transmitter using a general-purpose SBC and open-source software.

This repository is intentionally **TX only**.

There is no receiver and no transceiver GUI.

The design philosophy is:

> **KISS — Keep It Simple.**

---

# Current Status

H.265 hardware encoding and DVB-S2 RF transmission have been successfully demonstrated on the Orange Pi 3B.

Current working signal path:

```text
Logitech C920
    |
    | H.264
    v
Orange Pi 3B
Rockchip RK3566
    |
    | FFmpeg / ffmpeg-rockchip
    | Rockchip VPU
    | H.265 / HEVC hardware encoding
    v
MPEG Transport Stream
    |
    | FIFO
    v
GNU Radio / gr-dvbs2
    |
    v
Pluto / Pluto Plus
    |
    v
DVB-S2 RF
```

This is an **early experimental release** intended for practical testing and community experimentation.

Feedback and test reports are welcome.

---

# Why Orange Pi 3B?

The Orange Pi 3B is not being used because it has the fastest CPU.

The main reason is the Rockchip RK3566 VPU.

The important feature for this project is:

```text
H.265 / HEVC hardware encoding
```

Instead of performing HEVC encoding entirely on the CPU, the video compression task is handled by dedicated video hardware.

For low-cost DATV experiments:

```text
Low-cost SBC
+
H.265 hardware encoder
+
GNU Radio
+
Pluto
=
Experimental H.265 DVB-S2 transmitter
```

---

# Hardware

Reference test configuration:

```text
Orange Pi 3B
Rockchip RK3566
2 GB RAM

Logitech C920 USB webcam

Pluto / Pluto Plus
```

Other configurations may work, but they have not necessarily been tested.

---

# Software

The transmitter uses:

```text
64-bit Linux
GNU Radio
gr-dvbs2
FFmpeg
ffmpeg-rockchip
Rockchip MPP / RKMPP
Python 3
libiio
libad9361
```

The H.265 encoder used by FFmpeg is:

```text
hevc_rkmpp
```

Check it with:

```bash
/home/orangepi/ffmpeg-rockchip/ffmpeg -encoders | grep rkmpp
```

---

# Basic Operation

Main transmitter script:

```text
h265_tx.sh
```

Usage:

```bash
./h265_tx.sh FREQUENCY MODCOD SYMBOL_RATE OSR
```

Example:

```bash
./h265_tx.sh 2400000000 QPSK3/4 333000 2
```

This means:

```text
Frequency   : 2400 MHz
MODCOD      : QPSK 3/4
Symbol Rate : 333 kSym/s
OSR         : 2
```

---

# Representative Commands

## 2400 MHz / 333 kSym/s

```bash
# 2400MHz / QPSK3/4 / 333kS/s / OSR2
./h265_tx.sh 2400000000 QPSK3/4 333000 2

# 2400MHz / QPSK1/2 / 333kS/s / OSR2
./h265_tx.sh 2400000000 QPSK1/2 333000 2

# 2400MHz / QPSK1/4 / 333kS/s / OSR2
./h265_tx.sh 2400000000 QPSK1/4 333000 2

# 2400MHz / 8PSK3/5 / 333kS/s / OSR2
./h265_tx.sh 2400000000 8PSK3/5 333000 2
```

## 438 MHz / 333 kSym/s

```bash
# 438MHz / QPSK3/4 / 333kS/s / OSR2
./h265_tx.sh 438000000 QPSK3/4 333000 2

# 438MHz / QPSK1/2 / 333kS/s / OSR2
./h265_tx.sh 438000000 QPSK1/2 333000 2

# 438MHz / QPSK1/4 / 333kS/s / OSR2
./h265_tx.sh 438000000 QPSK1/4 333000 2
```

---

# Experimental 125 kSym/s Commands

```bash
# 438MHz / QPSK1/2 / 125kS/s / OSR2
./h265_tx.sh 438000000 QPSK1/2 125000 2

# 438MHz / QPSK1/4 / 125kS/s / OSR2
./h265_tx.sh 438000000 QPSK1/4 125000 2

# 2400MHz / QPSK1/2 / 125kS/s / OSR2
./h265_tx.sh 2400000000 QPSK1/2 125000 2

# 2400MHz / QPSK1/4 / 125kS/s / OSR2
./h265_tx.sh 2400000000 QPSK1/4 125000 2
```

## Important Note for 125 kSym/s

The current reference `h265_tx.sh` uses:

```text
Video bitrate : 300 kbit/s
TS muxrate    : 505 kbit/s
```

These values are intended for the current 333 kSym/s experiments.

They are too high for many 125 kSym/s configurations, especially QPSK 1/4.

For 125 kSym/s experiments, the following may need to be reduced:

```text
Resolution
Frame rate
H.265 video bitrate
MPEG-TS muxrate
```

Therefore:

```text
333 kSym/s = current reference configuration

125 kSym/s = experimental super-narrow DATV configuration
```

---

# h265_tx.sh

```bash
#!/usr/bin/env bash

FIFO="/tmp/in.ts"
CAM="/dev/video0"

FREQ="${1:-2400000000}"
MODCOD="${2:-QPSK3/4}"
SYMRATE="${3:-333000}"
OSR="${4:-2}"

FFMPEG="/home/orangepi/ffmpeg-rockchip/ffmpeg"
DVBS2="./RF_FIFO_dvbs2_experiment.py"

cleanup()
{
    echo
    echo "Stopping..."

    [[ -n "${FFMPEG_PID:-}" ]] && kill "${FFMPEG_PID}" 2>/dev/null || true
    [[ -n "${TX_PID:-}" ]] && kill "${TX_PID}" 2>/dev/null || true

    rm -f "${FIFO}"
}

trap cleanup EXIT INT TERM

fuser -k /dev/video0 2>/dev/null || true

rm -f "${FIFO}"
mkfifo "${FIFO}"

echo "Orange Pi 3B H.265 DVB-S2 TX"
echo "FREQ    = ${FREQ}"
echo "MODCOD  = ${MODCOD}"
echo "SR      = ${SYMRATE}"
echo "OSR     = ${OSR}"

# --------------------------------------------------
# C920 H.264
#       ->
# Rockchip VPU H.265 / HEVC
#       ->
# MPEG Transport Stream
#       ->
# FIFO
# --------------------------------------------------

"${FFMPEG}" \
    -y \
    -hide_banner \
    -loglevel warning \
    -f v4l2 \
    -input_format h264 \
    -video_size 800x448 \
    -framerate 15 \
    -i "${CAM}" \
    -c:v hevc_rkmpp \
    -b:v 300k \
    -an \
    -muxrate 505k \
    -muxdelay 0 \
    -muxpreload 0 \
    -fflags +genpts \
    -mpegts_flags +resend_headers \
    -f mpegts \
    "${FIFO}" &

FFMPEG_PID=$!

sleep 1

# --------------------------------------------------
# GNU Radio DVB-S2 TX
# --------------------------------------------------

"${DVBS2}" \
    -z "${FREQ}" \
    -m "${MODCOD}" \
    -s "${SYMRATE}" \
    -o "${OSR}" &

TX_PID=$!

wait "${TX_PID}"
```

Make it executable:

```bash
chmod +x h265_tx.sh
```

---

# Video Processing

The Logitech C920 provides an H.264 video stream.

The Orange Pi 3B converts this to H.265 / HEVC using the RK3566 VPU.

```text
C920
 |
 | H.264
 v
FFmpeg
 |
 v
Rockchip RK3566 VPU
 |
 | hevc_rkmpp
 v
H.265 / HEVC
 |
 v
MPEG-TS
```

The C920 is the current reference camera.

Other cameras may work but are not part of the tested reference configuration.

---

# DVB-S2 Processing

The MPEG Transport Stream is written to:

```text
/tmp/in.ts
```

as a FIFO.

The GNU Radio transmitter reads the FIFO using:

```text
RF_FIFO_dvbs2_experiment.py
```

Complete data path:

```text
Logitech C920
      |
      v
FFmpeg / RKMPP
      |
      v
H.265
      |
      v
MPEG-TS
      |
      v
/tmp/in.ts
      |
      v
GNU Radio
      |
      v
gr-dvbs2
      |
      v
Pluto / Pluto Plus
      |
      v
DVB-S2 RF
```

---

# MODCOD

Currently tested or used experimentally:

```text
QPSK 1/4
QPSK 1/2
QPSK 3/4
8PSK 3/5
```

Not every possible combination of:

```text
MODCOD
Symbol Rate
Video Bitrate
Mux Rate
OSR
```

has been tested.

---

# Symbol Rates

Current experiments include:

```text
333 kSym/s
125 kSym/s
```

333 kSym/s is the current reference operating point.

125 kSym/s is being investigated for very narrow DATV experiments.

---

# Frequencies

Current laboratory experiments include:

```text
438 MHz
2400 MHz
```

Examples:

```bash
./h265_tx.sh 438000000 QPSK1/2 333000 2
```

```bash
./h265_tx.sh 2400000000 QPSK1/2 333000 2
```

---

# Environment Setup

Update the package list:

```bash
sudo apt update
```

Install the basic GNU Radio / Pluto development environment:

```bash
sudo apt install -y \
build-essential \
cmake \
pkg-config \
git \
wget \
curl \
python3 \
python3-pip \
python3-numpy \
python3-mako \
python3-yaml \
python3-click \
python3-click-plugins \
libboost-all-dev \
libfftw3-dev \
libgmp-dev \
libusb-1.0-0-dev \
libudev-dev \
liborc-0.4-dev \
libspdlog-dev \
doxygen \
graphviz \
libpcap-dev \
gnuradio \
gnuradio-dev \
libiio-dev \
libiio-utils \
python3-libiio \
libad9361-dev
```

Check the CPU architecture:

```bash
uname -m
```

Expected result:

```text
aarch64
```

---

# Rockchip MPP

This project uses Rockchip MPP / RKMPP for hardware video processing.

Source:

```text
https://github.com/rockchip-linux/mpp
```

The tested Orange Pi system used Rockchip MPP together with a Rockchip-enabled FFmpeg build.

On small SBCs, a conservative build such as:

```bash
make -j1
```

may be preferable if parallel builds cause memory or stability problems.

---

# ffmpeg-rockchip

The Rockchip-compatible FFmpeg implementation used for the H.265 experiment is:

```text
https://github.com/nyanmisaka/ffmpeg-rockchip
```

Check available RKMPP encoders:

```bash
/home/orangepi/ffmpeg-rockchip/ffmpeg -encoders | grep rkmpp
```

The H.265 encoder should include:

```text
hevc_rkmpp
```

---

# gr-dvbs2

The DVB-S2 transmitter uses:

```text
https://github.com/drmpeg/gr-dvbs2
```

Example installation:

```bash
cd ~

mkdir -p src
cd ~/src

git clone https://github.com/drmpeg/gr-dvbs2.git

cd gr-dvbs2

mkdir -p build
cd build

cmake ..
make -j1

sudo make install
sudo ldconfig
```

---

# Pluto Check

Check whether Pluto / Pluto Plus is visible:

```bash
iio_info -s
```

The SDR should appear before starting the transmitter.

---

# Camera Check

List video devices:

```bash
v4l2-ctl --list-devices
```

Check camera formats:

```bash
v4l2-ctl -d /dev/video0 --list-formats-ext
```

Current reference input:

```text
Device      : /dev/video0
Format      : H.264
Resolution  : 800x448
Frame rate  : 15 fps
```

---

# Repository Files

A minimal TX-only repository can contain:

```text
README.md
LICENSE
h265_tx.sh
RF_FIFO_dvbs2_experiment.py
RF_FIFO_dvbs2_experiment.grc
```

Optional files may include:

```text
screenshots
test logs
installation notes
low-symbol-rate scripts
```

There is intentionally no DVB-S2 receiver code in this repository.

---

# KISS Design Philosophy

The basic rule is:

```text
One SBC
One SDR
One primary task
```

For this repository:

```text
Orange Pi 3B = H.265 DVB-S2 transmitter
```

The receiver can run on another SBC or computer.

This keeps the transmitter easy to:

```text
understand
test
debug
modify
port
maintain
```

---

# Hardware Is Replaceable

Today's platform is:

```text
Orange Pi 3B
Rockchip RK3566
```

Future SBCs will change.

They may include newer and more efficient video hardware.

The reusable foundation is:

```text
Linux
GNU Radio
FFmpeg
gr-dvbs2
Git
GitHub
Open Source
Code
Knowledge
Measurements
Reproducible results
```

The SBC is replaceable.

The knowledge remains.

---

# Project Scope

This repository is specifically intended for:

> **Low-cost H.265 / HEVC DVB-S2 transmission experiments using Orange Pi 3B.**

The emphasis is:

```text
Affordable hardware
Open source
Reproducibility
Real RF testing
Low symbol rates
Practical experimentation
```

It is not intended to replace existing DATV systems.

It is another experimental approach.

---

# Early Release

This repository is intentionally being published before development of a complete Orange Pi DATV transceiver.

A complete transceiver is not required to make the H.265 transmitter useful.

The first goal is:

```text
Orange Pi 3B
+
H.265 hardware encoding
+
GNU Radio DVB-S2
+
Pluto
=
Working RF transmitter
```

That goal has been demonstrated.

Future development may include:

```text
Lower bitrate H.265 profiles
Additional symbol rates
Audio
Automatic bitrate selection
Improved scripts
GUI
Receiver integration
Other SBCs
```

These are not required for the first release.

---

# RF Notice

This project can generate real RF signals.

Users are responsible for complying with all applicable:

```text
Amateur radio regulations
Licence conditions
Frequency allocations
Bandwidth limits
Emission requirements
Power limits
```

Use a dummy load, attenuator, shielded setup, or other appropriate laboratory arrangement when required.

Do not transmit on frequencies for which you are not authorized.

---

# Credits

This project builds on existing open-source software.

Particular thanks go to the developers and contributors of:

```text
GNU Radio
gr-dvbs2
Rockchip MPP
ffmpeg-rockchip
FFmpeg
libiio
```

The DVB-S2 modulation technology itself was not invented by this project.

The purpose of this project is integration:

```text
Orange Pi 3B
+
Rockchip H.265 hardware encoding
+
GNU Radio DVB-S2
+
Pluto
```

into a simple, affordable and reproducible experimental DATV transmitter.

---

# Result

```text
Orange Pi 3B
+
Rockchip RK3566 VPU
+
H.265 / HEVC hardware encoding
+
GNU Radio
+
gr-dvbs2
+
Pluto / Pluto Plus
=
WORKS
```

That is enough for the first release.

---

# License

This project is licensed under the GNU General Public License version 3 or any later version.

See the `LICENSE` file for the complete license text.

---

# Author

Shinji Yamazaki

2026

73,

Shinji
