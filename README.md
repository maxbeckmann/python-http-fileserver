# python-http-fileserver

Usage (client side):
To upload `bethany.jpg` to http://192.168.119.198:8000/ from the current directory:

- Windows Powershell:
    `Invoke-RestMethod -Uri http://192.168.119.198:8000/bethany.jpg -Method Post -InFile bethany.jpg`

- Windows living-off-the-land binaries (https://lolbas-project.github.io/#/upload):
    (text/urlencoded only!) `CertReq -Post -config http://192.168.119.198:8000/bethany.jpg.txt bethany.jpg.txt`

- Linux shell:
    `curl --data-binary @bethany.jpg http://192.168.119.198:8000/bethany.jpg`
    `curl -F "file=@bethany.jpg" http://192.168.119.198:8000/`
