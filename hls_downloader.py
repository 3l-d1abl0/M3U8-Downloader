#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import urllib.request

class HlsDownloader(object):

    @staticmethod
    def isValidUrl(url: str) -> bool:
        if url == '':
            print("URL ERROR : Empty String !")
            return False

        elif os.path.splitext(url)[1].lower() != '.m3u8':
            print("URL ERROR : Not a hls/m3u8 master File !")
            return False

        elif not (url.startswith('https') or url.startswith('http')):
            print("URL ERROR : Url must be an http/https source !")
            return False
        else:
            return True
    
    def __new__(cls, url):

        if HlsDownloader.isValidUrl(url):
            return object.__new__(cls)
            #super(MyClass, cls).__new__(cls, url)

        return None

    def __init__(self, url):

        self.master_url = url
        print("Init HLS Class")


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--url", required=True, help="Url for the master m3u8 File !")
    args = vars(ap.parse_args())

    print(args["url"])
    
    m3u8_object = HlsDownloader(args["url"])
    if m3u8_object is None:
        print("Enter a valid m3u8 URL")
    else:
        print(m3u8_object.master_url)
    