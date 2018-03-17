import os
import csv
import shutil
import time

# Path where data.bin (from Touch Detective 1, maybe other games?) file is        
basePath = ".\\"

class Subfile:

    def __init__(self, index=-1, offset=-1, size=-1, path=""):
        self.index = index #zero-based index
        self.offset = offset #offset of subfile inside data.bin, base dec
        self.size = size # size of subfile, in bytes, according to pointer table
        self.path = path #'Workspace' folder path, each subfile will have it's own workspace

    def readBytesFromDataBin(self, file):
        file.seek(self.offset)
        self.byteString = file.read(self.size)           
        
    def getBytes(self):
        return self.byteString

    def exportToWorkspaceFolder(self, baseLocation):
        self.path = "{}\\bin_subfiles\\{}".format(baseLocation, '{:0>5}'.format(self.index))
        if not os.path.exists(self.path):
            os.makedirs(self.path)

        #Write binary data file
        dataFilePath = "{}\\{}.data".format(self.path, self.index)
        dataFile = open(dataFilePath, "wb")       
        dataFile.write(self.byteString)
        dataFile.close()

        #Write metadata file
        metaFilePath = "{}\\{}.metadata".format(self.path, self.index)
        metaFile = open(metaFilePath, "w")
        metaFile.write("0-index,{}\n".format(self.index))
        metaFile.write("offset,{}\n".format(self.offset))
        metaFile.write("size,{}\n".format(self.size))
        metaFile.write("path,{}\n".format(metaFilePath))
        metaFile.close()        

    def writeBytesIntoDataBin(self, file):
        file.seek(self.offset)
        file.write(self.byteString)

# Returns next divisible by 4 integer. If integer is already divisible by 4
# it is simply returned.
# This is needed to calculate valid offsets.
def nextMultipleOf4(integer):
    if 0 == integer & 0x03:
        return integer
    else:
        return (integer | 0x03) + 1

# build a character string with the amount first bytes of a bytearray
def prettyPrintBytes(byteArr, amount):
    if (len(byteArr) < amount):
        amount = len(byteArr)        
    charList = []
    for i in range(0, amount):        
        intval = byteArr[i]
        if (intval == 44):
            charList.append('.')
        elif (intval < 32):
            charList.append('.')
        elif (intval > 126):
            charList.append('.')
        else:
            charList.append(chr(byteArr[i]))        

    return ''.join(charList)
    

# Sets up the working environment, creating a subfolder for each subfile
def unpack():
    # Open data.bin, get subfile count (number of entries in the pointer table)
    binData = open("{}\\data.bin".format(basePath),"rb")
    print("data.bin file opened")
    sfCount = int.from_bytes(binData.read(4), byteorder='little', signed=False)    
    
    # Iterate the pointer table, each new Subfile object will keep track of each subfile location and size
    print("Found {} entries in pointer table, building metadata ...".format(sfCount))
    subfiles = []
    for i in range(0, sfCount):
        #Offsets are divided by 4, all of them must be bit-shifted <<2 to read the actual offset value 
        sfOffset = int.from_bytes(binData.read(4), byteorder='little', signed=False)<<2
        sfSize = int.from_bytes(binData.read(4), byteorder='little', signed=False)
        subfiles.append(Subfile(i, sfOffset, sfSize, ""))    
    # end pointer table iteration
    print("\t ...done.")
    
    # Create subfolder 'bin_subfiles' and the workspace folders within
    print("Building {} workspace folders ...".format(sfCount))

    csvFilePath="{}\\binSubFiles.csv".format(basePath)
    csvFile = open(csvFilePath, "w")
    csvFile.write("0-index,offset,size,path,preview\n")
    
    for i in range(0, sfCount):
        subfiles[i].readBytesFromDataBin(binData)
        subfiles[i].exportToWorkspaceFolder(basePath)
        #Store metadata in database for later        
        csvFile.write("{},{},{},{},{}\n".format(i, subfiles[i].offset, subfiles[i].size, subfiles[i].path, prettyPrintBytes(subfiles[i].getBytes(), 16)))        

    csvFile.close()
    print("\t ...done.")
    
    binData.close()
    print("data.bin file closed. Done.")

# Recreates the data.bin with the workspace folders' .data files. It will not
# overwrite the original file, but create a new one with a timestamp as extension.
def repack():
    # Open data.bin, get subfile count (number of entries in the pointer table)
    binData = open("{}\\data.bin".format(basePath),"rb")
    print("data.bin file opened")
    sfCount = int.from_bytes(binData.read(4), byteorder='little', signed=False) 
    binData.close()
    print("Found {} entries in pointer table. data.bin file closed.".format(sfCount))

    #Iterate bin_subfiles folders, create subfiles object array with subfile metadata 
    print("Building subfile workspace in-memory registry (from filesystem)...")
    workfolderNames = next(os.walk('{}\\bin_subfiles'.format(basePath)))[1]

    subfiles = []
    # "previous" size&offset variables for dynamic offset calculation based on previous subfile
    previousSize = sfCount * 8 + 4 # pointer table size
    previousOffset = 0 # pointer table's offset
    for wfn in workfolderNames:
        #Locate each workfolder complete path
        wfPath = "{}\\bin_subfiles\\{}".format(basePath, wfn)
        #Read bytes & size from .data file within
        wDataFilePath = "{}\\{}.data".format(wfPath, wfn.lstrip('0'))
        wDataFile = open(wDataFilePath, "rb")
        wDataBytes = wDataFile.read()
        wDataFile.close()
        sizeFromBytes = len(wDataBytes)
        #Read size from .metadata file
        wMetaFile = open("{}\\{}.metadata".format(wfPath, wfn.lstrip('0')),"r")
        sizeDataLine = wMetaFile.readlines()[2]        
        wMetaFile.close()
        sizeFromMetadata = int(sizeDataLine.lstrip('size,'))
        #Size check
        if sizeFromBytes < sizeFromMetadata:
            #xxx.data is smaller, padding to meet sizeFromMetadata will be necessary
            wDataBytes = wDataBytes.ljust(sizeFromMetadata, b'\x00')
        wDataSize = len(wDataBytes)
        
        #Offset calculation, previous file offset + size, must also be mult. of 4
        wDataOffset = nextMultipleOf4(previousOffset + previousSize)

        #Instance new Subfile() to keep track of all this metadata
        sfInstance = Subfile(int(wfn) - 1, int(wDataOffset), int(wDataSize), wfPath)
        sfInstance.byteString = wDataBytes
        subfiles.append(sfInstance)        

        #Remember size & offset of this subfile for next iteration
        previousSize = wDataSize
        previousOffset = wDataOffset
        
    print("... Done.")  
    
    #Write timestamped data.bin
    repackdDataBinPath = "{}\\data.bin.{}".format(basePath, time.strftime('%Y%m%d'))
    repackdDataBin = open(repackdDataBinPath, "wb")
    print("Writing on new file {}...".format(repackdDataBinPath))

    #Write fileCount
    print("Writing file count...")
    repackdDataBin.write(sfCount.to_bytes(4, byteorder='little', signed=False))
    
    #Write file pointer table
    print("Writing {} pointer table entries...".format(sfCount))
    for x in range(sfCount):
        littleEndianAndShiftedOffset = (subfiles[x].offset>>2).to_bytes(4, byteorder='little', signed=False)
        repackdDataBin.write(littleEndianAndShiftedOffset)
        littleEndianSize = subfiles[x].size.to_bytes(4, byteorder='little', signed=False)
        repackdDataBin.write(littleEndianSize)        

    #Write each subfile bytes
    print("Writing {} subfiles...".format(sfCount))
    for sf in subfiles:
        repackdDataBin.seek(sf.offset)
        repackdDataBin.write(sf.byteString)        
        
    repackdDataBin.close()
    print("... Done.")
    print("File {} is ready.".format(repackdDataBinPath))
