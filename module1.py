import os
from os.path import expanduser
home = expanduser("~")
path_file=home+"/.bash_history"
path_script=home+"/module1"
path_bashrc=home+"/.bashrc"
path_hot_file=home+"/.test-folder/.test_count"
path_beginned_n=home+"/.test-folder/.hot_file"
path_beginned_file=home+"/.test-folder/.start_status"	#0 or 1
path_score_file=home+"/.test-folder/.score"
path_overview=home+"/.test-folder/.overview.txt"
path_my_file=home+"/my-file"
os.system("mkdir .test-folder 2> stderr")
os.system("ls "+path_beginned_n+" 2>"+home+"/.stderr | wc -l >"+path_beginned_file)
check=open(path_beginned_file,"r")
check_status=str(check.read().strip())
check.close()

if check_status=='0':
    os.system("touch "+path_beginned_n)
    os.system("echo 1 >"+path_hot_file)
    os.system("echo 0 >"+path_score_file)
    print("1-savol. hozirda siz turgan direktoriyani ekranga chiqarish komandasi: ")
    os.system("echo '1-savol. hozirda siz turgan direktoriyani ekranga chiqarish komandasi: ' >> "+path_overview)		#new2
    with open(expanduser("~/.bashrc"), "at") as bashrc:
        bashrc.write(
            "\n"
            "shopt -s histappend\n"
            'PROMPT_COMMAND="history -a;$PROMPT_COMMAND"\n'
            "# Added by myprogram on somedate\n"
            "alias ok='./module1'\n"
        )
    os.system("/bin/bash")
    
elif check_status=='1':
    check_test=open(path_hot_file,"r")
    check_test_status=check_test.read().strip()
    check_test.close()
    check_score=open(path_score_file,"r")
    score=int(check_score.read().strip())
    check_score.close()

#1
    if check_test_status=='1':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="pwd":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 2 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("2-savol. tree komandasi yordamida ushbu / direktoriyaning ikki qatlamini aks ettiring:")
        os.system("echo '2-savol. tree komandasi yordamida ushbu / direktoriyaning ikki qatlamini aks ettiring:' >> "+path_overview)		#new2
#2
    elif check_test_status=='2':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        #if his=="tree -L 2 /":
        if ("tree" in his) and ("-L 2" in his) and ("/" in his):
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 3 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        #print("baho:",score)
        print("3-savol. packetlar royxati(apt list)ni less komandasi orqali ekranda chiqaring: ")
        os.system("echo '3-savol. packetlar royxati(apt list)ni less komandasi orqali ekranda chiqaring:' >> "+path_overview)		#new2

#3
    elif check_test_status=='3':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="apt list | less" or his=="apt list |less" or his=="apt list|less":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 4 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("4-savol. /tmp da file1 file2 va file3 deb nomlangan fayllar yarating(cd va ; ishlatish mumkin emas):")
        os.system("echo '4-savol. /tmp ichiga file1 file2 va file3 deb nomlangan fayllar yarating(cd va ; ishlatish mumkin emas):' >> "+path_overview)		#new2

#4
    elif check_test_status=='4':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="touch /tmp/file1 /tmp/file2 /tmp/file3":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 5 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("5-savol. /run direktoriyasidagi file,papkalar va yashirin(hidden) fayllarni royxatini chiqaring:")
        os.system("echo '5-savol. /run direktoriyasidagi file,papkalar va yashirin(hidden) fayllarni royxatini chiqaring:' >> "+path_overview)		#new2

#5
    elif check_test_status=='5':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        #os.system("echo "+his)
        #if his=="ls -lah /run" or his=="ls -lha /run" or his=="ls -la /run" or his=="ls -a /run" or his=="ls -lah /run/" or his=="ls -lha /run/" or his=="ls -la /run/" or his=="ls -a /run/": 
        if ("ls" in his) and ("-" in his) and ("a" in his) and ("/run" in his):
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 6 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("6-savol. /tmp da bir/ikki/uch ichma ich folder yarating(cd va ; ishlatish mumkin emas):")
        os.system("echo '6-savol. /tmp ichiga bir/ikki/uch ichma ich folder yarating(cd va ; ishlatish mumkin emas):' >> "+path_overview)		#new2

#6
    elif check_test_status=='6':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="mkdir -p /tmp/bir/ikki/uch":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 7 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("7-savol. /etc papkani ichidagi hamma narsasi bilan /tmp papkaga kopirovat qiling:")
        os.system("echo '7-savol. /etc papkani ichidagi hamma narsasi bilan /tmp papkaga kopirovat qiling:' >> "+path_overview)		#new2

#7
    elif check_test_status=='7':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="cp -r /etc /tmp" or his=="cp -r /etc/ /tmp" or his=="cp -r /etc /tmp/" or his=="cp -r /etc/ /tmp/":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 8 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("8-savol. /etc papkadan arxiv oling, etc.tar.gz nomlangan filega")
        os.system("echo '8-savol. /etc papkadan arxiv oling, etc.tar.gz nomlangan filega' >> "+path_overview)		#new2

#8
    elif check_test_status=='8':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        #if his=="tar cfz etc.tar.gz  /etc" or his=="tar cfz etc.tar.gz  /etc" or his=="tar czf etc.tar.gz  /etc" or his=="tar czf /etc.tar.gz  /etc":
        if ("tar" in his) and ("c" in his) and ("f" in his) and ("z" in his) and ("etc.tar.gz" in his) and ("/etc" in his):
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 9 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("9-savol. gzip deb nomlangan packetni obnavleniya(upgrade) qilishdan olib tashlash:")
        os.system("echo '9-savol. gzip deb nomlangan packetni obnavleniya(upgrade) qilishdan olib tashlash:' >> "+path_overview)		#new2

#9
    elif check_test_status=='9':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="apt-mark hold gzip":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 10 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("10-savol.useradd bilan istalgan nom bilan user yaratish , home direktoriyasi bilan, shell /bin/bash ")
        os.system("echo '10-savol.useradd bilan istalgan nom bilan user yaratish , home direktoriyasi bilan, shell /bin/bash' >> "+path_overview)		#new2

#10
    elif check_test_status=='10':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if ("useradd" in his) and ("-m" in his) and ("-s" in his) and ("/bin/bash" in his):
            #os.system("echo "+his)
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 11 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("11-savol./etc direktoriyasi ichidan os-release deb nomlangan faylni, find komandasi orqali  izlash ")
        os.system("echo '11-savol./etc direktoriyasi ichidan os-release deb nomlangan faylni, find komandasi orqali  izlash' >> "+path_overview)		#new2

#11
    elif check_test_status=='11':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if "find" and "/etc" and "-name" and "os-release" in his:
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 12 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("12-savol. hozirda sistemaga ulangan userlay royxatini chiqarish ")
        os.system("echo '12-savol. hozirda sistemaga ulangan userlay royxatini chiqarish' >> "+path_overview)		#new2

#12
    elif check_test_status=='12':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="w" or his=="who":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 13 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        os.system("touch "+path_my_file)
        print("13-savol. ~/my-file ni userini root ga ozgartirish:")
        os.system("echo '13-savol. ~/my-file ni userini root ga ozgartirish:' >> "+path_overview)		#new2

#13
    elif check_test_status=='13':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        his2="chown root "+path_my_file
        if his=="chown root ~/my-file" or his=="chown root my-file" or his==his2:
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 14 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("14-savol. ~/my-file ga 555 ruxsatni harflar orqali berish:")
        os.system("echo '14-savol. ~/my-file ga 555 ruxsatni harflar orqali berish:' >> "+path_overview)		#new2

#14
    elif check_test_status=='14':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        his2="chmod ugo=rx "+path_my_file
        his3="chmod a=rx "+path_my_file
        if his=="chmod ugo=rx ~/my-file" or his=="chmod a=rx ~/my-file" or his==his2 or his==his3 or his=="chmod ugo=rx my-file" or his=="chmod a=rx my-file":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 15 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("15-savol. ~/my-file ga r-xr-xr-- ruxsat raqamlar orqali bering:")
        os.system("echo '15-savol. ~/my-file ga r-xr-xr-- ruxsat raqamlar orqali bering:' >> "+path_overview)		#new2

#15
    elif check_test_status=='15':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        his2="chmod 554 "+path_my_file
        if his=="chmod 554 ~/my-file" or his=="chmod 554 my-file" or his==his2:
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 16 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("16-savol. barcha jarayonlar orasidan ssh ni grep filteri orqali ekranga chiqaring:")
        os.system("echo '16-savol. barcha jarayonlar orasidan ssh ni grep filteri orqali ekranga chiqaring:' >> "+path_overview)		#new2
#16
    elif check_test_status=='16':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if "ps" and "grep ssh" in his:
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 17 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("17-savol. systemd orqali network-manager xizmatini holatini tekshiring:")
        os.system("echo '17-savol. systemd orqali network-manager xizmatini holatini tekshiring:' >> "+path_overview)		#new2

#17
    elif check_test_status=='17':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if "systemctl" and "status" and "network-manager" in his:
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 18 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("18-savol. ed25519 algoritmi orqali ssh kalit yarating:")
        os.system("echo '18-savol. ed25519 algoritmi orqali ssh kalit yarating:' >> "+path_overview)		#new2

#18
    elif check_test_status=='18':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="ssh-keygen -t ed25519":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 19 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("19-savol. super user orqali krontabni edit qilish comandasini yozing: ")
        os.system("echo '19-savol. super user orqali krontabni edit qilish comandasini yozing:' >> "+path_overview)		#new2

#19
    elif check_test_status=='19':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        if his=="sudo crontab -e":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 20 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("20-savol. 30025 id ga ega bo'lgan jarayonni 'zudlik' bilan to'xtatish komandasini yozing:")
        os.system("echo '20-savol. 30025 id ga ega bo'lgan jarayonni 'zudlik' bilan to'xtatish komandasini yozing:' >> "+path_overview)		#new2

#20
    elif check_test_status=='20':
        with open(path_file, "r") as file:
            first_line = file.readline()
            for last_line in file:
                pass
        his=last_line.strip()
        os.system("echo 'sizning javobingiz:' >> "+path_overview)		#new
        os.system("echo "+his+" >> "+path_overview)				#new
        his=his.replace("sudo ","")
        if his=="kill -9 30025":
            score+=3
            os.system("echo 'Ball : 3' >> "+path_overview)			#new3
        else:
            score+=0
            os.system("echo 'Ball : 0' >> "+path_overview)			#new3
        os.system("echo 21 >"+path_hot_file)
        score_file=open(path_score_file,"w")
        score_file.write(str(score))
        score_file.close()
        print("\n")
        os.system("cat "+path_overview)
        print("\n")
        print("Umumiy Ball:",score)
