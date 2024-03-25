## About
Renames images according to the time created in their metadata
  
  Pass in a folder/file, and after confirming it will rename to follow this standard: YYYYMMDD_HHMMSS.heic

## Motivation

When exporting and backing up images from an iPhone, image filenames take the form IMG_XXXX.heic.
  
  This is annoying for a few reasons, so I wanted to convert them to follow the Android standard.

## Bugs

Timezones are really funny. I have used this tool to convert images from my DSLR while in Hong Kong, and the time in the metadata followed Canada.
  
  If you convert images where the timezone on the camera was incorrect, the date in the filename will be off by a few hours.
