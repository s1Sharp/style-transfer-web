#!/bin/bash

while getopts s:k: option
do   
    case "${option}"
        in
        s)SRC_FILE=${OPTARG};;
        k)KEY=${OPTARG};;
    esac
done


# Decrypt the file
# --batch to prevent interactive command
gpg --symmetric --quiet --batch --passphrase $KEY \
--cipher-algo AES256 $SRC_FILE
