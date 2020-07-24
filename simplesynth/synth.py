from abc import ABC
import numpy as np
import itertools
from synthplayer.oscillators import Sine, Triangle, Square, SquareH, Sawtooth
from synthplayer.oscillators import Pulse, WhiteNoise, Semicircle, MixingFilter
from synthplayer import params
from .filters import LowPassFilter


osc_1_options = {
    'Sine': Sine,
    'Triangle': Triangle,
    'Square': Square,
    'SquareH': SquareH,
    'Sawtooth': Sawtooth,
    'Pulse': Pulse,
    'Semicircle': Semicircle
}

osc_2_options = {
    'Sine': Sine,
    'Triangle': Triangle,
    'Square': Square,
    'SquareH': SquareH,
    'Sawtooth': Sawtooth,
    'Pulse': Pulse,
    'WhiteNoise': WhiteNoise,
    'Semicircle': Semicircle
}


class Synth(ABC):
    def __init__(self, sr=44100):
        """
        Parameters
        ----------
        sr : int
            Samplerate used for the resulting sounds
        """
        self.sr = sr
        self.set_parameters()

    def set_parameters(self, **kwargs):
        """Sets the parameters of the synth"""
        self._check_parameters_values(kwargs)
        self.osc_1_name = kwargs.get('osc_1', 'Sine')
        self.osc_1 = osc_1_options[self.osc_1_name]
        self.osc_2_name = kwargs.get('osc_2', 'Sine')
        self.osc_2 = osc_2_options[self.osc_2_name]
        self.mix = kwargs.get('mix', 0.5)
        self.phase_1 = kwargs.get('phase_1', 0)
        self.cutoff = kwargs.get('cutoff', 10000)

    def _check_parameters_values(self, kwargs):
        if kwargs.get('osc_1', 'Sine') not in osc_1_options:
            raise AssertionError('Invalid shape for osc 1')
        if kwargs.get('osc_2', 'Sine') not in osc_2_options:
            raise AssertionError('Invalid shape for osc 2')
        if kwargs.get('mix', 0.5) < 0 or kwargs.get('mix', 0.5) > 1 :
            raise AssertionError('Parameter `mix` should be in the range [0,1]')
        if kwargs.get('phase', 0) < 0 or kwargs.get('phase', 0) > 0.5:
            raise AssertionError('Parameter `phase` should be in the range [0,0.5]')

    def get_parameters(self):
        """Returns a dict with the current paramters"""
        return {
            'osc_1': self.osc_1_name,
            'osc_2': self.osc_2_name,
            'mix': self.mix,
            'phase_1': self.phase_1,
            'cutoff': self.cutoff,
        }

    def _get_raw_data_from_obj(self, obj, duration):
        num_blocks = int(self.sr*duration//params.norm_osc_blocksize)
        tmp = np.array(list(itertools.islice(obj.blocks(), num_blocks)))
        return tmp.flatten()

    def _hookup_modules(self, note):
        """Creates oscillators with the correct parameters pipeline"""
        osc1 = self.osc_1(note,
                          amplitude=1 - self.mix,
                          phase=self.phase_1,
                          samplerate=self.sr)
        osc2 = self.osc_2(note,
                          amplitude=self.mix,
                          samplerate=self.sr)
        mixer = MixingFilter(osc1, osc2)
        self.out = LowPassFilter(mixer, cutoff=self.cutoff, samplerate=self.sr)

    def get_sound_array(self, note=440, duration=1):
        """Returns a sound for the set parameters

        Returns
        -------
        sound_array : np.ndarray
            The sound for the given note and duration
        """
        self._hookup_modules(note)
        return self._get_raw_data_from_obj(self.out, duration)
