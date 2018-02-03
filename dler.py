# Downloader
# 

import os
import re
import sys
import urllib
import shutil

import requests
import threading

"""
"""
task_queue = []     # can be modified in do_task() & queue_tasks()
task_buffer = []    # can be modified in do_task() & task_hub()

class do_task(threading.Thread):
    def __init__(self, name, args):
        threading.Thread.__init__(self)
        self.name = name
        self.args = args
        return

#    def run(self):
#        logging.debug('running with %s and %s', self.args, self.kwargs)
#        return
        
    #def do_task(args):
    def run(self):        
        """
        Process the commend to retrieve images in url
        url url:
            downloads all images in url
        murl url:
            downloads all related images in url in special aspect
        curl url:
            downloads all related image in url by last page count
        file:
            acts like 'url url', dler.txt treats as input source code
        """
        global task_queue
        global task_buffer
        
        try:
            todir = str(self.args[1].split('/')[-2])
            if self.args[0] == 'url':      
                urls_code = self.get_page(self.args[1])  
                img_urls = self.read_urls(urls_code)            
            elif self.args[0] == 'murl':
                urls_code = self.get_page([self.args[1]])  
                img_urls = self.read_murls(urls_code)                  
            elif self.args[0] == 'curl':
                img_urls = self.read_curls(self.args[1])               
            elif self.args[0] == 'file':
                todir = 'dler'
                img_urls = self.read_txt('dler.txt')    
                
            if todir:
                self.download_images(img_urls, todir)
            else:
                print '\n'.join(img_urls)   
        except Exception as e:
            print e
            print 'Aborted', self.args[0], self.args[1]
        
        print 'Done!', self.args[0], self.args[1]   
        task_queue.pop(task_queue.index(self.args))
        task_buffer.pop(task_buffer.index(self.args)) 
        return
    
    def remove_duplicates(self, values):
        """
        Remove all duplicated link of image to avoid extra downloading time
        """
        output = []
        seen = set()
        for value in values:
            # If value has not been encountered yet,
            # ... add it to both list and set.
            if value not in seen:
                output.append(value)
                seen.add(value)
        return output
    
    def read_urls(self, urlfile):
        """
        For cmd = url ...
        Scan url source code with image extension matching 
        """
        imgtypes = ('jpg', 'png', 'gif', 'bmp', 'tif', 'tiff')
        imgs = [];
        for imgtype in imgtypes:
            pattern = re.compile(r'''"(http\S+.'''+ imgtype + ''')''')
            temp = re.findall(pattern, urlfile)
            imgs = imgs + temp
          
        return self.remove_duplicates(imgs)
        
    def read_murls(self, urlfile):
        """
        For cmd = murl ...
        Scan url source code with image extension matching 
        """
        pattern = re.compile(r'''(//\S+.jpg)''')
        imgs = re.findall(pattern, urlfile)
        imgs = [w.replace('jpg.jpg', 'jpg') for w in imgs]
        imgs = [w.replace('t.jpg', '.jpg') for w in imgs]
        imgs = [w.replace('//t.', 'https://i.') for w in imgs]
        imgs = [w.replace('//tn.', 'https://0a.') for w in imgs]
        imgs = [w.replace('/smalltn/', '/galleries/') for w in imgs]
          
        return self.remove_duplicates(imgs)
        
    def read_curls(self, urllink):
        """
        For cmd = curl ...
        Scan url source code with image extension matching 
        """    
        imgs = [];
        maxcount = urllink.split('/')[-1][:-4]
        urllink = urllink[:urllink.find(maxcount)]  
        print urllink
        
        for count in range(1, int(maxcount)):
            imgs.append(urllink + str(count) + '.jpg')
          
        return imgs
        
    def read_txt(self, urlfile):
        """
        For cmd = file ...
        Scan url source code in txt with image extension matching 
        """
        imgtypes = ('jpg', 'png', 'gif', 'bmp', 'tif', 'tiff')
        imgs = [];
        f = open(urlfile, 'r')
        for imgtype in imgtypes:
            pattern = re.compile(r'''"(http\S+.'''+ imgtype + ''')''')
            temp = re.findall(pattern, f.read())
            imgs = imgs + temp
        f.close()      
        return self.remove_duplicates(imgs)
    
    def download_images(self, img_urls, dest_dir):
        """
        Create directory related to url name
        Download the images to the directory
        Generate overview.html
        """
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
    
        index = file(os.path.join(dest_dir, 'overview.html'), 'w')
        index.write('<html><body>\n')
    
        for img_url in img_urls:
          
            img_name = img_url.split('/')[-1]
            img_name = re.sub('[^0-9a-zA-Z]+', '_', img_name.split('.')[-2]) + '.' + img_url.split('.')[-1]
            try:
                response = requests.get(img_url, stream=True)
                with open(dest_dir + '/' + img_name, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)  
            
                index.write('<img src="%s"><p>/n"%s"</p>' % (img_name,img_name,))
                
            except Exception as e:
                print e
    
        index.write('\n</body></html>\n')
        index.close()
      
      
    def get_page(self, url):
        """
        Retrieve source code of url
        """
        r = requests.get(url[0])
        content = r.text.encode('utf-8', 'ignore')
        return content
        
def task_hub():
    """
    Running in background to transfer queue task to buffer 
    and fire it to do_task()
    The task with same domain remains in queue until done in buffer
    """
    global task_buffer
    
    while True:
        for task in task_queue:
            if not task_buffer:
                task_buffer.append(task)
                do_task(name = task[1], args=task).start()
            if not task in task_buffer:
                dling = False
                for b in task_buffer:
                    if b[2] == task[2]:                           
                        dling = True
                if not dling:    
                    task_buffer.append(task)
                    do_task(name = task[1], args=task).start()
        
        

def domain_count_dict(domains):
    """
    Reports domain list with concurrent counts 
    """
    domain_count = {}    
    for domain in domains:        
        if not domain in domain_count:
            domain_count[domain] = 1
        else:
            domain_count[domain] = domain_count[domain] + 1
    return domain_count

def queue_tasks(args):  
    """
    Insert task by input with error check.
    Report concurrent count after any input
    """
    global task_queue
    cmd_list = ('url', 'murl', 'curl', 'file')
    
    if not args:
        print 'usage: cmd url'
    elif not args[0] in cmd_list:
        print 'Error: Undefined Command'  
    elif not args[1]:
        print 'usage: cmd url'
    elif not args[1].startswith('http'):
        print "Error: url should start with 'http'"        
    elif not args in task_queue:
        task_queue.append(args)
    else:
        print 'cmd exists...' 
    
    domain_count = domain_count_dict([d for c, u, d in task_queue])    
    domains = sorted(domain_count.keys())
    print '\nDomains in Queue:'
    for domain in domains:
        print domain, domain_count[domain]
    
    print '\nTask in Progress:'
    for b in task_buffer:
        print b[0], b[1]

def main():
    """
    Initialization of background thread with infinite loop for inputs
    """
    taskhub = threading.Thread(target = task_hub)    
    taskhub.daemon = True
    taskhub.start()
    
    while True:
        try:
            s = raw_input('\ncmd, url:\n')
            if s == 'status':                
                queue_tasks(s)
            elif s:
                s = s.split(' ')
                s.append(s[1].split('/')[2])
                queue_tasks(s)
        except Exception as e:
            print e

if __name__ == '__main__':
  main()
