# FuzzTheREST
A Black-Box RESTful API Fuzzer


# FTP Server for file upload in UI 
docker build -t ftp-server .
docker run -d  -p 21:21 -p 21000-21010:21000-21010 -e USERS="admin|admin123|/srv/ftp" delfer/alpine-ftp-server
