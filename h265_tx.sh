#!/usr/bin/env bash

FIFO="/tmp/in.ts"
CAM="/dev/video0"

FREQ="${1:-2400000000}"
MODCOD="${2:-QPSK3/4}"
SYMRATE="${3:-333000}"
OSR="${4:-4}"

FFMPEG="/home/orangepi/ffmpeg-rockchip/ffmpeg"
DVBS2="./RF_FIFO_dvbs2_experiment.py"

cleanup()
{
    echo
    echo "Stopping..."

    [[ -n "${FFMPEG_PID:-}" ]] && kill "${FFMPEG_PID}" 2>/dev/null
    [[ -n "${TX_PID:-}" ]] && kill "${TX_PID}" 2>/dev/null

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
# C920 H.264 -> Rockchip VPU -> H.265 -> MPEG-TS
# FIFO writerとして先に起動
# readerが開くまでここで待つので問題なし
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
