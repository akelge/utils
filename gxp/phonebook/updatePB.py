#!/usr/bin/python

output = '<?xml version="1.0"?>\n<AddressBook>\n'

print "--------------------------------------------------------------"
print "Generate CUBE GXP-2000 Phonebook"
print "--------------------------------------------------------------"

counter = 0
f = open('phonebook.csv','r')
for line in f:
    line = line.replace('\n','')
    r = line.split(',')
    output+='<Contact>\n'
    output+='\t<LastName>%s</LastName>\n'%r[0].strip()
    #output+='\t<FirstName>%s</FirstName>\n'%r[0].strip()
    output+='\t<Phone>\n\t\t<phonenumber>%s</phonenumber>\n'%r[1].strip()
    output+='\t\t<accountindex>0</accountindex>\n\t</Phone>\n'
    output+='</Contact>\n'
    counter+=1

output+='</AddressBook>'
f.close()

f = open('gs_phonebook.xml','w')
f.write(output)
f.close()

print "%s entries" % counter
print "phonebook created > gs_phonebook.xml"
