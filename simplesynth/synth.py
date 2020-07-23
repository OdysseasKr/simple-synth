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
    def __init__(self, sf=44100):
        """
        Parameters
        ----------
        sf : int
            Samplerate used for the resulting sounds
        """
        self.sf = sf
        self.set_parameters()

    def set_parameters(self, **kwargs):
        """Sets the parameters of the synth"""
        # TODO: Add range check for phase, mix and cuttoff
        self.osc_1_name = kwargs.get('osc_1', 'Sine')
        self.osc_1 = osc_1_options[self.osc_1_name]
        self.osc_2_name = kwargs.get('osc_2', 'Sine')
        self.osc_2 = osc_2_options[self.osc_2_name]
        self.mix = kwargs.get('mix', 0.5)
        self.phase_1 = kwargs.get('phase_1', 0)
        self.cutoff = kwargs.get('cutoff', 10000)

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
        # TODO: This doesn't work with duration < 1
        num_blocks = self.sf*duration//params.norm_osc_blocksize
        tmp = np.array(list(itertools.islice(obj.blocks(), num_blocks)))
        return tmp.flatten()

    def _hookup_modules(self, note):
        """Creates oscillators with the correct parameters pipeline"""
        osc1 = self.osc_1(note,
                          amplitude=1 - self.mix,
                          phase=self.phase_1,
                          samplerate=self.sf)
        osc2 = self.osc_2(note,
                          amplitude=self.mix,
                          samplerate=self.sf)
        mixer = MixingFilter(osc1, osc2)
        self.out = LowPassFilter(mixer, cutoff=self.cutoff, samplerate=self.sf)

    def get_sound_array(self, note=440, duration=1):
        """Returns a sound for the set parameters

        Returns
        -------
        sound_array : np.ndarray
            The sound for the given note and duration
        """
        self._hookup_modules(note)
        return self._get_raw_data_from_obj(self.out, duration)
