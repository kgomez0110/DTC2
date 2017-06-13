#!/usr/bin/python
import smbus
import math
import RPi.GPIO as gpio
import time
#import sounddevice as sd
import pyaudio
import wave


'''recorder.py
Provides WAV recording functionality via two approaches:
Blocking mode (record for a set duration):
>>> rec = Recorder(channels=2)
>>> with rec.open('blocking.wav', 'wb') as recfile:
...     recfile.record(duration=5.0)
Non-blocking mode (start and stop recording):
>>> rec = Recorder(channels=2)
>>> with rec.open('nonblocking.wav', 'wb') as recfile2:
...     recfile2.start_recording()
...     time.sleep(5.0)
...     recfile2.stop_recording()
'''
######################################
class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):
    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None

    def __enter__(self):
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            self.wavefile.writeframes(audio)
        return None

    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile

########################################################
# power managment registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

gpio.setmode(gpio.BCM)

threshUp = 17
threshDown = 22
recording = 24
stopRecording = 23

firstTime = True
isRecording = False
something = False
thresh = 5000
fs = 48000
duration = 6
#sd.default.samplerate = fs
#sd.default.channels = 2

def read_byte(adr):
    return bus.read_byte_data(address,adr)
 
def read_word(adr):
    high = bus.read_byte_data(address,adr)
    low = bus.read_byte_data(address,adr+1)
    val = (high << 8) + low
    return val
 
def read_word_2c(adr):
    val = read_word(adr)
    if(val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val
 
bus = smbus.SMBus(1)
address = 0x68      #mpu address
 
#wake up the 6050
bus.write_byte_data(address,power_mgmt_1,0)
 
gpio.setup(threshUp, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(threshDown, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(recording, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(stopRecording, gpio.IN, pull_up_down = gpio.PUD_UP)

def playWAV(filePath) : 
    #define stream chunk   
    chunk = 1024  

    #open a wav format music  
    f = wave.open(filePath,"rb")  
    #instantiate PyAudio  
    p = pyaudio.PyAudio()  
    #open stream  
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                    channels = f.getnchannels(),  
                    rate = f.getframerate(),  
                    output = True)  
    #read data  
    data = f.readframes(chunk)  

    #play stream  
    while data:  
        stream.write(data)  
        data = f.readframes(chunk)  

    #stop stream  
    stream.stop_stream()  
    stream.close()  

    #close PyAudio  
    p.terminate()

playWAV(r"/home/pi/ready.wav")
print("ready")
while True :
    
    current_xout = read_word_2c(0x3b)
    current_yout = read_word_2c(0x3d)
    current_zout = read_word_2c(0x3f)

    up_state = gpio.input(threshUp)
    down_state = gpio.input(threshDown)
    record_state = gpio.input(recording)
    stop_state = gpio.input(stopRecording)
    
    if firstTime :
        last_xout = current_xout
        last_yout = current_yout
        last_zout = current_zout
        firstTime = False
    if up_state == False :
        print("Raise Threshold")
        thresh = thresh + 200
        print(thresh)
        if thresh > 10000 :
            thresh = 10000
        playWAV(r"/home/pi/boop.wav")
    elif down_state == False :
        print("Lower Treshold")
        thresh = thresh - 200
        print(thresh)
        if thresh < 100 :
            thresh = 100
        playWAV(r"/home/pi/boop.wav")
        print(thresh)
    elif stop_state == False :
        if thresh != 10000 :
            thresh = 10000
            print(":set to max")
            print(thresh)
        else :
            thresh = 1000
            print("set to min")
            print(thresh)
        playWAV(r"/home/pi/boop.wav")
    elif record_state == False and isRecording == False :
        print("recording")
          #define stream chunk   
        chunk = 1024  

        #open a wav format music  
        f = wave.open(r"/home/pi/recording.wav","rb")  
        #instantiate PyAudio  
        p = pyaudio.PyAudio()  
        #open stream  
        stream = p.open(format = p.get_format_from_width(f.getsampwidth()),  
                        channels = f.getnchannels(),  
                        rate = f.getframerate(),  
                        output = True)  
        #read data  
        data = f.readframes(chunk)  

        #play stream  
        while data:  
            stream.write(data)  
            data = f.readframes(chunk)  

        #stop stream  
        stream.stop_stream()  
        stream.close()  

        #close PyAudio  
        p.terminate()  
        isRecording = True
        #myRecording = sd.rec(duration)
        #sd.wait()
        rec = Recorder(channels=2)
        with rec.open('myRecording.wav','wb') as recfile2 :
            recfile2.start_recording()
            #while stop_state == True :
            time.sleep(3)
            recfile2.stop_recording()
        isRecording = False
        something = True
        print("done recording")
    elif abs(current_xout - last_xout) > thresh or abs(current_yout - last_yout) > thresh or abs(current_zout - last_zout) > thresh :
        print("triggered")
        if something :
            playWAV(r"/home/pi/myRecording.wav")
            time.sleep(3)
    last_xout = current_xout
    last_yout = current_yout
    last_zout = current_zout
