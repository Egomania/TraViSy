#!/bin/bash

ssh $1@$2 "tcpdump -i "$3" -s 0 -U -w - not port 22" > $4

