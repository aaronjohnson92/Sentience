if [ $(id -u) = 0 ]; then
   echo "Do not run as root, yet. Try again."
   exit 1
fi

req=`python3 -c 'import sys; print("%i" % (sys.hexversion<0x03000000))'`
if [ $req -eq 0 ]; then
    echo 'python version is >= 3'
    echo 'Installing dependices'
    sudo apt-get install python3-pip libexpat1-dev libpython3-dev python-pip-whl python3-dev python3-setuptools python3-wheel build-essential git ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev swig libpulse-dev espeak
    sudo apt-get update
else 
    echo "python version is < 3"
    echo "Installing Python3+ and dependencies" 
    sudo apt-get install python3 python3-pip libexpat1-dev libpython3-dev python-pip-whl python3-dev python3-setuptools python3-wheel build-essential git ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev swig libpulse-dev espeak
    sudo apt-get update
    echo "Python 3 is now installed." 
fi 
    read -p "Install remaining dependencies?(y/n)" ok
    wget - http://www.portaudio.com/archives/pa_stable_v190600_20161030.tgz
    tar -xvzf pa_stable_v190600_20161030.tgz
    cd portaudio
    echo n | ./configure && make
    echo n | sudo make install
    sudo apt-get update
    sudo -H python3 -m pip install Cython==0.23 
    sudo -H python3 -m pip install kivy==1.9.1 pyttsx3 chatterbot PyAudio PocketSphinx SpeechRecognition bleach boto boto3 botocore bz2file cffi click colorama command-not-found cryptography cssselect docutils fire flashtext Flask future gensim google-api-core google-api-python-client google-auth google-cloud-core google-resumable-media googleapis-common-protos html5lib httplib2 idna imbalanced-learn jedi Jinja2 jupyter jupyter-console jupyter-core kappa Keras  luminoth lxml nltk notebook numpy pandas pendulum Pillow pyasn1 pycrypto pygobject pymongo PyNaCl PyOpenGL PyQt5 PySDL2 python-twitter pytz PyYAML pyzmq requests rsa scikit-learn scipy selenium setuptools sip six SQLAlchemy ssh-import-id style tensorflow tensorflow-gpu Theano tornado tqdm  urllib3 wheel xkit xlwt
	
    if ! [ $ok = "y" -o $ok = "Y" ]; then exit 1
fi
