"""Demo for packing DHGR pixels in such a way that colours cancel."""

import glob
import os.path
import random

from PIL import Image
import numpy as np

XMAX = 560
YMAX = 192


def pixel(clock):
    return "".join("01"[c] for c in clock)


def get_bw_transitions(filename):
    im = Image.open(filename).resize((XMAX, YMAX)).convert("1")

    flip_transitions = [[] for _ in range(YMAX)]

    for y in range(YMAX):
        old_pixel = im.getpixel((0, y))
        for x in range(XMAX):
            current_pixel = im.getpixel((x, y))
            if old_pixel != current_pixel:
                flip_transitions[y].append((x, current_pixel != 0))
                # print("Line %d transition at %d (%d -> %d)" % (
                #    y, x, old_pixel, current_pixel))
            old_pixel = current_pixel

    return flip_transitions


OUTPUT_DIR = "hackfest/hackfest/files"


def main():
    for filename in glob.glob("images/*.png"):
        flip_transitions = get_bw_transitions(filename)

        dhgr = render(flip_transitions)

        memory = pack(dhgr)

        base_filename = ".".join(
            os.path.basename(filename).split(".")[:-1] + ["bin"])
        output_filename = os.path.join(
            OUTPUT_DIR, base_filename)

        dump(memory, output_filename)


def render(flip_transitions, seeds = None):
    dhgr = np.zeros((YMAX, XMAX), dtype=np.bool)

    clock = [False, False, False, False]

    def _seed(val, offset):
        dhgr[y, offset] = val & 0b1
        clock[offset] = val & 0b1

    # flip points
    # ycenter = YMAX // 2
    # xcenter = XMAX // 2

    for y in range(YMAX):
        phase = 0

        # TODO: why do 2,3,6,7,8,9,12,13 give colours - too low intensity?
        seed = random.choice(seeds or (0, 1, 4, 5, 10, 11, 14, 15))

        # TODO: compute sequence of intensities for all 8 seeds and 2 run
        #  lengths

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

        tr = list(transitions[seed])

        _seed(seed, 3)
        seed >>= 1

        _seed(seed, 2)
        seed >>= 1

        _seed(seed, 1)
        seed >>= 1

        _seed(seed, 0)
        seed >>= 1

        # Initial choice
        run_size = 1  # random.randint(1, 2)

        run_count = 0
        do_print = False

        # radius = 192 // 2
        # y0 = y - ycenter
        # x0 = (560. / 192) * math.sqrt(radius * radius - y0 * y0)
        # flip_points = [xcenter - x0, xcenter + x0, 999]
        num_transisitions = 0

        flip_data = flip_transitions[y]
        flip_data.append((999, 1))

        should_flip = False
        for x in range(4, XMAX):
            flip_point, new_value = flip_data[num_transisitions]
            if x >= flip_point:
                flip_target_value = new_value
                should_flip = True
                num_transisitions += 1
                print("Line %d should flip at %d" % (y, x))

            # Find would-be next bit if we repeat the same colour
            next_bit = clock[phase]

            if phase not in tr:
                run_count += 1
                if run_count == run_size:
                    next_bit = 1 - next_bit
                    run_count = 0
                clock[phase] = next_bit
            else:
                # Possible transition point
                #
                # See if the transition target is valid
                next_clock = clock
                next_clock[phase] = 1 - next_bit
                next_seed = (next_clock[3]) + (next_clock[2] << 1) + (
                        next_clock[1] << 2) + (next_clock[0] << 3)

                can_flip = next_seed in transitions
                if should_flip and can_flip:
                    print("run size %d, new_value %d" % (run_size,
                                                         flip_target_value))

                if (
                        should_flip and can_flip and
                        (run_size == 3 - (flip_target_value + 1))
                ):
                    print("Line %d transitioning at %d" % (y, x))
                    should_flip = False

                    next_bit = 1 - next_bit
                    # TODO: why is it necessary to flip run_size?
                    # run_size = 3 - run_size
                    run_size = flip_target_value + 1
                    run_count = 0

                    clock[phase] = next_bit
                    seed = (clock[3]) + (clock[2] << 1) + (clock[1] << 2) + \
                           (clock[0] << 3)

                    tr = list(transitions[seed])
                else:
                    run_count += 1
                    if run_count == run_size:
                        next_bit = 1 - next_bit
                        run_count = 0
                    clock[phase] = next_bit

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

    return dhgr


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


def dump(memory, output_filename):
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

    with open(output_filename, "wb") as out:
        out.write(main.tobytes())
        out.write(aux.tobytes())


if __name__ == "__main__":
    main()
