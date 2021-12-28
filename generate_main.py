import argparse
import os
import librosa

from generating import AudioGenerator

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_folder', help='Folder of trained model', type=str, required=True)
    parser.add_argument('--n_signals', help='Number of signals to generate', type=int, default=1)
    parser.add_argument('--length', help='Length of signals to generate', type=float, default=30)
    parser.add_argument('--generate_all_scales', help='Write signals of all scales', default=False, action='store_true')
    parser.add_argument('--condition',
                        help='Condition the generated signals on the lowest scale of input, to enforce general structure',
                        default=False, action='store_true')
    parser.add_argument('--condition_file', help='file to use to condition the generation of the selected model', type=str, default=None)
    parser.add_argument('--reconstruct', help='Generate the reconstruction of the signal', default=False, action='store_true')
    args = parser.parse_args()

    audio_generator = AudioGenerator(os.path.join('outputs', args.input_folder))
    if args.condition or args.condition_file:
        if args.condition_file:
            print('conditioning with custom file', args.condition_file + '.wav')
            condition_signal, condition_fs = librosa.load(
                os.path.join('inputs/', args.condition_file + '.wav'), sr=audio_generator.params.fs_list[0],  duration=args.length)
            norm_factor = max(abs(condition_signal.reshape(-1)))
            print(norm_factor, 'norm factor')
            condition_signal = condition_signal / norm_factor
        else:
            condition_signal, condition_fs = librosa.load(
                os.path.join(audio_generator.output_folder, 'real@%dHz.wav' % audio_generator.params.fs_list[0]), sr=None)
        condition = {'condition_signal': condition_signal, 'name': args.condition_file, 'condition_fs': condition_fs}
        audio_generator.condition(condition)

    if args.reconstruct:
        audio_generator.reconstruct()
    else:
        if args.condition:
            condition_signal, condition_fs = librosa.load(
                os.path.join(audio_generator.output_folder, 'real@%dHz.wav' % audio_generator.params.fs_list[0]), sr=None)
            condition = {'condition_signal': condition_signal, 'name': 'self', 'condition_fs': condition_fs}
            audio_generator.condition(condition)
        else:
            audio_generator.generate(nSignals=args.n_signals, length=args.length,
                                     generate_all_scales=args.generate_all_scales)
