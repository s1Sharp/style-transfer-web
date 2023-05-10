#!/bin/bash

while getopts s:d:k: option
do 
    case "${option}"
        in
        s)SRC_FILE=${OPTARG};;
        d)DST_FILE=${OPTARG};;
        k)KEY=${OPTARG};;
    esac
done


# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$KEY" \
--output $DST_FILE $SRC_FILE
