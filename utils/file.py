import requests


def download_image(url, filename):
	try:
		response = requests.get(url)
		# Check if the request was successful (status code 200)
		if response.status_code == 200:
			# Write the content of the response (image) to a file
			with open(filename, 'wb') as file:
				file.write(response.content)
			print(f"Image downloaded successfully as '{filename}'")
		else:
			print(f"Failed to download image from URL: {url}. Status code: {response.status_code}")
	except Exception as e:
		print(f"An error occurred: {e}")


def upload_file_to_minio(minio_client, image_path, bucket_name, object_name):
	minio_client.upload_file(
		image_path,
		bucket_name,
		object_name,
		ExtraArgs={
			'ContentType': 'image/jpeg',
			'ACL': 'public-read'
		}
	)
	return f"{minio_client.meta.endpoint_url}/{bucket_name}/{object_name}"


class BotTeleGram:
	def __init__(self, token, default_chat_id=None):
		self.default_chat_id = default_chat_id
		self.token = token

	def send_message(self, chat_id=None, text="", parse_mode="MARKDOWN"):
		if not bool(chat_id):
			chat_id = self.default_chat_id
		url = f"https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={text}&parse_mode={parse_mode}"
		requests.get(url).json()

	def send_photo(self, chat_id=None, photo_url=None, caption=None):
		if not bool(chat_id):
			chat_id = self.default_chat_id
		url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
		payload = {
			"photo": photo_url,
			"caption": caption,
			"disable_notification": False,
			"reply_to_message_id": None,
			"chat_id": chat_id
		}
		headers = {
			"accept": "application/json",
			"content-type": "application/json"
		}
		response = requests.post(url, json=payload, headers=headers)

	def send_photo_file(self, chat_id=None, photo=None, photo_path=None, caption=None):
		if not bool(chat_id):
			chat_id = self.default_chat_id
		url = f"https://api.telegram.org/bot{self.token}/sendPhoto"
		if photo is None:
			photo = open(photo_path, 'rb')
		files = {"photo": photo}
		payload = {
			"caption": caption,
			"chat_id": chat_id
		}
		response = requests.post(url, files=files, params=payload)
		print(response.json())
