from pyasn1.type.univ import Null
import speech_recognition as sr
from multiprocessing.dummy import Pool
import re
from word2number import w2n
import requests
import json

pool = Pool(8)  # Number of concurrent threads


with open("speech/api-key.json") as f:
    GOOGLE_CLOUD_SPEECH_CREDENTIALS = f.read()

r = sr.Recognizer()
# files = sorted(os.listdir('parts/'))


def localLiveSpeech():
    # speech = LiveSpeech(lm=False, keyphrase='forward', kws_threshold=1e-20,
    # verbose=True, debug=True)
    # for phrase in speech:
    #     print(phrase.segments(detailed=True))
    # r = sr.Recognizer()
    try:
        mic = sr.Microphone(0)
        with mic as source:
            while True:
                order_id = Null

                r.adjust_for_ambient_noise(source, duration=1)
                print("Listening...")
                audio = r.listen(source, phrase_time_limit=3)
                print("Processing...")
                try:
                    # result_order = r.recognize_sphinx(audio,
                    #   language='en-US')
                    # result_order = r.recognize_sphinx(audio,
                    #   language='en-US',keyword_entries=[("ready", 0.95)])
                    result_order = r.recognize_google_cloud(
                        audio, credentials_json=GOOGLE_CLOUD_SPEECH_CREDENTIALS
                    )
                    print("you said [{}]".format(result_order))
                    if "ready" in result_order:
                        print("We have an order! [{}]".format(result_order))
                        orders_number = re.findall(
                            r"[-+]?\d*\.\d+|[-+]?\d+", result_order)
                        print("order length ={}".format(len(orders_number)))
                        if len(orders_number) == 0:
                            print("we found ready but no order numbers")
                            continue
                        order_id = 0
                        # look for numbers as text! e.g five, sixty nine
                        if len(orders_number) == 0:
                            try:
                                order_id = w2n.word_to_num(result_order)
                                print("word to number =[{}]".format(order_id))
                            except ValueError:
                                pass
                        else:
                            order_id = orders_number[0]
                            print("order number=[{}]".format(order_id))
                        # if the number is a float looking number
                        # e.g 0.69 then we want to use the
                        # float part of the number!
                        if order_id.find(".") != -1:
                            float_parts = order_id.split(".")
                            print(float_parts)
                            for part in float_parts:
                                if int(part) > 0:
                                    order_id = int(part)

                        url = "http://api.localhost/orderready/" + order_id
                        data = {"order_id": order_id}
                        headers = {'Content-type': 'application/json',
                                   'Accept': 'text/plain'}
                        # only send the order if the number is an integer
                        if int(order_id) > 0:
                            try:
                                req = requests.put(url, data=json.dumps(
                                    data), headers=headers)
                                print("order status code {0}".format(
                                      req.status_code))
                            except requests.exceptions.RequestException as \
                                    error:
                                print("Error: Have you started the backend \
                                     api?", error)
                except sr.UnknownValueError:
                    print("can not process - try again")
                except sr.RequestError as e:
                    print("Sphinx error; {0}".format(e))

    except KeyboardInterrupt:
        pass


def main():
    localLiveSpeech()


if __name__ == "__main__":
    main()
