import RPi.GPIO as gpio
import time
import pyaudio
import wave

gpio.setmode(gpio.BCM)

threshUp = 17
threshDown = 22
recording = 24
stopRecording = 23

gpio.setup(threshUp, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(threshDown, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(recording, gpio.IN, pull_up_down = gpio.PUD_UP)
gpio.setup(stopRecording, gpio.IN, pull_up_down = gpio.PUD_UP)

while True:
    up_state = gpio.input(threshUp)
    down_state = gpio.input(threshDown)
    record_state = gpio.input(recording)
    stop_state = gpio.input(stopRecording)

    if up_state == False :
        print("Raise Threshold")
        #define stream chunk   
        chunk = 1024  

        #open a wav format music  
        f = wave.open(r"/home/pi/beep-3.wav","rb")  
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
        time.sleep(.5)
    elif down_state == False :
        print("Lower Threshold")
        time.sleep(.5)
    elif record_state == False :
        print("Start Recording")
        time.sleep(.5)
    elif stop_state == False :
        print("Stop Recording")
        time.sleep(.5)
