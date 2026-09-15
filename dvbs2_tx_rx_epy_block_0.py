import numpy as np
from gnuradio import gr
import time


class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(
            self,
            name='Pluto Input Rate Monitor',
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )

        self.last = time.time()
        self.count = 0

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out0 = output_items[0]

        n = min(len(in0), len(out0))
        out0[:n] = in0[:n]

        self.count += n
        now = time.time()

        if now - self.last >= 1.0:
            dt = now - self.last
            rate = self.count / dt
#            print(f"Pluto input rate: {rate:.0f} samples/s", flush=True)
            self.count = 0
            self.last = now

        return n
