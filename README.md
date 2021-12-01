# prnt.sc scraping
simple script that scrapes prnt.sc

## what
prnt.sc is a free and anonymous image hosting site that is very openly public. the script will access random prnt.sc IDs and donwload the images to disk.

the images saved are named after the ID they were retrieved from. the script will automatically skip invalid images, such as ones with deleted imgur links or deleted sources.

you can occasionally find some interesting images, but most of the time, you will find screen captures of video games in other languages. i have included a few examples that i thought were interesting.

## requirements

`pip3 install requests bs4`
