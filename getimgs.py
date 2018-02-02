# Downloader
# 

import os
import re
import sys
import urllib
import shutil

import requests

"""
"""

def read_urls(urlfile):
    """
    """
    imgtypes = ('jpg', 'png', 'gif', 'bmp', 'tif', 'tiff')
    imgs = [];
    for imgtype in imgtypes:
        pattern = re.compile(r'''"(http\S+.'''+ imgtype + ''')''')
        temp = re.findall(pattern, urlfile)
        print '# of', imgtype, ':', len(temp)
        imgs = imgs + temp
      
    return imgs
    
def read_txt(urlfile):
    """
    """
    imgtypes = ('jpg', 'png', 'gif', 'bmp', 'tif', 'tiff')
    imgs = [];
    f = open(urlfile, 'r')
    for imgtype in imgtypes:
        pattern = re.compile(r'''"(http\S+.'''+ imgtype + ''')''')
        temp = re.findall(pattern, f.read())
        print '# of', imgtype, ':', len(temp)
        imgs = imgs + temp
    f.close()      
    return imgs

def download_images(img_urls, dest_dir):
    """
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    index = file(os.path.join(dest_dir, 'overview.html'), 'w')
    index.write('<html><body>\n')

    for img_url in img_urls:
      
        img_name = img_url.split('/')[-1]
        img_name = re.sub('[^0-9a-zA-Z]+', '_', img_url.split('.')[-2]) + '.' + img_url.split('.')[-1]
        print 'Retrieving...', img_url
        try:
            response = requests.get(img_url, stream=True)
            with open(dest_dir + '/' + img_name, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)  
        
            index.write('<img src="%s"><p>/n"%s"</p>' % (img_name,img_name,))
            
        except Exception as e:
            print e

    index.write('\n</body></html>\n')
    index.close()
  
  
def get_page(url):
    r = requests.get(url)
    content = r.text.encode('utf-8', 'ignore')
    print content
    return content
    
def main():
    args = sys.argv[1:]

    if not args:
        print 'usage: [--url url] logfile '
        sys.exit(1)
    
    if args[0] == '--url':      
        todir = str(args[1].split('/')[2])
        urls_code = get_page(args[1])  
        img_urls = read_urls(urls_code)
        
    elif args[0] == '--file':
        todir = 'getimgs'
        img_urls = read_txt('getimgs.txt')
    
    if todir:
        download_images(img_urls, todir)
    else:
        print '\n'.join(img_urls)
  

if __name__ == '__main__':
  main()
