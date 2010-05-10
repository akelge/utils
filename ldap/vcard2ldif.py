#!/usr/bin/env python
#-*- coding: latin-1 -*-

import sys, re, time

def isvalidEntry(entry):
    # Standard keys in VCF Version 3
    #FN|N|NICKNAME|PHOTO|BDAY|ADR|LABEL|TEL|EMAIL|MAILER|TZ|GEO|TITLE|ROLE|LOGO|AGENT|
    #ORG|CATEGORIES|NOTE|PRODID|REV|SORT\-STRING|SOUND|URL|UID|CLASS|KEY
    if (not(re.match('^(?:FN|N|BDAY|ADR|TEL|EMAIL|ORG)',entry))): return False
    return True

def debugprint(value):
    if debug: print value

### USAGE #####################
try:
    vcfFile = sys.argv[1]
    ldifFile = sys.argv[2]
    templateFile = sys.argv[3]
except:
    print "USAGE: vcard2ldif.py vcfFile ldifFile templateFile"
    sys.exit()
##############################

debug = False


### LOAD TEMPLATE ############
template = []
tpl=open(templateFile,'r+')
for line in tpl:
    item = ['','']
    match = re.search('{{([^}]+)}}',line)
    if match: item[1] = match.groups()[0]
    line = re.sub('{{[^}]+}}','$VAR',line)
    line = re.sub('[\n\r]','',line)
    item[0] = line
    template.append(item)
tpl.close()
##############################

print "------------------------------------------------------------"
print "PARSING VCF \"%s\"" % vcfFile

vcf=open(vcfFile, 'r+')

entries = []
onvcard = False # lines between begin and end
hasmail = False
hasphone = False
iscompany = False
countervcf = 0

for line in vcf:
    line = line.strip()
    if line == 'BEGIN:VCARD':
        entry = {}
        onvcard = True
        hasmail = False
        hasphone = False
        iscompany = False
        debugprint('------------------------------------------------------------')
    if line == 'END:VCARD':
        entry[':ISCOMPANY'] = iscompany
        entry[':HASPHONE'] = hasphone
        entry[':HASMAIL'] = hasmail
        for key in sorted(entry.iterkeys()):
            debugprint("%s = %s" % (key, entry[key]))
        print " > %s" % entry['FN']
        countervcf +=1
        entries.append(entry)
        entry = None
        onvcard = False
    if onvcard:
        line = re.sub('^item\d+\.','',line)
        s = re.search('^([^:;]+)((?:\;type=[^;]+)*)\:(.+)$',line)
        key,types,values = (None,None,None)
        if s and isvalidEntry(line):
            key = s.groups()[0]
            types = s.groups()[1].replace('pref','').replace(';type=',' ').strip().replace(' ',':')
            values = s.groups()[2].replace('\\n','').replace('\\','')

            # FIRST CLEAN

            if key == 'N':
                if not values.replace(';','').strip():
                    iscompany = True
                    values = ''
                else:
                    entry['N:SURNAME'] = values.split(';')[0]
                    entry['N:NAME'] = values.split(';')[1]
                    values = "%s, %s" % (entry['N:SURNAME'],entry['N:NAME'])
            elif key == 'ORG':
                values = re.sub('(^;+|;+$)','',values)
                values = re.sub('[;]+',', ',values)
            elif key == 'ADR':
                address = values.split(';')
                try: entry['ADR:STREET'] = address[2]
                except: pass
                try: entry['ADR:CITY'] = address[3]
                except: pass
                try: entry['ADR:STATE'] = address[4]
                except: pass
                try: entry['ADR:ZIP'] = address[5]
                except: pass
                try: entry['ADR:COUNTRY'] = address[6]
                except: pass
                values = re.sub('(^;+|;+$)','',values)
                values = re.sub('[;]+',', ',values)
            else:
                values = values.split(';')
                if len(values) == 1: values = values[0]

            # SECOND CLEAN

            if key == 'TEL':
                values = values.replace(" ","").replace("-","").replace(".","")
                hasphone = True
            if key == 'MAIL': hasmail = True
            if key == 'FN':
                values = values.replace(',','')
                uid = re.sub('[^a-z]','',values.lower())
                entry['UID'] = "%s%s" % (uid,int(time.time()%int(time.time())*100000))
            if types:
                key = "%s:%s" % (key,types)
            entry[key] = values

vcf.close()
print "Done %s VCF entries" % countervcf
print "------------------------------------------------------------"
print "WRITING LDIF \"%s\"" % ldifFile

ldif=open(ldifFile, 'w+')
counterldif=0

### OPEN LDIF
for entry in entries:
    for tline in template:
        skipline = False
        line = tline[0]
        replaceArray = tline[1]
        if replaceArray != "":
            replaceArray = replaceArray.split('|')
            torepl = ""
            for replaceEl in replaceArray:
                if not replaceEl:
                    skipline = True
                    break #for
                torepl = entry.get(replaceEl)
                if torepl: break #for
            if not skipline:
                if not torepl: torepl = ""
                line = line.replace("$VAR",torepl)
                debugprint(line)
                ldif.write("%s\n" % line)
        else:
            debugprint(line)
            ldif.write("%s\n" % line)
        if line.startswith('dn:'): print " > %s" % line
    ldif.write("\n")
    debugprint("-----------\n")
    counterldif+=1

ldif.close()

print "Done %s LDIF entries" % counterldif
print "------------------------------------------------------------"
print "VCF #%s / LDIF #%s" % (countervcf,counterldif)

