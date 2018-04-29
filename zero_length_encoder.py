# coding:utf-8


class ZeroLengthEncoder:
    @staticmethod
    def encode(sequence):
        zero_run_length = 0
        encoded_sequence = []

        for s in sequence:
            if s:
                encoded_sequence.append([zero_run_length, s])
                zero_run_length  = 0
            else:
                zero_run_length += 1
        else:
            if zero_run_length:
                encoded_sequence.append([zero_run_length, 0])

        return encoded_sequence

    @staticmethod
    def decode(sequence):
        decoded_sequence = []

        for s in sequence:
            zero_run_length, value = s
            decoded_sequence += [0]*zero_run_length
            if value:
                decoded_sequence += [value]

        return decoded_sequence
