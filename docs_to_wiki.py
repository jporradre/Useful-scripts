#!/usr/bin/env python

#Copyright (C) 2015  Juan Pablo Orradre
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import subprocess

def ayuda():
    msg="docs_to_wiki.py : Convierte documentacion en formato .doc, .docx y .odt a formato wiki.\n" \
        "NOTA: Debe tener instalado Pandoc y Libreoffice ver. >= 4 para que el script funcione correctamente.\n"\
        "Parametros: -h : (opcional) Ayuda \n" \
        "            <ruta fichero a convertir> : Se debe indicar un archivo o fichero de archivos a ser convertidos a formato Wiki\n";
    print(msg);



#Convierte un documento de texto a docx
def x_to_docx(pFName):

    cmd = 'soffice --headless --convert-to docx "'+pFName+'"';
    subp = subprocess.Popen(cmd,  stdout=subprocess.PIPE , stderr=subprocess.PIPE, shell=True);

    stdout, stderr = subp.communicate();

    ecode = subp.returncode;

    if ecode != 0 :
        raise Exception("[ERROR] Hubo un error en la conversion a docx del archivo "+pFName+" : "+stderr+" . "+stdout);



#Convierte un archivo docx a formato wiki
def docx_to_wiki(pFName):

    cmd = 'pandoc -o "'+pFName+'.wiki" -t mediawiki "'+pFName+'"';
    subp = subprocess.Popen(cmd,  stdout=subprocess.PIPE , stderr=subprocess.PIPE, shell=True);

    stdout, stderr = subp.communicate();

    ecode = subp.returncode;

    if ecode != 0 :
        raise Exception("[ERROR] Hubo un error en la conversion a wiki del archivo "+pFName+" : "+stderr+" . "+stdout);



#Procesa la conversion del archivo
def convertir(pFName):

    try:
        ext = pFName.split(".")[pFName.count(pFName)].strip().upper();
    except Exception as e:
        print("[ERROR] Error al obtener la extension del documento "+pFName+" - "+str(e));
        exit(1);

    if (ext in ["DOCX","DOC","ODT"]):

        try:

            if (ext != "DOCX"):
                x_to_docx(pFName);

            docx_file = pFName.replace("."+ext.lower(),".docx");
            docx_to_wiki(docx_file);
            os.remove(docx_file);

        except Exception as e:
            print("[ERROR] Error al procesar el archivo "+pFName+" - "+str(e));

    else:
        print("[ERROR] El archivo "+pFName+" no tiene una extension valida");



#Realiza el procesamiento inicial de la conversion
def procesar(pFName):

    global cmd;
    global ext;
    global docx_file;
    global tipo_fic;

    if (os.path.isdir(pFName)):

        try:
            files = os.listdir(pFName);
            for f in files:
                convertir(f);
        except Exception as e:
            print("[ERROR] Error al iterar el fichero "+pFName+" - "+e.message);
            exit(1);

    else:
        convertir(pFName);



if len(sys.argv) < 2 or sys.argv[1].strip() == "":
    ayuda();
    exit(1);

fname = sys.argv[1];

if not (os.path.exists(fname)):
    print("[ERROR] El fichero "+fname+" no existe!!!");
    exit(1);

procesar(fname);
