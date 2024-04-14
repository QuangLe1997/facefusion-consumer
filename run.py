#!/usr/bin/env python3

from facefusion import core

if __name__ == '__main__':
	core.setup_variable()
	output = core.main_process(
			source_paths=['input/quangle.jpg'],
			target_path='input/quangle2.jpg',
			config_params={
				'face_selector_mode': 'many'
			}
	)
