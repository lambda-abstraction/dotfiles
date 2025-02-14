#!/bin/bash

CLASS="dropdown"

{
  read -r ADDRESS
  read -r WORKSPACE
} < <(hyprctl clients -j | jq -r '.[] | select(.class == "dropdown") | .address, .workspace.name')

if [ -n "$ADDRESS" ]; then
    if [[ "$WORKSPACE" == "special:special" ]]; then
        ID=$(hyprctl activeworkspace -j | jq '.id')
        hyprctl dispatch movetoworkspacesilent $ID,address:$ADDRESS
        hyprctl dispatch focuswindow address:$ADDRESS
    else
        hyprctl dispatch movetoworkspacesilent special,address:$ADDRESS
    fi
else
    kitty --class=dropdown
fi
