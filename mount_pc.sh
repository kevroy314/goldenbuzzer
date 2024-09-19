read -s -p "Password: " password
sudo mount -t cifs //192.168.2.4/Users/kevin /mnt/desktop -o username=kevin.horecka@gmail.com,password=$password
