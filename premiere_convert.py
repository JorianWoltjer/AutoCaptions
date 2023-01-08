from jinja2 import Template
from base64 import b64encode
import json
import pysrt
import os
import sys

FRAME_RATE = 60  # FPS
WIDTH, HEIGHT = 1920, 1080
DIR = sys.path[0]

with open(os.path.join(DIR, "templates", "premiere_sequence.xml")) as f:
    template = Template(f.read())

def total_secs(time):
    secs = time.milliseconds / 1000
    secs += time.seconds
    secs += time.minutes * 60
    secs += time.hours * 60 * 60
    return secs

def make_data(text):
    data = {"mShadowFontMapHash": None,
            "mTextParam": {
                "mAlignment": 2.0,
                "mBackFillColor": 0.0,
                "mBackFillOpacity": 0.0,
                "mBackFillSize": 0.0,
                "mBackFillVisible": False,
                "mDefaultRun": [],
                "mHeight": 0.0,
                "mHindiDigits": False,
                "mIndic": False,
                "mIsMask": False,
                "mIsMaskInverted": False, 
                "mIsVerticalText": False, 
                "mLeading": 0.0,
                "mLigatures": False, 
                "mLineCapType": 0.0, 
                "mLineJoinType": 0.0, 
                "mMiterLimit": 0.0, 
                "mNumStrokes": 1.0, 
                "mRTL": False, 
                "mShadowAngle": 135.0, 
                "mShadowBlur": 40.0, 
                "mShadowColor": 4144959.0, 
                "mShadowOffset": 7.0, 
                "mShadowOpacity": 75.0, 
                "mShadowSize": 0.0, 
                "mShadowVisible": False, 
                "mStyleSheet": {
                    "mAdditionalStrokeColor": [], 
                    "mAdditionalStrokeVisible": [], 
                    "mAdditionalStrokeWidth": [], 
                    "mBaselineOption": {"mParamValues": [[0.0, 0.0]]}, 
                    "mBaselineShift": {"mParamValues": [[0.0, 0.0]]}, 
                    "mCapsOption": {"mParamValues": [[0.0, 0.0]]}, 
                    "mFauxBold": {"mParamValues": [[0, False]]}, 
                    "mFauxItalic": {"mParamValues": [[0, False]]}, 
                    "mFillColor": {"mParamValues": [[0.0, 16777215.0]]}, 
                    "mFillOverStroke": {"mParamValues": [[0, True]]}, 
                    "mFillVisible": {"mParamValues": [[0, True]]}, 
                    "mFontName": {"mParamValues": [[0, "ArialMT"]]}, 
                    "mFontSize": {"mParamValues": [[0.0, 60.0]]}, 
                    "mKerning": {"mParamValues": [[0.0, 0.0]]}, 
                    "mStrokeColor": {"mParamValues": [[0.0, 0.0]]}, 
                    "mStrokeVisible": {"mParamValues": [[0, True]]}, 
                    "mStrokeWidth": {"mParamValues": [[0.0, 10.0]]}, 
                    "mText": text, 
                    "mTracking": {"mParamValues": [[0.0, 0.0]]}, 
                    "mTsumi": {"mParamValues": [[0.0, 0.0]]}, 
                    "mUnderline": None}, 
                "mTabWidth": 400.0, 
                "mVerticalAlignment": 0.0, 
                "mWidth": 0.0}, 
            "mUseLegacyTextBox": False, 
            "mVersion": 1.0
        }
    
    s = json.dumps(data, ensure_ascii=False)  # Makes sure characters like 'é' are not escaped
    
    data = b"\x0f\x0f\x00\x00\x00\x00\x00\x00" + s.encode('utf-16-le')
    
    return b64encode(data).decode('utf-8')

def ascii(text):
    import unicodedata
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')

def srt_to_xml(srt_filename):
    clips = []

    captions = pysrt.open(srt_filename)
    for line in captions:
        clips.append({
            "name": ascii(line.text),  # Convert to ascii
            "start": round(total_secs(line.start)*FRAME_RATE),
            "end": round(total_secs(line.end)*FRAME_RATE),
            "data": make_data(line.text.rstrip('.'))
        })

    settings = {
        "duration": clips[-1]['end'],
        "timebase": FRAME_RATE,
        "width": WIDTH,
        "height": HEIGHT
    }
    
    filename = os.path.splitext(os.path.basename(srt_filename))[0]

    return template.render(settings=settings, clips=clips, filename=filename)
