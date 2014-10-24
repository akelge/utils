#!/bin/bash

# only node names
# wget -O ~/.ssh/known_hosts "http://docs.syspay.com/modules/network/external/node_info.php?password=password&format=nameonly"

# dns names A + CNAMES

# Syapay
wget -q -O ~/.ssh/syspaydns --post-data "password=password&domain=internal#syspay.com" "http://docs.syspay.com/modules/network/external/api_node_autocomplete.php"
cat ~/.ssh/syspaydns | sort > ~/.ssh/config

# DNX
#for Domain in internal#neteden.fr;do
for Domain in internal#neteden.fr internal#tac.priv internal#dating.priv internal#market.priv;do
	wget -q -O ~/.ssh/netedendns --post-data "password=password&domain=$Domain" "http://docs.neteden.fr/modules/network/external/api_node_autocomplete.php"
	cat ~/.ssh/netedendns | sort >> ~/.ssh/config
done

sed -i 's/^/Host /' ~/.ssh/config
