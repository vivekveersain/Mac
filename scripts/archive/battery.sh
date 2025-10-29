if [ "$(termux-battery-status | jq -r .plugged)" != "PLUGGED_USB" ]; then
  curl -d "$(termux-battery-status)" ntfy.sh/kaptaan;
fi

