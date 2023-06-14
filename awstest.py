import boto3
import os
from tempfile import gettempdir
from contextlib import closing

# constant
REGION = 'us-east-1'
SRC_LANG = 'en'
TRG_LANG = 'ja'


def get_translate_text(text):

    translate = boto3.client('translate', region_name=REGION)

    response = translate.translate_text(
        Text=text,
        SourceLanguageCode=SRC_LANG,
        TargetLanguageCode=TRG_LANG
    )

    return response

def play_polly_text(text):
    polly = boto3.client("polly", region_name=REGION)

    response = polly.synthesize_speech(Text = text,
                                    OutputFormat = "mp3",
                                    VoiceId = "Takumi",Engine='neural')

    if "AudioStream" in response:
        with closing(response["AudioStream"]) as stream:
            output = os.path.join(gettempdir(), "speech.mp3")

            with open(output, "wb") as file:
                file.write(stream.read())

    os.startfile(output)

def detect_labels_local_file(photo):
    client=boto3.client('rekognition')
   
    with open(photo, 'rb') as image:
        response = client.detect_labels(Image={'Bytes': image.read()})
        
    print('Detected labels in ' + photo)    
    for label in response['Labels']:
        print (label['Name'] + ' : ' + str(label['Confidence']))

    return len(response['Labels'])

def main():
    # Text to translate
    text = """Natural and accurate language translation"""

    # From Japanese to English
    # while len(text.encode('utf-8')) > 5000:
    #   text = text[:-1]

    # From English to Japanese
    # while len(text) > 5000:
    #  text = text[:-1]

    result = get_translate_text(text)
    print(result.get('TranslatedText'))
    # play_polly_text("なんか途中から聞こえるのは変じゃない？今日の天気は雨")

    label_count=detect_labels_local_file("gimp.jpg")
    print("Labels detected: " + str(label_count))


if __name__ == '__main__':
    main()