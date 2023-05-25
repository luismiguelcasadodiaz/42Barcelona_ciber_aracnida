#!/Users/lcasado-/miniconda3/envs/42AI-lcasado-/bin/python
#!/home/luis/anaconda3/envs/42AI-lcasado-/bin/python

"""
#!/usr/bin/python3
Created on Sat Apr 15 06:11:12 2023

@author: lcasado-

El programa spider permitirá extraer todas las imágenes de un sitio web,
de manera recursiva, proporcionando una url como parámetro.

Gestionarás las siguientes opciones del programa:
./spider [-rlpS] URL

  • Opción -r : descarga de forma recursiva las imágenes en una URL recibida
  como parámetro.

  • Opción -r -l [N] : indica el nivel profundidad máximo de la descarga
  recursiva.   En caso de no indicarse, será 5.

  • Opción -p [PATH] : indica la ruta donde se guardarán los archivos
  descargados. En caso de no indicarse, se utilizará ./data/.

  El programa descargará por defecto las siguientes extensiones:
  ◦ .jpg/jpeg
  ◦ .png
  ◦ .gif
  ◦ .bmp
"""

import argparse       # helper to analise command line arguments
import pathlib
import os
import sys
from pprint import pprint
import time

import requests
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

import re
from bs4 import BeautifulSoup


import validators



MIN_LEVEL_RECUR = 1
MAX_LEVEL_RECUR = 5
ALLOWED_SCHEMES = ['https', 'http', 'file']
# IANA schemes include http, https, ftp, mailto, file, data and irc
WEB_SCHEMES = ['https', 'http']
LOCAL_SCHEMES = ['file']
ALLOWED_CHARSETS = ['utf-8', 'ISO-Latin-1', 'latin-1', 'iso-8859-1', 'iso-8859-15']
ALLOWED_IMG_EXTE = tuple([".jpg", ".JPG", ".jpeg", ".JPEG",
                          ".png", ".PNG", ".gif", ".GIF",
                          ".bmp", ".BMP", ".pdf", ".PDF",
                          ".docx", ".DOCX"])

def ft_progress(list):
    size = len(list)
    elap_time = 0
    sleep_time = 0.0
    bar_size = 40
    bar_items = 0
    count = -1
    start_time = time.time()
    my_time = start_time
    times_between_calls = []

    size_len = len(str(size))
    percen = 0
    
    while count < size - 1:
        count = count + 1
        actual_time = time.time()
        sleep_time = actual_time - my_time  #  time diff between calls
        times_between_calls.append(sleep_time)
        my_time = actual_time               #  last call time update
        # i use time average between calls to calculate execution time
        tot_eta_time = (sum(times_between_calls) / len(times_between_calls)) * size 
        # elapsee time accumulation
        elap_time = elap_time + sleep_time
        chunk5 = f"| elapsed time {elap_time:.2f}s"
        eta_time = tot_eta_time - elap_time
        display_eta_time = eta_time if eta_time > 0 else 0
        chunk1 = f"ETA: {display_eta_time:0>5.2f}s "
        percen = (count + 1) / size
        chunk2 = f"[{100 * percen:3.0f}%]"
        display_counter = count + 1
        chunk4 = f"{display_counter:{size_len}}/{size}"
        bar_items = "=" *(int(bar_size * percen) - 1) + ">"
        chunk3 = f"[{bar_items:<{bar_size}}] "
        print(chunk1 + chunk2 + chunk3 + chunk4 + chunk5, end="\r", flush=True)
        yield list[count]


def create_argument_parser():

    def uniform_resource_locator(url_txt):
        """
          helper function that validates url passed at command line
        """
        # 1.- urlparse splits componenst
        parsed_url = urlparse(url_txt)
        # 2.- check if scheme is allowed in this app
        if parsed_url.scheme in ALLOWED_SCHEMES:
            if parsed_url.scheme in WEB_SCHEMES:
                # validators does not accept other schemes than http
                fake_url = "https://" + parsed_url.netloc
                # 3.- check if netloc/domain/autohity i ok
                ok_url = validators.url(fake_url)
                if not ok_url:
                    parser.error(f"Invalid WEB url {url_txt}")
                else:
                    # 4.- returns ALLOWED SCHEME and valid Authuority
                    return url_txt
            else:
                # we face a file path
                if os.path.isfile(parsed_url.path):
                    return url_txt
                else:
                    parser.error(f"Invalid PATH {url_txt}")

        else:
            # passed scheme is not allowed
            problem1 = parsed_url.scheme
            msg = f"Scheme '{problem1}' from url {url_txt} not allowed"
            parser.error(msg)

    def recursion_level(argument):
        """
          helper function that recursion level passed at command line
        """
        if argument is None:
            return 5
        else:
            try:
                int_arg = int(argument)
                if MIN_LEVEL_RECUR <= int_arg and int_arg <= MAX_LEVEL_RECUR:
                    return int_arg
                else:
                    parser.error("Recursivity level not between {} and {}".
                                 format(MIN_LEVEL_RECUR, MAX_LEVEL_RECUR))
            except:
                parser.error(f"Incorrect recursivity level '{argument}'")

    parser = argparse.ArgumentParser(
                                     prog='spider',
                                     description='Extraer todas las imágenes\
                                                  de un sitio web',
                                     epilog='Este es el final de la ayuda')

    parser.add_argument('--recursive', '-r',
                        help='Descarga recursivamente las imágenes.',
                        action='store_true',
                        default=False
                        )

    parser.add_argument('--level', '-l',
                        help=f'Nivel máximo de la descarga recursiva. \
                          {MAX_LEVEL_RECUR} niveles por defecto.',
                        type=recursion_level)

    parser.add_argument('--path', '-p',
                        help='Ruta para guardar las imágenes.',
                        type=pathlib.Path,
                        default='./data/')

    parser.add_argument('url',
                        help='URL de un sitio web al que descargar las\
                               imágenes',
                        type=uniform_resource_locator,
                        nargs='+')

    return parser


class Html_page():
    """ This class generates an instance per url.
        Uses the url to recover the body of an html page.
        creates a list with all image links
        creates a list with all links
        This links belong to same domain name or authority from url

        with two dictionaries avoids link duplication.

        Dictionaries:
          Key : URL
          Value : list [num_times_found, visited]

    """
    NUM_TIMES_FOUND = 0
    VISITED = 1
    cls_img_d = {}
    cls_link_d = {}

    def __init__(self, url):
        self.url = url
        self.num_links = 0
        self.num_images = 0
        self.authority = None
        self.scheme = None
        self.ins_img_d = {}
        self.ins_link_d = {}
        self.char_set = ""
        self.html = url

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, an_url):
        self._url = an_url

    @property
    def num_links(self):
        return self._num_links

    @num_links.setter
    def num_links(self, num):
        if isinstance(num, int) and num >= 0:
            self._num_links = num

    @property
    def num_images(self):
        return self._num_images

    @num_images.setter
    def num_images(self, num):
        if isinstance(num, int) and num >= 0:
            self._num_images = num

    @property
    def authority(self):
        return self._authority

    @authority.setter
    def authority(self, text):
        self._authority = text

    @property
    def scheme(self):
        return self._scheme

    @scheme.setter
    def scheme(self, text):
        if text in ALLOWED_SCHEMES:
            self._scheme = text
        else:
            self._scheme = None

    @property
    def ins_img_d(self):
        return self._ins_img_d

    @ins_img_d.setter
    def ins_img_d(self, an_url):
        if hasattr(self, '_ins_img_d'):
            if an_url in self._ins_img_d:
                # as it exist add 1 to num times
                self._ins_img_d[an_url][self.NUM_TIMES_FOUND] += 1
            else:
                self._ins_img_d[an_url] = [1, False]
                self.num_images = self.num_images + 1
        else:
            setattr(self, '_ins_img_d', {})

    @property
    def ins_link_d(self):
        if '_ins_link_d' not in self.__dict__:
            pass
        else:
            return self._ins_link_d

    @ins_link_d.setter
    def ins_link_d(self, an_url):
        if hasattr(self, '_ins_link_d'):
            if self._ins_link_d is None:
                pass
            if an_url in self._ins_link_d:   # link found previously
                # as it exist add 1 to num times
                self._ins_link_d[an_url][self.NUM_TIMES_FOUND] += 1
            else:  # new link
                self._ins_link_d[an_url] = [1, False]
                self.num_links = self.num_links + 1
        else:
            setattr(self, '_ins_link_d', {})

    @property
    def char_set(self):
        return self._char_set

    @char_set.setter
    def char_set(self, text):
        if text in ALLOWED_CHARSETS:
            self._char_set = text
        else:
            # print(f"Charset {text} no ha sido considerado")
            self._char_set = None

    @property
    def html(self):
        return self._html

    @html.setter
    def html(self, an_url):
        parsed_url = urlparse(an_url)
        # print("tratamos esto", parsed_url)
        if parsed_url.scheme in ALLOWED_SCHEMES:
            if parsed_url.scheme in WEB_SCHEMES:
                self.scheme = parsed_url.scheme
                #  check if new link belong to.
                self.authority = parsed_url.netloc
                # opens the url and gets de body
                tested_url = My_url(an_url)
                self.char_set = tested_url.char_set
                # link inserted in the instance dictionary
                self.ins_link_d = an_url
                self._html = tested_url.body
                self.ins_link_d[an_url] = [1, True]  # set link as visited
                self.cls_link_d[an_url] = [1, True]  # set link as visited
            else:
                # TODO: html is in a local file
                self.scheme = parsed_url.scheme
                tested_path=My_url(parsed_url.path)
                self._html = tested_path.body
                self.char_set = tested_path.char_set
                self.scheme = tested_path.scheme
                self.authority = tested_path.authority
                # link inserted in the instance dictionary
                self.ins_link_d = an_url
                self.ins_link_d[an_url] = [1, True]  # set link as visited
                self.cls_link_d[an_url] = [1, True]  # set link as visited
        else:
            msg = f"Html_page:Scheme '{parsed_url.scheme}'"
            msg = msg + " from url {an_url} not allowed"
            raise ValueError(msg)

    def find_right_attributes(self, link):
        """
        Analyse link attributes dictionary
        Filters attributes relates to image src
        returns a set
        """
        # from link attributes dictionary i remove teh ones not related to src
        my_set = set()
        for k, v in link.attrs.items():
            if k in ['src', 'data-full-src']:
                my_set.add(v)
        return my_set

    def find_images_in_url(self):
        # print(f"searching images -{self.url}-")
        soup = BeautifulSoup(self.html, 'html.parser',
                             from_encoding=self.char_set)
        for link in soup.find_all('img'):
            the_urls = self.find_right_attributes(link)
            if len(the_urls) > 0:  # avoids register img tags without src
                for an_url in the_urls:
                    # Register only some extensions
                    if an_url.endswith(ALLOWED_IMG_EXTE):
                        self.ins_img_d = an_url

    def find_links_in_url(self):
        soup = BeautifulSoup(self.html, 'html.parser',
                             from_encoding=self.char_set)
        links = soup.find_all('a')
        print(f"Found {len(links)} links in -{self.url}-")
        for link in links:
            an_url = link.get('href')
            if an_url is not None:
                parsed_url = urlparse(an_url)
                if parsed_url.netloc in self.authority:  # link IN my domain
                    # first try was parsed_url.netloc == self.authority
                    # as 'elpais.com' was != 'www.elpais.com'
                    # i changed it to parsed_url.netloc in self.authority
                    self.ins_link_d = an_url
                else:
                    pass   # i do nothing wiht links not belonging to my domain
            else:
                pass   # do nothing when a linsk has not href

    def filter_links(self):
        """
          Filters the link_dictionary
          returns
          Dictionaries:
            Key : URL
            Value : Duple (num_times_found, visited)
            self.link_dict[k][0] = True   ==> VISITED
            self.link_dict[k][1] = False  ==> NOT VISITED
        """
        filtered_d = {}
        for k, v in self.ins_link_d.items():
            if not self.ins_link_d[k][1]:
                filtered_d[k] = v

        return filtered_d
    
    #@classmethod
    def filter_class_links(cls):
        """
          Filters the link_dictionary
          returns
          Dictionaries:
            Key : URL
            Value : Duple (num_times_found, visited)
            self.link_dict[k][0] = True   ==> VISITED
            self.link_dict[k][1] = False  ==> NOT VISITED
        """
        filtered_d = {}
        for k, v in cls.cls_link_d.items():
            if not cls.cls_link_d[k][1]:
                filtered_d[k] = v

        return filtered_d

    
    def update_link_class_dict(self):
        for link in self.ins_link_d:
            if link not in self.__class__.cls_link_d:
                self.__class__.cls_link_d[link] = self.ins_link_d[link]


class My_url():
    """ This class converts an url into a url body
    """
    def __init__(self, url):
        self.url = url
        self.status = None
        self.body = None
        self.char_set = None
        self.scheme = None
        self.authority = None

        if os.path.isfile(url):
            self.get_file_content()
        else:
            self.get_body()

    def get_file_content(self):
        with open(self.url, 'r') as f:
            content = f.readlines()
        self.body = "".join(content).strip()
        self.char_set = 'utf-8'
        soup = BeautifulSoup(self.body, 'html.parser', from_encoding='utf-8')
        file_canonical =""
        for i in soup.select('link[rel*=canonical]'):
            file_canonical =i['href']
        parsed_file_canonical = urlparse(file_canonical)
        self.scheme = parsed_file_canonical.scheme
        self.authority = parsed_file_canonical.netloc

    def get_body(self):
        """
        Opens the url. if staus ok returs devode body
        """
        try:
            with urlopen(self.url, timeout=10) as response:
                body = response.read()
                self.status = response.status

            if self.status == 200:
                self.char_set = response.headers.get_content_charset()
                try:
                    self.body = body.decode(self.char_set)
                except UnicodeDecodeError:
                    self.body = " "
                except TypeError:
                    self.body = " "
            else:
                return None
        except HTTPError as error:
            print(error.status, error.reason)
        except URLError as error:
            print(error.reason)
        except TimeoutError:
            print("Request timed out")


def img_scrapper(url, path: str, recursive: bool, level=5):
    """
    Parameters:
      url: the url to start scrap from
      path : a path for saving url images
      recursive: boolean, indicates if recursively scrap links founds
      level : int . set the deep for recur

    Returns
      a dictionary whose key is an url os an image
    """
    print(f"at level {level} scrapping -{url}-")
    image_urls = {}
    if not recursive:
        page = Html_page(url)
        page.find_images_in_url()
        return page.ins_img_d, Html_page.cls_link_d
    if recursive:
        if level > 0:
            parsed_url = urlparse(url)
            page = Html_page(url)
            # pprint(page.html)
            page.find_images_in_url()
            page.find_links_in_url()
            page.update_link_class_dict()
            not_visited_links = page.filter_class_links()
            print(f"pending of visit {len(not_visited_links)}")
            links_to_images_d = {}
            for link in not_visited_links:
                parsed_l = urlparse(link)
                if parsed_l.netloc == '':
                    # treat relative url found in this page
                    # i add the autoroty from this page before scraping it
                    if parsed_url.scheme == 'file':
                        # this is the case that i find a relative web URL
                        # inside an html read from file
                        # i got autority from the canonical url at open
                        parsed_l = parsed_l._replace(netloc=page.authority)
                    else:
                        parsed_l = parsed_l._replace(netloc=parsed_url.netloc)
                if parsed_l.scheme == '':
                    # this is the case when the link has not scheme
                    if parsed_url.scheme == 'file':
                        # if the link belong to an htmel read form file
                        # i got scheme from the caninical
                        parsed_l = parsed_l._replace(scheme=page.scheme)
                    else:
                        parsed_l = parsed_l._replace(scheme=parsed_url.scheme)
                if parsed_l.scheme in ALLOWED_SCHEMES:
                    dict_with_images, enlaces = img_scrapper(parsed_l.geturl(), path, recursive, level - 1)
                    links_to_images_d.update(dict_with_images)

            return links_to_images_d, Html_page.cls_link_d
        else:
            page = Html_page(url)
            page.find_images_in_url()
            return page.ins_img_d, Html_page.cls_link_d



if __name__ == '__main__':
    # create cli arguments parser
    parser = create_argument_parser()
    # analize arguments
    pprint(sys.argv)
    #args = parser.parse_args(sys.argv[1:])
    #args = parser.parse_args(['--recursive', '--level',  '1', 'file:/Users/lcasado-/Documents/42/cyber/arachnida/eldebate.html'])
    #args = parser.parse_args(['--recursive', '--level',  '1', 'https://www.iese.edu/'])
    args = parser.parse_args(['--recursive',  'https://rodalies.gencat.cat/es/inici/'])
    """
    try:
        args = parser.parse_args(sys.argv[1:])
    except:
        #args = parser.parse_args(['https://www.elpais.com/'])
        #args = parser.parse_args(['--recursive', '--level',  '1', 'https://www.elmundo.es/'])
        #args = parser.parse_args(['--recursive', '--level',  '1', 'https://www.elpais.com/'])
        #args = parser.parse_args(['--recursive', '--level',  '1', 'https://www.eldebate.com'])
        print("intente nuevamente")
    
    #args = parser.parse_args(['-p','~/','https://www.eldebate.com/'])

    args = parser.parse_args(['https://realpython.github.io/fake-jobs/'])
    args = parser.parse_args(['https://www.eldebate.com'])

    #args = parser.parse_args(['https://www.eldebate.com/'])
    """
    # check if folder for images exists
    print(args)
    cwd = os.getcwd()
    spiderpath = os.path.join(cwd, args.path)
    try:
        if not os.path.isdir(spiderpath):  # spider path does not exist
            os.makedirs(spiderpath)          # then I create it
        else:                              # spider pathfolder exist
            if not os.access(spiderpath, os.W_OK):
                msg = f"Write permission denegated at {spiderpath}"
                raise ValueError(msg)
    except ValueError:
        print(msg)

    # Detectar si tengo permiso de escribir en ese directorio
    #os.system('clear')
    if not args.recursive:
        if args.level is None:
            links_to_images_d, links = img_scrapper(args.url[0], spiderpath,
                                             args.recursive)
        else:
            msg = f"recursitivy level {args.level} incorrect "
            msg = msg + "when no recursivity required"
            parser.error(msg)
    else:
        if args.level is None:
            links_to_images_d , links= img_scrapper(args.url[0], spiderpath,
                                             args.recursive, MAX_LEVEL_RECUR)
        else:
            links_to_images_d, links = img_scrapper(args.url[0], spiderpath,
                                             args.recursive, args.level)

    print("He encontrado ", len(links_to_images_d), " imagenes")
    print("He encontrado ", len(links), " enlaces")
    pprint(links)

    image_counter = 0
    # calcule to know length of counter, for zero left padding
    image_counter_lenght = len(str(len(links_to_images_d)))
    site = urlparse(args.url[0])
    img_duplication_control = {}  #dict to avoid download repeated img
    duplicated = 0  # counter of duplicated image
    for url in ft_progress(list(links_to_images_d.keys())):
        if url is not None:
            image_num = f"{image_counter:0>{image_counter_lenght}}_"
            image_counter = image_counter + 1
            parsed_l = urlparse(url)
            if parsed_l.netloc == '':
                parsed_l = parsed_l._replace(netloc=site.netloc)
            if parsed_l.scheme == '':
                parsed_l = parsed_l._replace(scheme=site.scheme)
            
            # print(image_counter)
            # 00nn_image_name
            image_name_in_url = url[url.rfind('/') + 1:]
            if image_name_in_url not in img_duplication_control:
                img_duplication_control[image_name_in_url] = True
                image_file_name = image_num + image_name_in_url
                img_data = requests.get(parsed_l.geturl()).content
                image_path = os.path.join(spiderpath, image_file_name)
                with open(image_path, 'wb') as handler:
                    handler.write(img_data)
            else:
                duplicated = duplicated + 1
    print(f"Descarga de imagenes en {spiderpath} finalizada.")
    print(f"He descargado {image_counter} images.")
    print(f"Encontre {duplicated} duplicadas que no descargue")
