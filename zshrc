#temp settings
#export OPENSSL_CONF=~/Github/Scrappers/temp_openssl.cnf
#temp settings end

#Terminal Colours Start
export PROMPT='%F{yellow}%~%b%f %F{red}$%f '
#export PROMPT='%F{green}%n%f@%F{cyan}%m%f %F{yellow}%B%~%b%f $ '
export CLICOLOR=1
export LSCOLORS=bxfxcxdxAbegedabagacad
#Terminal Colours End

#Custom Commands Start
alias ls='ls -GFh'
alias ll='ls -lGFh'
alias gpg='gpg1'
export PATH=/usr/local/bin:/usr/local/sbin:~/bin:$PATH:~/Xtra/executables

alias lan='ssh u0_a154@192.168.1.102 -p 8022'
put() {if [ $1 ]; then if [ $2 ]; then dest="storage/downloads/$2"; else dest=""; fi; scp -v -P 8022 $1 u0_a154@192.168.1.102:/data/data/com.termux/files/home/$dest; fi;}
#alias kandor='ssh -i ~/.ssh/kandor/kandor.pem ubuntu@52.15.109.241'
#alias gpu_kandor='ssh -i ~/.ssh/kandor/kandor.pem ubuntu@18.118.112.95'
#get() {if [ $1 ]; then scp -v -i ~/.ssh/kandor/kandor.pem $1 ${HOME}/Kandor/Downloads/; fi;}
#put() {if [ $1 ]; then scp -v -i ~/.ssh/kandor/kandor.pem $1 ubuntu@13.59.150.56:/home/ubuntu/dev/; fi;}
#scp -v -i ~/.ssh/kandor/kandor.pem ubuntu@3.143.211.99:/home/ubuntu/writing/Grammar.pkl ./Grammar.pkl
#alias python=/usr/local/bin/python3.11
#alias pip=/usr/local/bin/pip3

alias speedtest="speedtest-cli --bytes"
alias start_ftp='echo Starting FTP at: $(ipconfig getifaddr en0); loc="/Volumes/Seagate Backup Plus Drive/Xtras/"; if [[ ! -d "$loc" ]] ; then loc="${HOME}/Movies/"; fi; python -m pyftpdlib --directory="$loc"'
#whatsmyip() {for line in `(curl -s https://get.geojs.io/v1/ip/geo$1.json) | tr -d "/\"{}" | tr " " "_" | tr "," " "` ; echo $line | sed 's/:/ : /g' | tr "_" " "}
whatsmyip() {python -c "import pandas as pd; import requests; print(pd.DataFrame().from_dict({'values' : requests.get('https://ipwhois.app/json/$1').json()}).drop(['success', 'continent_code', 'country_code', 'country_flag', 'country_neighbours', 'timezone_dstOffset', 'timezone_gmtOffset', 'currency_plural']).to_string(header = False))"}

alias download="aria2c --conf-path=${HOME}/.config/aria2.conf"
alias start_download_server="screen -dmS downloader aria2c --conf-path=${HOME}/.config/aria2.conf --enable-rpc=true --download-result=full"
loot() {if [ $2 ] ; then loc=$2; else loc="${HOME}/Downloads"; fi; curl http://127.0.0.1:6800/jsonrpc -H "Content-Type: application/json" -H "Accept: application/json" --data '{"jsonrpc": "2.0","id":1, "method": "aria2.addUri", "params":[['\"$1\"'], {"dir":'\"$loc\"'}]}'; }
alias stop_download_server="aria2p call shutdown"
alias manage_downloads='aria2p top'

alias rest='cd Xtra/rest; python cust_table.py; python rest.py; cd;'
alias rohtak='OPENSSL_CONF=Github/Scrappers/temp_openssl.cnf python Github/Scrappers/all_huda_scrapper.py'
alias huda25='OPENSSL_CONF=Github/Scrappers/temp_openssl.cnf python Github/Scrappers/huda_scrapper.py'
alias auctions='python Github/Scrappers/auctions.py'

alias circuit_check='python Github/Random/check_circuit.py'
alias natn='cp /usr/local/etc/tor/entry_exit.stock /usr/local/etc/tor/entry_exit; brew services restart tor'
alias intn='echo "">/usr/local/etc/tor/entry_exit; brew services restart tor'
#alias clean_tor='rm ${HOME}/Library/Application\ Support/TorBrowser-Data/Tor/state'

github_sync() {cp "${HOME}/.zshrc" "${HOME}/Github/Mac/zshrc"; cd "${HOME}/Github/"; for dir in */; do; echo ""; echo "==> $dir"; cd "$dir"; rm .DS_Store 2> /dev/null; git pull; git add . ; git reset -- .DS_Store; git commit -m 'Minor Changes!'; git push; cd ..; done; cd;}
#backup_torrent_files() { hdd="/Volumes/Seagate Backup Plus Drive"; tor_files="$hdd/Xtras/Torrent Files/"; qbt_loc="${HOME}/Library/Application Support/qBittorrent/BT_backup"; if mount | grep -q $hdd; then; cp $qbt_loc/*.torrent $tor_files; echo Backed up : $(ls $tor_files | wc -l); else; echo Drive NOT Mounted!!; fi;}
copy_torrent_files() { hdd="${HOME}/Downloads"; tor_files="$hdd/Shared/"; qbt_loc="${HOME}/Library/Application Support/qBittorrent/BT_backup"; cp $qbt_loc/$1*.torrent $tor_files; echo Copied : $(ls $tor_files | wc -l);}
alias dependencies_brew='brew leaves | xargs brew deps --for-each --tree | sed "s/ .*/$(tput setaf 1)&$(tput sgr0)/"'
alias mp3youtube="youtube-dl --extract-audio --audio-format mp3 --audio-quality 320K --ffmpeg-location ${HOME}/Github/Mac"

alias ips="cat ~/.ip_list"
alias vpn="networksetup -setsocksfirewallproxy wi-fi 127.0.0.1 9050; networksetup -setsocksfirewallproxystate wi-fi on; tor; networksetup -setsocksfirewallproxystate wi-fi off; networksetup -setsocksfirewallproxy wi-fi '' ''; "
alias proxy="export http_proxy='socks5://127.0.0.1:9050'; export https_proxy='socks5://127.0.0.1:9050'"
alias noproxy="export http_proxy=''; export https_proxy=''"
cache_handler() {setopt localoptions rmstarsilent; for loc in "${HOME}/Library/Caches/" "${HOME}/Library/Logs/"; do; du -sh $loc; if [ $1 ]; then rm -rf $loc/*; fi; done;}
alias translate='python Github/Mac/translate.py'
alias summary='python Github/Mac/summary.py'
alias clean_meta='exiftool -all:all= -r '
alias list_meta='exiftool -a '
alias tesseract='tesseract -c preserve_interword_spaces=1'
#Custom Commands End

#Old Commands
#alias walkman="sh ~/Github/Mac/walkman.sh"
#alias backup="python ~/Github/Mac/backup.py"
#alias news="sh ~/Github/Mac/news.sh"
#alias update="brew update; brew upgrade --ignore-pinned; brew cleanup; brew doctor"
alias wget="wget -P ~/Downloads/"
#Old Commands End

#zsh auto completion start
HISTFILE=${HOME}/.cache/zsh/zsh_history
autoload -Uz compinit 
compinit -d ${HOME}/.cache/zsh/zcompdump-$ZSH_VERSION
zstyle ':completion:*' menu select
eval "`pip completion --zsh`"
compdef gpg1=gpg
zstyle ':completion::complete:*' cache-path ${HOME}/.cache/zsh/.zcompcache/
# don't use autocompletion for git. it's slow as hell
compdef -d git

# Get fn+delete working in zsh
bindkey "^[[3~" delete-char

#zsh auto completion ends

#Bash Completion
[[ -r "/usr/local/etc/profile.d/bash_completion.sh" ]] && . "/usr/local/etc/profile.d/bash_completion.sh"

