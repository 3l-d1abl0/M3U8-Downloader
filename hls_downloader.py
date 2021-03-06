#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import ssl
import sys
import argparse
import urllib.request

class HlsDownloader(object):

    def parseM3U8(self) -> list:

        with open(os.path.join(self.output_dir, self.m3u8_master_file_name), 'r') as file:
            lines = file.readlines()

        #lines = [line.strip() for line in lines]
        iterable_obj = iter(lines)

        #list of bandwidth/resolution and source
        self.source_list = []
        while True:
            try:
                line = next(iterable_obj)
                line = line.strip().split("BANDWIDTH=")
                if len(line)==2:
                    self.source_list.append([line[1].split(",")[0], os.path.join(self.base_url, next(iterable_obj).strip())])

            except StopIteration:
                break

        if(self.source_list == []):
            print('No source found in the master file !')
            return []
        else:

            print('| Choose a source(s) to Download. Use comma to speerate multiple choices !\n')
            for idx, ele in enumerate(self.source_list):
                print("| {} --> BANDWIDTH = {}\n".format(idx, ele[0]))

            option =[]
            options_list = [i for i in range(len(self.source_list)) ]

            while HlsDownloader.checkOption(option, options_list) is False:
                option = input("\nEnter your choice : ")
                option = list( map(int, option.strip().split(",")) )

                if HlsDownloader.checkOption(option, options_list) is False:
                    print("Incorrect ! Choose the available option ! : ")
                else:
                    return option


    def getData(self) -> str:

        ssl._create_default_https_context = ssl._create_unverified_context
        site = urllib.request.urlopen(self.master_url)
        meta = site.info()

        #size in Bytes
        print( int(meta['Content-Length']) )

        with site as response:
            data = response.read()

        print('=> getData ', os.path.join(self.output_dir, self.m3u8_master_file_name))

        with open(os.path.join(self.output_dir, self.m3u8_master_file_name), 'wb') as file:
            file.write(data)


        return True


    def getSegments(self, option) -> None:

        #use when insecure ssl needed
        #ssl._create_default_https_context = ssl._create_unverified_context
        site = urllib.request.urlopen(self.source_list[option][1])
        meta = site.info()

        if not '?' in self.master_url :
            media_name = os.path.basename(self.source_list[option][1])
        else:
            media_name = os.path.basename(self.source_list[option][1]).split('?')[0]

        with site as response:
            data = response.read()

        with open(os.path.join(self.output_dir, os.path.basename(media_name)), 'wb') as file:
            file.write(data)

        media_ext =''
        with open(os.path.join(self.output_dir, os.path.basename(self.source_list[option][0]))+'.tmp', 'wb') as file:
            for line in data.splitlines():
                line = line.strip()

                extension = os.path.splitext(line)[1]
                extension = extension.lower().decode("utf-8").split("?")[0]

                if any(ext in extension for ext in ['.aac','.mp4','.ts']):
                    media_url = os.path.join(self.base_url, line.decode())
                    if media_ext == '':
                        media_ext = extension
                    print('--> ', media_url)
                    with urllib.request.urlopen(media_url) as response:
                                file.write(response.read())

        os.rename(os.path.join(self.output_dir, os.path.basename(self.source_list[option][0]))+'.tmp', os.path.join(self.output_dir, os.path.basename(self.source_list[option][0]))+str(media_ext))

    @staticmethod
    def checkOption(option, options_list) -> bool:

        if option ==[]:
            return False

        for op in option:
            if op not in options_list:
                return False

        return True

    @staticmethod
    def createFolder(path: str) -> bool:
        if not os.path.exists(path):
            try:
                os.mkdir(path)
            except Exception as e:
                print("{1}\n Failed to create folder {2}. Exiting !!!".format(e, path))
                return False

        return True

    @staticmethod
    def isValidUrl(url: str) -> bool:

        if url == '':
            print("URL ERROR : Empty String !")
            return False

        elif not '.m3u8' in url:
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
        '''
        self.output_dir
        self.m3u8_master_file_name
        '''
        print("Init HLS Class")

    def process(self) -> bool:
        self.base_url = os.path.dirname(self.master_url)
        if not '?' in self.master_url :
            self.m3u8_master_file_name = os.path.basename(self.master_url)
        else:
            self.m3u8_master_file_name = os.path.basename(self.master_url).split('?')[0]

        curPath = os.path.abspath(os.curdir)
        binDir = os.path.join(curPath, self.master_url.split('/')[-2])


        self.output_dir = os.path.join(os.path.abspath(os.curdir), self.master_url.split('/')[-2])

        if HlsDownloader.createFolder(self.output_dir) is True:
            print('reading File ... ')
            #read master file
            master_flag = self.getData()

            if master_flag is False:
                print("ERROR while handling m3u8 file !")
                exit(-1)
            else:   #process
                download_options = self.parseM3U8()

                if download_options == []:
                    print('Exiting !')
                    exit(-1)
                else:
                    print("Processing your option(s) : {}\n".format(download_options))

                    for val in download_options:
                        print(self.source_list[val][1])

                        self.getSegments(val)

                    print('-----------------')
        else:
            exit(-1)


if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-u", "--url", required=True, help="Url for the master m3u8 File !")
    args = vars(ap.parse_args())

    print(args["url"])

    m3u8_object = HlsDownloader(args["url"])
    if m3u8_object is None:
        print("Enter a valid m3u8 URL")
        exit(-1)
    else:
        print('Processing ... ', m3u8_object.master_url)
        m3u8_object.process()
