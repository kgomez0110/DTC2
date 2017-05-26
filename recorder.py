import sounddevice as sd 

fs = 48000 # sampling frequency
sd.default.samplerate = fs
sd.default.channels = 2 # ???????
sd.play(voice)
sd.stop()
duration = 10 # seconds
myrecording = sd.rec(duration * fs)
sd.wait() # returns value after recording is finished