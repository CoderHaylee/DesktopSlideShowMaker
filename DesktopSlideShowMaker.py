#!/usr/bin/env python2
import argparse
import random
import sys
import os
import shutil
import subprocess

#Sets up Vars for Yes and Invalid Chars
invalidChar = {"<":"LT",">":"GY;","&":"AND"}

#Sets up Parser
parser = argparse.ArgumentParser(description="A script for creating a desktop slideshow")
parser.add_argument("--destination", "-d", help="The place where the files will stored while "
	"beign your slide show (Default ~/.Background/)")
parser.add_argument("--source", "-s", help="The place where the pics are stored. (Default "
	"~/Pictures/Backgrounds)")
parser.add_argument("--duration", "-D", help="How long the pic stays up for. (Default 30)")
parser.add_argument("--shuffle", "-S", action="store_false", help="Shuffles the images into "
	"a random order on creation. (Default Yes)")
parser.add_argument("--GUI", "-g", action="store_true", help="Confirm closing, for GUI "
	"use. (Default False)")

def destination(parsed):
	#Figures the Destination
	if parsed.destination == None:
		backgroundLocal = os.path.expanduser("~/.Background/")
	else:
		backgroundLocal = parsed.destination
	if not os.path.isdir(backgroundLocal):
		print("Creating '{}'".format(backgroundLocal))
		os.mkdir(backgroundLocal)
	return backgroundLocal

def source(parsed):
	#Figures the source
	if parsed.source == None:
		sourceFiles = os.path.expanduser("~/Pictures/Backgrounds/")
	else:
		sourceFiles = parsed.source
	print("Pics located at: " + sourceFiles)
	return sourceFiles

def picList(sourceFiles):
	#Creates the list of pictures and gets the number of them
	try:
		pictureList = os.listdir(sourceFiles)
	except OSError:
		print(sourceFiles + " is not a valid folder.")
		sys.exit()
	picsFound = len(pictureList)
	return pictureList, picsFound

def picDur(parsed, picsFound):
	#Figures the duration of the slideshow.
	if parsed.duration == None:
		picDuration = "30"
	else:
		picDuration = parsed.duration
	print("Pic duration is: " + picDuration)
	slideShowLength = float(picsFound * int(picDuration))
	picDuration = int(picDuration)*60
	return picDuration, slideShowLength

def shuf(parsed, pictureList):
	#Shuffles if shuffle set
	if parsed.shuffle:
		random.shuffle(pictureList)
	print("Pic Shuffling is: " + str(parsed.shuffle))
	return pictureList

def XMLCreate(pictureList, sourceFiles, backgroundLocal, picDuration):
	#Creats the XML File for the slide show
	xmlEntry = []
	xmlEntry.append("<background>")

	for pics in pictureList:
		origPicPath = sourceFiles + "/" + pics
		for chars in list(invalidChar.keys()):
			if chars in pics:
				origPic = pics
				pics = pics.replace(chars,invalidChar[chars])
				print("Changing the file name of {} to {}".format(origPic, pics))
		picPath = backgroundLocal + pics
		shutil.copyfile(origPicPath,picPath)
		xmlEntry.append("    <to>{}</to>".format(picPath))
		xmlEntry.append("  </transition>")
		xmlEntry.append("  <static>")
		xmlEntry.append("    <duration>{}</duration>".format(picDuration))
		xmlEntry.append("    <file>{}</file>".format(picPath))
		xmlEntry.append("  </static>")
		xmlEntry.append("  <transition>")
		xmlEntry.append("    <duration>2.00</duration>")
		xmlEntry.append("    <from>{}</from>".format(picPath))
	xmlEntry.append("    <to>{}</to>".format(sourceFiles + pictureList[0]))
	xmlEntry.append("  </transition>")
	xmlEntry.append("</background>")
	xmlEntry.pop(1)
	xmlEntry.pop(1)
	xmlFile = "\n".join(xmlEntry)
	return xmlFile

def picWrites(backgroundLocal, xmlFile, slideShowLength, picsFound, pictureList):
	for pic in os.listdir(backgroundLocal):
		if pic not in pictureList:
			os.remove(backgroundLocal + pic)
	open(backgroundLocal + "Background.xml","w").write(xmlFile)
	subprocess.call(["gsettings", "set", "org.gnome.desktop.background", 
		"picture-uri", "'file://" + backgroundLocal + "Background.xml'"])
	slideShowLengthHour = float(slideShowLength / 60)
	slideShowLengthDay = float(slideShowLengthHour / 24)
	print("{} pictures have been turn into a {} minute ({} Hours, {} Days) "
		"Slide show".format(picsFound, slideShowLength, slideShowLengthHour, 
		slideShowLengthDay))

def main():
	parsed = parser.parse_args()
	backgroundLocal = destination(parsed)
	sourceFiles = source(parsed)
	pictureList, picsFound = picList(sourceFiles)
	picDuration, slideShowLength = picDur(parsed, picsFound)
	pictureList = shuf(parsed, pictureList)
	xmlFile = XMLCreate(pictureList, sourceFiles, backgroundLocal, picDuration)
	picWrites(backgroundLocal, xmlFile, slideShowLength, picsFound, pictureList)
	if parsed.GUI:
		raw_input("Press enter to close")

main()
