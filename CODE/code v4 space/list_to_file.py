a_list = [2.0,3.0]
a_list = str(a_list)
textfile = open("gps_file.txt", "w")
for element in a_list:
    textfile.write(element + "\n")
textfile.close()