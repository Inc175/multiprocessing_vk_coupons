from multiprocessing import Process, Queue
import qrcode
import vk_api
from vk_api import VkUpload
import time
from random import randint
import uuid
from PIL import Image


class VKbot:
    def __init__(self):
        self.q = Queue()

    def generate_one_qr_code_image(self, url):
        img = qrcode.make(url)
        img = img.resize((500,500))

        qr_code_path = 'qrcode_images/' + str(uuid.uuid4().hex) + '.jpg'
        img.save(qr_code_path)
        return qr_code_path

    def generate_one_coupon_image(self, qr_code_path): 
        coupon_path = 'coupons_images' + qr_code_path[13:]
        
        img = Image.open(qr_code_path)
        background = Image.open('template-page-001.jpg')
    
        # upper-left corner coordinates
        offset = ((500 - 250), (500 - 250))
        # paste qrcode image
        background.paste(img, offset)
        background.save(coupon_path)
        return coupon_path   
     
    def add_one_coupon_to_queue(self, coupon_path):
        self.q.put(coupon_path)
    
    def generate_coupons(self):
        for i in range(5):
            qr_code_path = self.generate_one_qr_code_image("www.google.com")
            coupon_path = self.generate_one_coupon_image(qr_code_path)
            self.add_one_coupon_to_queue(coupon_path)

    def send_coupons(self):
        # for coupons uploading
        vk_session = vk_api.VkApi('login', 'password')
        vk_session.auth(token_only=True)
        upload = vk_api.VkUpload(vk_session)

        # for sending messages
        vk_session_2 = vk_api.VkApi(token='token')
        vk = vk_session_2.get_api()

        for i in range(10):
            name = self.q.get()

            # uploading coupon image to group album
            photo = upload.photo(name, album_id='album_id', 
                                        group_id='group_id')

            # formimg attachment
            attachments = []
            attachments.append(
                'photo{}_{}'.format(photo[0]['owner_id'], photo[0]['id'])
            )

            # sending message with attachment
            vk.messages.send(
                user_id='user_id',
                attachment=','.join(attachments),
                message='Your QR-code!',
                random_id=randint(1, 10000)
            )

            time.sleep(1)

    
if __name__ == "__main__":
    vk_bot = VKbot()

    # run 2 processes for coupons generation
    for i in range(2):
        prс = Process(target=vk_bot.generate_coupons)
        prc.start()

    # send coupons
    prc = Process(target=vk_bot.send_coupons)
    prc.start()





