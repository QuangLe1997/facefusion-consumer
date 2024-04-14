#!/usr/bin/env python3

from facefusion import core

if __name__ == '__main__':
	output = core.cli(
			source_paths=['input/quangle.jpg'],
			target_path='input/video.mp4',
			config_params={}
	)
	print(output)
