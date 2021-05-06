#Terminal Colours Start
export PROMPT='%F{green}%n%f@%F{cyan}%m%f %F{yellow}%B%~%b%f $ '
export CLICOLOR=1
export LSCOLORS=bxfxcxdxAbegedabagacad
#Terminal Colours End

#Custom Commands Start
alias ls='ls -GFh'
alias ll='ls -lGFh'
alias python=python3
alias pip=pip3

alias speedtest="speedtest-cli --bytes"
alias start_ftp="echo Starting FTP at: $(ipconfig getifaddr en0); if [[ -d '/Volumes/Seagate Backup Plus Drive/Xtras/' ]] ; then loc='/Volumes/Seagate Backup Plus Drive/Xtras/'; else loc='~/Movies/'; fi; python3 -m pyftpdlib --directory='$loc'"

alias download="aria2c --conf-path=${HOME}/.config/aria2.conf"
alias download_server="screen -dmS downloader aria2c --conf-path=${HOME}/.config/aria2.conf --enable-rpc=true --download-result=full"
loot(){ if [ $2 ] ; then loc=$2; else loc=~/Downloads;fi; curl http://127.0.0.1:6800/jsonrpc -H "Content-Type: application/json" -H "Accept: application/json" --data '{"jsonrpc": "2.0","id":1, "method": "aria2.addUri", "params":[['\"$1\"'], {"dir":'\"$loc\"'}]}'; }
alias stop_download_server="aria2p call shutdown"
loot(){ if [ $2 ] ; then loc=$2; else loc=~/Downloads;fi; curl http://127.0.0.1:6800/jsonrpc -H "Content-Type: application/json" -H "Accept: application/json" --data '{"jsonrpc": "2.0","id":1, "method": "aria2.addUri", "params":[['\"$1\"'], {"dir":'\"$loc\"'}]}'; }
alias manage_downloads='aria2p top'

alias github_sync="sh ~/Github/Mac/git_sync.sh"
torrent_files() {if mount | grep -q '/Volumes/Seagate\ Backup\ Plus\ Drive'; then; cp /Users/vivekarya/Library/Application\ Support/qBittorrent/BT_backup/*.torrent /Volumes/Seagate\ Backup\ Plus\ Drive/Xtras/Torrent\ Files/; echo Backed up : $(ls /Volumes/Seagate\ Backup\ Plus\ Drive/Xtras/Torrent\ Files/ | wc -l); else; echo Drive NOT Mounted!!; fi;}
alias dependencies_brew='brew leaves | xargs brew deps --for-each | sed "s/^.*:/$(tput setaf 1)&$(tput sgr0)/"'
alias mp3youtube="youtube-dl --extract-audio --audio-format mp3 -f bestaudio --audio-quality 0"
alias corona="python -c \"import requests; data=requests.get('https://api.covid19india.org/data.json').json()['statewise'][0];  tm, confirm, delta = data['lastupdatedtime'], int(data['confirmed']), int(data['deltaconfirmed']); display=f'{tm} => {confirm:,} ({delta:,})'; print(display)\""

alias ips="cat ~/.ip_list"
alias proxyon="export http_proxy='socks5://127.0.0.1:9050'; export https_proxy='socks5://127.0.0.1:9050'"
alias proxyoff="export http_proxy=''; export https_proxy=''"
#Custom Commands End

#Old Commands
#alias walkman="sh ~/Github/Mac/walkman.sh"
#alias backup="python ~/Github/Mac/backup.py"
#alias news="sh ~/Github/Mac/news.sh"
#alias update="brew update; brew upgrade --ignore-pinned; brew cleanup; brew doctor"
#alias wget="wget -P ~/Downloads/"
#Old Commands End

#zsh auto completion start
autoload -Uz compinit
compinit
zstyle ':completion:*' menu select
# don't use autocompletion for git. it's slow as hell
compdef -d git

# Get fn+delete working in zsh
bindkey "^[[3~" delete-char

#zsh auto completion ends

#Bash Completion
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"
