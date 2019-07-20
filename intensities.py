"""Demo for packing DHGR pixels in such a way that colours cancel."""

import random

import numpy as np

SEEDS = (0, 1, 4, 5, 10, 11, 14, 15)

def intensities():
    clock = [False, False, False, False]

    def _seed(val, offset):
        clock[offset] = val & 0b1

    transitions = {
        # 0123012301230123
        # 0000111100001111
        0: {0, 3},
        # 0123012301230123
        # 0001111000011110
        1: {2, 3},
        # 010010110100
        4: {2, 3},
        # 010110100
        5: {0, 3},
        # 012301230123
        # 1010010110100
        10: {3, 0},
        # 012301230123
        # 101101001011
        11: {2, 3},
        # 1230123
        # 11100001111000011110
        14: {2, 3},
        # 11110000
        15: {0, 3},
    }

    intensities = np.zeros((16, 2), dtype=np.float64)

    for seed in SEEDS:
        for run_size in (0, 1):
            phase = 0

            s = seed
            _seed(s, 3)
            s >>= 1

            _seed(s, 2)
            s >>= 1

            _seed(s, 1)
            s >>= 1

            _seed(s, 0)
            s >>= 1

            run_count = 0

            row = np.zeros(8, dtype=np.bool)
            row[0:4] = clock

            for x in range(4, 8):
                # Find would-be next bit if we repeat the same colour
                next_bit = clock[phase]

                run_count += 1
                if run_count == (run_size + 1):
                    next_bit = 1 - next_bit
                    run_count = 0
                clock[phase] = next_bit
                row[x] = next_bit

                phase += 1
                if phase == 4:
                    phase = 0
            print(row)
            for x in range(5):
                intensities[seed, run_size] = sum(row) / 8


    return intensities
