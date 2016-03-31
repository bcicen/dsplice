import io
import os
import sys
import json
import tarfile
import tempfile
import logging
import shutil
import hashlib
import filecmp
from time import sleep
from collections import defaultdict
from docker import Client

log = logging.getLogger()
logging.basicConfig(level=logging.INFO)

def merge_dirs(paths, outpath):
    #resolve all conflicts
    for fpath,imgpaths in get_conflicts(paths).items():
        print('\nfilepath conflict: %s' % fpath)
        print('overwrite from source:')
        choice = getchoice(list(imgpaths))
        #remove conflicting file from all other images
        rmpaths = [ '%s/%s' % (i, fpath) for i in imgpaths if i != choice ]
        for p in rmpaths:
            os.remove(p)

    print('\npopulating image...')
    for path in paths:
        copy_contents(path, outpath)

def copy_contents(srcdir, dstdir):
    for folder, subs, files in os.walk(srcdir):
        for filename in files:
            srcfile = '%s/%s' % (folder, filename)
            filebase = srcfile.replace(srcdir, '')
            dstfile = '%s%s' % (dstdir, filebase)

            basedir = os.path.dirname(dstfile)
            if not os.path.isdir(basedir):
                log.debug('mkdir %s' % basedir)
                os.makedirs(basedir)

            if not os.path.islink(dstfile):
                log.debug('cp %s -> %s' % (srcfile,dstfile))
                rprint(filebase)
                shutil.copy2(srcfile, dstfile, follow_symlinks=False)

def diff_dirs(path1, path2, diff=[]):
    def parse_diff(result, prefix=''):
        for f in result.diff_files:
            if prefix:
                diff.append('%s/%s' % (prefix, f))
            else:
                diff.append(f)
        for k,v in result.subdirs.items():
            newpfix = '%s/%s' % (prefix,k)
            parse_diff(v, newpfix)

    parse_diff(filecmp.dircmp(path1, path2, ignore=[]))
    return diff

def get_conflicts(paths):
    """ find conflicting file paths in dirs """
    conflicts = defaultdict(set)
    for this_dir in paths:
        comp_dirs = [ p for p in paths if p != this_dir ]
        for cd in comp_dirs:
            for filepath in diff_dirs(this_dir, cd):
                conflicts[filepath].add(cd)
                conflicts[filepath].add(this_dir)
    return conflicts

def getchoice(opts):
    selected = None
    for idx, opt in enumerate(opts):
        print('%s. %s' % (idx, opt))
    print('q. abort')
    while not selected:
        selected = opts[0]
        try:
            selected = opts[int(input('selection> '))]
        except (IndexError, ValueError):
            print('invalid selection')
    print()
    return selected

def rprint(msg):
    sys.stdout.write("\033[K")
    print(msg, end='\r')

def main(merge_images):

    client = Client(base_url='unix://var/run/docker.sock')
    
    new_image_dir = tempfile.mkdtemp() 
    layers_dir = new_image_dir + '/layers'
    build_dir = new_image_dir + '/build'
    os.mkdir(layers_dir)
    os.mkdir(build_dir)
    images = []

    print('exporting images...')
    for img in merge_images:
        print('%s: exporting' % img, end='')
        res = client.get_image(img)
    
        rprint('%s: extracting' % img)
        tmpdir = tempfile.mkdtemp()
        tarfile.open(fileobj=io.BytesIO(res.data), mode='r|').extractall(tmpdir)
    
        with open(tmpdir + '/manifest.json') as of:
            layers = [ l.split('/')[0] for l in \
                       json.loads(of.read())[0]['Layers'] ]
    
        #move all layers to common folder
        for layer in layers:
            src = '%s/%s/layer.tar' % (tmpdir, layer)
            dst = '%s/%s.tar' % (layers_dir, layer)
            rprint('%s: gathering layer %s' % (img, layer))
            if not os.path.exists(dst):
                shutil.move(src, dst)
                log.debug('mv %s -> %s' % (src,dst))
    
        shutil.rmtree(tmpdir)
    
        extract_dir = '%s/%s' % (new_image_dir, img.replace('/', '-'))
        os.mkdir(extract_dir)
    
        rprint('%s: done\n' % (img))
        images.append({ 'name': img, 'layers': layers, 'dir': extract_dir  })
    
    all_layers = [ i['layers'] for i in images ]
    shared_layers = set(all_layers[0]).intersection(*all_layers[1:])
    
    #create image base using shared layers
    print('\nextracting image layers...')
    for layer in images[0]['layers']:
        if layer in shared_layers:
            rprint('extracting shared layers: %s' % layer)
            tar = tarfile.open('%s/%s.tar' % (layers_dir, layer))
            tar.extractall(build_dir)
    rprint('extracting shared layers: done\n')
    
    #extract all layers for each image to own dir
    for i in images:
        uniq_layers = [ l for l in i['layers'] if l not in shared_layers ]
        for layer in uniq_layers:
            rprint('extracting unique layers: %s' % layer)
            tar = tarfile.open('%s/%s.tar' % (layers_dir, layer))
            tar.extractall(i['dir'])
    rprint('extracting unique layers: done\n')
    
    print(build_dir)
    merge_dirs([ i['dir'] for i in images ], build_dir)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('usage: %s image1:latest image2:latest ...' % sys.argv[0])
        sys.exit(1)
    main(sys.argv[1:])
