import PySimpleGUI as sg
#wordのファイルを操作するため
import docx
#AWSのサービスを利用するため
import boto3
#wordを起動するため
import win32com.client
#docxをpdfに変換するため
from docx2pdf import convert
#Adobe Reader（外部プログラム）を動かすため
import subprocess

import os

#カレントディレクトリを取得する
cwd = os.getcwd() + "\\"

#Wordを起動する : Applicationオブジェクトを生成する
# Application=win32com.client.Dispatch("Word.Application")

#東京リージョン
REGION = 'ap-northeast-1'
SRC_LANG = 'en'
TRG_LANG = 'ja'

#翻訳エンジンへの接続
translate = boto3.client('translate', region_name=REGION)

layout = [
   [sg.Text("ファイル"), sg.InputText(), sg.FileBrowse(key="file1",button_text="ファイル選択")],
   [sg.Submit("翻訳"), sg.Cancel("キャンセル")],
]

window = sg.Window("ファイル選択", layout)

#ファイルを読み込む
event, values = window.read()
if event == "翻訳":
    doc = docx.Document(values['file1'])
    newdoc = docx.Document()
    for paragraph in doc.paragraphs:
        print(paragraph.text)
        if paragraph.text != "":
            response = translate.translate_text(
                    Text=paragraph.text,
                    SourceLanguageCode=SRC_LANG,
                    TargetLanguageCode=TRG_LANG
                    )
            # print(response['TranslatedText'])
            paragraph.text = response['TranslatedText'].replace('証人', '本契約').replace('一方、', '')
            # paragraph.text = response['TranslatedText']
            # paragraph.style.paragraph_format.alignment.
            # print(paragraph.style.paragraph_format)
        
        newdoc.add_paragraph(paragraph.text)
        newdoc.paragraphs[-1].alignment = paragraph.alignment

newdoc.save(cwd + "翻訳結果.docx")
#作成したwordファイルを表示
#Application.Documents.Open(cwd + "翻訳結果.docx")
#Application.Visible=True

#pdfへ変換する
convert(cwd + "翻訳結果.docx")

#Acrobat.exe 保管場所
acr_path = "C:/Program Files/Adobe/Acrobat DC/Acrobat/Acrobat.exe"

pdf_pro = subprocess.Popen([acr_path,cwd + "翻訳結果.pdf"], shell=False)

while True:  # Event Loop
    event, values = window.read()
    if event == "キャンセル":
        break

pdf_pro.kill()