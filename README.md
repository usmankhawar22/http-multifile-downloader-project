# http multifile downloader project
 
Summary 
Server setup:
Server is setup using local host on apache; which is integrated in Zamp. The server is accessed through local-id 127.0.0.1 as a virtual host.

Techniques used for download:
The requesting header for any website is sent using the HTTP HEAD request, the HTTP response in the field accept-ranges is recorded. (which is either none or BYTE)

Download Using Multiple Connections
If the server accepts byte ranges, multiple connections are invoked which are then merged at the completion at the end of download in one file.  Use of threading and OS libraries of python is used
Else only single a connection is invoked if the server doesn’t support threading.
Downloading Multiple files:
For downloading multiple files we obtain the server addresses from the user and pass them into a list from where the files are downloaded sequentially.
Download Resuming:
Incase a download is interrupted and in the subsequent request user turns on the download resumption flag (-r) then we read the files if present in the download directory and start download from after those bytes which have already been downloaded from the server. This resumption function if only possible if the server supports byte ranges otherwise the file will be downloaded from scratch.
Conclusion
The developed project is fully supporting the implemented functionality. All the required constraints are implemented in the project. Domain knowledge of HTTP, sockets, Threading and its required integration with python is the best outcome of the project.

