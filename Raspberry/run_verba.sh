PYTHONPATH=../../../binaries/raspbian/armv7l:../../../python \
LD_LIBRARY_PATH=../../../binaries/raspbian/armv7l:$LD_LIBRARY_PATH \
python3 recognizer2.py --video ./video2.mp4 --assets ../../../assets  --mode 1