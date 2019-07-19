"""Demo for packing DHGR pixels in such a way that colours cancel."""

import random

import numpy as np

import colours

XMAX = 560
YMAX = 192


def pixel(clock):
    return "".join("01"[c] for c in clock)


def main():
    dhgr = np.zeros((YMAX, XMAX), dtype=np.bool)

    clock = [False, False, False, False]  # np.zeros(shape=4, dtype=np.bool)

    def _seed(val, offset):
        dhgr[y, offset] = val & 0b1
        clock[offset] = val & 0b1

    for y in range(YMAX):
        phase = 0

        seed = [10, 2, 6, 4][y % 4]  # y//(192//16) # random.randint(0, 16)
        # seed = 0b1101
        # seed = 0b1101 # random.randint(0, 16)

        # seed = y % 16

        seed = y // (192 // 16)

        # TODO: why do 2,3,6,7,8,9,12,13 give colours?
        seed = random.choice((0, 1, 4, 5, 10, 11, 14, 15))

        # 0000 & clock = 1 or 3
        # 0001 & clock = 1 or 3
        # 0100 & clock = 1 or 3
        # 0101 & clock = 1 or 3
        # 1010 & clock = 2 or 4
        # 1011 & clock = 2 or 4
        # 1110 &
        # 1111

        # seed = [0, 1, 4, 5, 10, 11, 14, 15][y // (192 // 8)]
        # seed = 4

        transitions = {
            # 0123012301230123
            # 0000111100001111
            0: {0, 3},
            # 0123012301230123
            # 0001111000011110
            1: {2, 3},  # XXX 2 3
            # 0010
            # 2: {},
            3: {2, 3},
            # 010010110100
            4: {2, 3},  # XXX 2 3
            # 010110100
            5: {0, 3},
            # 6: {},
            # 7: {},
            # 8: {},
            # 9: {},
            # 012301230123
            # 1010010110100
            10: {3, 0},
            # 012301230123
            # 101101001011
            11: {2, 3},  # XXX 2 3
            # 1230123
            # 11100001111000011110
            # 12: {},
            # 13: {},
            14: {2, 3},  # XXX 0 3
            # 11110000
            15: {0, 3},
        }

        tr = list(transitions[seed])

        # seed = 0  # 0000111100001111 phase 0,3 - first and last in run of 0
        # or 1 bits
        # seed = 1  # 00011110000111100001  phase 2,3
        # seed = 4  # 010010110100  phase 2,3
        # seed = 5  # 010110100 phase 0,3
        # seed = 15
        # seed = 2

        _seed(seed, 3)
        seed >>= 1

        _seed(seed, 2)
        seed >>= 1

        _seed(seed, 1)
        seed >>= 1

        _seed(seed, 0)
        seed >>= 1

        # print(pixel(clock))

        print()
        run_size = random.randint(1, 2)

        # flip_positions = set(random.randint(0, 139) * 4 + random.randint(2,3)
        #                      for _ in range(4))

        flip_positions = set(y * 4 + tr[0] for y in range(140))
        flip_positions.update(set(y * 4 + tr[1] for y in range(140)))
        flip_positions = {random.choice(list(flip_positions)) for _ in range(1)}
        # XXX ok to flip on phase 2,3 for this seed - why?

        # flip_positions = {random.choice([10, 11, 14, 15, 18, 19])}
        run_count = 0
        do_print = False

        for x in range(4, XMAX):
            # Find would-be next bit if we repeat the same colour
            next_bit = clock[phase]

            # run_size += 1
            # flip = random.randint(0, 1)
            # if run_size == (y % 2) + 1:
            #     # Have to terminate run or we'd accumulate colour
            #     next_bit = ~next_bit
            #     # if run_size == 1:
            #     #     print("Max run size")
            #     # elif flip:
            #     #     print("Terminating early")
            #     run_size = 0
            # else:
            #     print("Carrying on")

            # run_length = (y % (192 // 8)) + 1
            #
            # if x % run_length != 0:
            #     next_bit = ~next_bit

            # Can slip a bit if clock is 0000, 0101, 1010, 1111
            # if (
            #         (clock == [0, 1, 0, 1] or clock == [0, 1, 0, 1])
            # ) or (
            #         (clock == [1, 0, 1, 0] or clock == [1, 1, 1, 1])
            # ):

            #            if x not in flip_positions:
            if phase not in tr:
                # if random.randint(0, 5) == 0 and (
                #     clock == [1,1,1,0] or
                #     clock == [0,0,0,0] or clock == [1,1,1,1] or clock == [0,0,0,1]
                # ):
                # if not next_bit and random.randint(0, 5) == 0:
                run_count += 1
                if run_count == run_size:
                    next_bit = 1 - next_bit
                    run_count = 0
                clock[phase] = next_bit
            else:
                next_clock = clock
                next_clock[phase] = 1 - next_bit
                next_seed = (next_clock[3]) + (next_clock[2] << 1) + (
                        next_clock[1] << 2) + (next_clock[0] << 3)
                if next_seed in transitions and random.randint(0, 5) == 0:
                    next_bit = 1 - next_bit
                    run_size = 3 - run_size
                    run_count = 0

                    print(pixel(clock))
                    clock[phase] = next_bit
                    seed = (clock[3]) + (clock[2] << 1) + (clock[1] << 2) + \
                           (clock[0] << 3)
                    print(pixel(clock))

                    tr = list(transitions[seed])
                else:
                    run_count += 1
                    if run_count == run_size:
                        next_bit = 1 - next_bit
                        run_count = 0
                    clock[phase] = next_bit

            # else:
            #     next_bit = 1 - next_bit
            #     print("slipping")
            # print("not")

            # if x != y:
            #     next_bit = ~next_bit

            # if x % 2 == 0:
            #     next_bit = clock[phase]
            # else:
            #     next_bit = ~clock[phase]

            # print("01"[next_bit])
            dhgr[y, x] = next_bit

            if do_print:
                do_print = False
                print(pixel(clock))
                print(phase)
                print("New weight = %d" % sum(clock))
            phase += 1
            if phase == 4:
                phase = 0

        print(dhgr[y, 0:20])

    #            print(pixel(clock))

    # print(dhgr[0,0:12])
    memory = pack(dhgr)
    # print(memory[0,0])
    dump(memory)


# See "Apple Graphics & Game Design", p95
def y_to_addr_base(y):
    a = y // 64
    d = y - 64 * a
    b = d // 8
    c = d - 8 * b

    return 1024 * c + 128 * b + 40 * a


X_Y_TO_PAGE = np.zeros((YMAX, XMAX), np.uint8)
X_Y_TO_OFFSET = np.zeros((YMAX, XMAX), np.uint8)

for y in range(YMAX):
    for x in range(XMAX):
        addr = y_to_addr_base(y) + x

        page = addr // 256
        offset = addr - (page * 256)

        X_Y_TO_OFFSET[y, x] = offset
        X_Y_TO_PAGE[y, x] = page


def dump(memory):
    even = memory[:, ::2]
    odd = memory[:, 1::2]

    main = np.zeros(8192, dtype=np.uint8)
    aux = np.zeros(8192, dtype=np.uint8)

    for y in range(YMAX):
        for x in range(XMAX // 14):
            page = X_Y_TO_PAGE[y, x]
            offset = X_Y_TO_OFFSET[y, x]

            addr = page * 256 + offset

            aux[addr] = even[y, x]
            main[addr] = odd[y, x]

    with open("out", "wb") as out:
        out.write(main.tobytes())
        out.write(aux.tobytes())


def pack(dhgr):
    """Pack bitmap into 7-bit screen map"""

    memory = np.zeros((YMAX, XMAX // 7), dtype=np.uint8)

    for x in range(0, XMAX - 7, 7):
        memory[:, x // 7] = (
                dhgr[:, x] + (dhgr[:, x + 1] << 1) + (
                dhgr[:, x + 2] << 2) + (
                        dhgr[:, x + 3] << 3) + (dhgr[:, x + 4] << 4) + (
                        dhgr[:, x + 5] << 5) + (dhgr[:, x + 6] << 6))

    return memory


# 01230123012301230123
# 1011
#  0110 = 0011
#   1101 = 0111
#    1010 = 0101
#     0100 = 0100

if __name__ == "__main__":
    main()
