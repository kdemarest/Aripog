# Environment

Make sure that your ~/.bash_profile contains
export OPENAI_API_KEY={your openai api key} 

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py

pip install flask[async]
pip install openai
pip install tiktoken
pip install redis
cd ~/code/Aripog

# Configue VSCode
In setting search for files.ass
Add the key *.yak and the value source.yak


# Get Redis
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install redis


# To run Aripig:
brew services start redis
python3 main.py

# To stop redis
brew services stop redis


watchmedo shell-command -p '*.py' --recursive --command='python3 main.py' .

