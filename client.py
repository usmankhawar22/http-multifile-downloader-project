import sys
import downloader

#This whole code is for CLi arguments and for downloading those files  
inputargs = {}
sites = []
ddir = []

if '-r' in sys.argv:
    i=2
    r=True
else:
    i=1
    r=False
print(sys.argv)
while i < sys.argv.index('-f'):
       inputargs[sys.argv[i]] = float(sys.argv[i+1])
       i+=2
       
xy = sys.argv.index('-f')
xye = int(inputargs['-nf'])

print(inputargs)
print(sys.argv)
name = [] 
for zxy in range(xye):
        sites.append(sys.argv[xy+zxy+1])
        ddir.append(sys.argv[xy+zxy+2+xye])
        name.append('File'+str(zxy))
        
print(inputargs)
for i in range(len(sites)):
       downloader.download_file(sites[i],ddir[i],name[i],r,
                                         int(inputargs['-n']),inputargs['-i'])


