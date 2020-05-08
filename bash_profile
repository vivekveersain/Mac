#Terminal Colours Start
export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h:\[\033[33;1m\]\w\[\033[m\]\$ "
export CLICOLOR=1
export LSCOLORS=bxfxcxdxAbegedabagacad
#Terminal Colours End

#Custom Commands Start
alias ls='ls -GFh'
alias ll='ls -lGFh'
alias python=python3
alias pip=pip3
alias walkman="sh ~/Github/Mac/walkman.sh"
alias backup="python ~/Github/Mac/backup.py"
#alias news="sh ~/Github/Mac/news.sh"
alias speedtest="speedtest-cli --bytes"
alias update="brew update; brew upgrade; brew cleanup; brew doctor"
alias mp3youtube="youtube-dl --extract-audio --audio-format mp3 -f bestaudio --audio-quality 0"
alias wget="wget -P ~/Downloads/"
alias download="aria2c --conf-path=${HOME}/.config/aria2.conf"
alias github_sync="sh ~/Github/Mac/git_sync.sh"
alias dependencies_brew='brew leaves | xargs brew deps --installed --for-each | sed "s/^.*:/$(tput setaf 4)&$(tput sgr0)/"'
alias corona="python -c \"import requests; data=requests.get('https://api.covid19india.org/data.json').json()['statewise'][0]; display='%s => %s (%s)' % (data['lastupdatedtime'], data['confirmed'], data['deltaconfirmed']); print(display)\""
#Custom Commands End

#Bash Completion
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"
