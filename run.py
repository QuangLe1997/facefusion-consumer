#!/usr/bin/env python3

from facefusion import core

import json
import os
import subprocess
import time
import uuid

import boto3
import requests
from confluent_kafka import Consumer

from utils.file import download_image, BotTeleGram, upload_file_to_minio

# Kafka Consumer to receive messages from the queue
consumer = Consumer({
	'bootstrap.servers': os.getenv("KAFKA_BROKERS"),
	'group.id': os.getenv("KAFKA_GROUP_ID"),
	'auto.offset.reset': 'earliest'}
)
consumer.subscribe([os.getenv("KAFKA_TOPIC")])
controller_endpoint = os.getenv("CALLBACK_ENDPOINT")
bot_telegram = BotTeleGram(
	token=os.getenv("TELEGRAM_BOT_TOKEN"),
	default_chat_id=os.getenv("TELEGRAM_CHAT_ID")
)

minio_client = boto3.client(
	's3',
	endpoint_url=os.getenv('MINIO_ENDPOINT', "http://minio:9000"),
	aws_access_key_id=os.getenv('MINIO_ACCESS'),
	aws_secret_access_key=os.getenv('MINIO_SECRET'))
bot_telegram.send_message(text='Consumer started')


if __name__ == '__main__':
	core.setup_variable()
	while True:
		msg = consumer.poll(1.0)
		if msg is None:
			continue
		if msg.error():
			print("Consumer error: {}".format(msg.error()))
			bot_telegram.send_message(text='Consumer error: {}'.format(msg.error()))
			continue
		message_data = json.loads(msg.value().decode('utf-8'))
		source_path = None
		target_path = None
		config_params = message_data.get('config_params', {})
		if message_data.get('source_url'):
			try:
				source_path = os.path.join('input', message_data.get('source_url').split('/')[-1])
				download_image(message_data.get('source_url'), source_path)
				bot_telegram.send_photo(
					photo_url=message_data.get('source_url'),
					caption='Source image'
				)
			except Exception as e:
				source_path= None
				bot_telegram.send_message(text='Failed to download image source, {}'.format(e))
		if message_data.get('target_url'):
			try:
				target_path = os.path.join('input', message_data.get('target_url').split('/')[-1])
				download_image(message_data.get('target_url'),target_path)
				bot_telegram.send_photo(
					photo_url=message_data.get('target_url'),
					caption='Target image'
				)
			except Exception as e:
				target_path = None
				bot_telegram.send_message(text='Failed to download image target, {}'.format(e))
		name = str(uuid.uuid4())
		output_path = os.path.join('output', f'{name}.jpg')
		if source_path and target_path:
			statis_data, url_final = core.main_process(
				source_paths=[source_path],
				target_path=target_path,
				output_path=output_path,
				config_params=config_params
			)
			if url_final:
				url_result = upload_file_to_minio(minio_client, output_path, os.getenv("BUCKET_NAME"), f'{name}.jpg')
				bot_telegram.send_photo(
					photo_url=url_result,
					caption='Result'
				)
		bot_telegram.send_message(text='Consumer process completed')
	consumer.close()
