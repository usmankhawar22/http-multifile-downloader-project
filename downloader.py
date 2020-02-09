import socket
import os,os.path
import threading
import time
import File_Merger


write_lock = threading.Lock()
def write_file(msg,fname,ftype,direct):
        os.chdir(direct)
        f = open(fname+'.' +ftype, 'ab')
        f.write(msg)
        f.close()
        
def write_file_new(msg,fname,ftype,direct):
        os.chdir(direct)
        f = open(fname+'.' +ftype, 'wb')
        f.write(msg)
        f.close()
        
def get_server_addess(site):
#procssing to string to sepearate server and address for http request
        if site.startswith('http://'):
                site = site[7:]
        server,address = site.split('/',1)
        address = '/' + address
        
        return (server,address)

def connect(server):
        #tcp connection establish
        cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (server,80)
        cs.connect(server_address)
        return cs

def byte_range_download(s,q,contentlength,address,server,cs,type1,folder,flname,byterange,total_bytes,i):
        if b'bytes' in s[b'Accept-Ranges']:
                        write_lock.acquire()
                        request = 'GET ' + address + ' HTTP/1.1\r\nHOST: ' + server + '\r\nRange:bytes=' + byterange + '\r\n\r\n'
                        request_header = bytes(request,'utf-8')  
                        cs.send(request_header)

                        byterange = byterange.split('-')
                        
                        if int(byterange[1])>contentlength:
                                flag = contentlength
                        full_msg = 0
                        new_msg= True
                        c=True
                        start = time.time()
                        bytesRecv = 0
                        while c:
                                msg = cs.recv(15000)    
                                if new_msg:
                                        head = msg.split(b'\r\n\r\n')
                                    
                                        msg = head[1]
                                        
                                        new_msg = False
                                
                                full_msg += len(msg)
                                if len(msg) ==0:
                                        write_lock.release()
                                        c=False
                                        new_msg = True
                                        break
                                write_file(msg,flname,type1,folder)
                                bytesRecv +=len(msg)
                                total_bytes +=len(msg)
                                

                                if (time.time()- start >= i):
                                        print(flname+"Download speed = ", (bytesRecv/(time.time()-start))/1024 ,'kB/sec')  

                                        print("% Download Completion = ", (total_bytes/contentlength)*100)
                                        start = time.time()
                                        bytesRecv = 0
                                
                                if full_msg== int(byterange[1])+1-int(byterange[0]):
                                        write_lock.release()
                                        new_msg = True
                                        full_msg =0
                                        c= False
                
def download_file(site,download_dir,filename,rflag,q,i):

        server,address = get_server_addess(site)
        cs = connect(server)

        #generating request and sending to know length of data
        request = 'HEAD ' + address + ' HTTP/1.1\r\nHOST: ' + server +'\r\n\r\n'
        request_header = bytes(request,'utf-8') 
        cs.send(request_header)
        
        #processing header to find content length of file to be downloaded
        header = cs.recv(4096)
        header = header.split(b'\r\n')
        
        s = {}
        for h in range(1,len(header)-2):
            y = header[h].split(b':')
            s[y[0]] = y[1]


        contentlength = int(s[b'Content-Length'])
        type1 = s[b'Content-Type'].split(b'/')[1]
        type1 = str(type1,'utf-8')

        #if file is resumable
        if b'Accept-Ranges' in s:
                startbyte = 0
                endbyte = contentlength//q
                threads_list = []
                for h in range(q):
                        byterange = "%s-%s"%(startbyte,endbyte)
                        name = filename+str(h)
                        resume_flag = File_Merger.getFileSize(name+'.'+type1,download_dir)
                        if rflag:
                                if resume_flag-1 == endbyte-startbyte or resume_flag-1 ==contentlength%(contentlength//q):
                                        print( name, 'Completely Donwloaded' )
                                        startbyte = endbyte+1
                                        endbyte += contentlength//q
                                        
                                        continue
                                elif resume_flag !=0:
                                        print(name,"Partially Downloaded")
                                        startbyte = resume_flag
                                      
                        t = threading.Thread(target = byte_range_download , name = name , args = (s,q,contentlength,address,server,cs,
                                                                                                  type1,download_dir,name,byterange,startbyte,i))
                        startbyte = endbyte+1
                        endbyte += contentlength//q
                        threads_list.append(t)
                        t.start()
                for t in threads_list:
                        t.join()
                cs.close()
                #mergin all the downloaded chunks into one file
                File_Merger.mergeFiles(q, filename,type1 ,download_dir)
                print(filename, ' done')

        else:   #if file is not resumable
                if rflag:
                        print('Download resumtion not allowed')
                request = 'GET ' + address + ' HTTP/1.1\r\nHOST: ' + server + '\r\n\r\n'
                
                request_header = bytes(request,'utf-8')  
                cs.send(request_header)

                full_msg = b''
                new_msg= True
                c=True
                #variables for metrics
                total_time = time.time()
                start = time.time()
                bytesRecv = 0
                filesize=0
                while c:
                    msg = cs.recv(4096)
                            
                    if new_msg :
                        head = msg.split(b'\r\n\r\n')
                        header=(len(head[0]))+4
                        msg = head[1]
                        new_msg = False
                    #full_msg += msg
                    bytesRecv += len(msg) 
                    filesize += len(msg)
                    #calculating metric
                    if (time.time()-start) >= i:
                            print(filename,"Download speed = ", (bytesRecv/(time.time()-start))/1024)
                            print(filename,"% Download Completion = ", (filesize/contentlength)*100)
                            start = time.time()
                            bytesRecv = 0
                    write_file(msg,filename,type1,download_dir)
                #breaking the loop if full file is recieved
                    if filesize== contentlength:
                        print(filename, "% Download Completion = ", (filesize/contentlength)*100)
                        print(filename,"Total Download speed = ", (filesize/(time.time()-total_time))/1024)
                        new_msg = True
                        #write_file(msg,filename,type1,download_dir)
                        full_msg = ""
                        filesize = 0
                        c= False
                        cs.close()         

                

                

#site = 'http://open-up.eu/files/Berlin%20group%20photo.jpg'

#ddir= "C:\project"
#download_file(site,ddir,'Cat',True,1,0.5)
