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
alias speedtest="speedtest-cli --bytes"
alias update="brew update; brew upgrade; brew cleanup; brew doctor"
alias mp3youtube="youtube-dl --extract-audio --audio-format mp3 -f bestaudio --audio-quality 0"
alias wget="wget -P ~/Downloads/"
alias download="aria2c --max-connection-per-server=10 --split=10 --check-integrity=true --dir=Downloads --file-allocation=none --continue=true --summary-interval=0"
alias github="sh ~/Github/Mac/git_sync.sh"
alias dependencies_brew='brew leaves | xargs brew deps --installed --for-each | sed "s/^.*:/$(tput setaf 4)&$(tput sgr0)/"'
#Custom Commands End

#Bash Completion
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"
