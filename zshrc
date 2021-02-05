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
alias walkman="sh ~/Github/Mac/walkman.sh"
alias backup="python ~/Github/Mac/backup.py"
alias news="sh ~/Github/Mac/news.sh"
alias speedtest="speedtest-cli --bytes"
#alias update="brew update; brew upgrade --ignore-pinned; brew cleanup; brew doctor"
alias mp3youtube="youtube-dl --extract-audio --audio-format mp3 -f bestaudio --audio-quality 0"
#alias wget="wget -P ~/Downloads/"
alias torrent_files="if mount | grep -q '/Volumes/Seagate\ Backup\ Plus\ Drive'; then; cp /Users/vivekarya/Library/Application\ Support/qBittorrent/BT_backup/*.torrent /Volumes/Seagate\ Backup\ Plus\ Drive/Xtras/Torrent\ Files/; echo Backed up : $(ls /Volumes/Seagate\ Backup\ Plus\ Drive/Xtras/Torrent\ Files/ | wc -l); else; echo Drive NOT Mounted!!; fi;"
alias start_ftp="echo Starting FTP at: $(ipconfig getifaddr en0); python3 -m http.server --directory ./Movies"
#alias start_download_manager="screen -dmS downloader aria2c --conf-path=${HOME}/.config/aria2_torrent.conf --download-result=full --enable-rpc=true"
#alias seed_torrents="sh ~/Github/Mac/start_torrent_client.sh"
#alias stop_download_manager="aria2p call shutdown"
#append_torrent(){ aria2p call adduri --json-params '[[ '\"$1\"' ], { "dir" : '\"$2\"'}]'; }
#alias manage_downloads='aria2p top'
alias download="aria2c --conf-path=${HOME}/.config/aria2.conf"
alias github_sync="sh ~/Github/Mac/git_sync.sh"
alias dependencies_brew='brew leaves | xargs brew deps --installed --for-each | sed "s/^.*:/$(tput setaf 4)&$(tput sgr0)/"'
alias corona="python -c \"import requests; data=requests.get('https://api.covid19india.org/data.json').json()['statewise'][0];  tm, confirm, delta = data['lastupdatedtime'], int(data['confirmed']), int(data['deltaconfirmed']); display=f'{tm} => {confirm:,} ({delta:,})'; print(display)\""
alias ips="cat ~/.ip_list"
#Custom Commands End

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
