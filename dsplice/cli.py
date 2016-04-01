from argparse import ArgumentParser

from dsplice import dsplice
from dsplice.version import version

def main():
    parser = ArgumentParser(description='dsplice %s' % version)
    parser.add_argument('-i', dest='interactive',
            action='store_true',
            help='Interactive mode. Prompt for user selection \
                  on any file conflicts')
    parser.add_argument('-t', dest='image_tag',
            help='Optional tag for created image',
            default=None)
    parser.add_argument('-s', dest='skip_import',
            action='store_true',
            help='Skip importing of image and create container \
                  archive in current directory')
    parser.add_argument('merge_images', nargs='*',
            help='Images to merge')

    args = parser.parse_args()
    dsplice(args.merge_images,
            tag=args.image_tag, 
            interactive=args.interactive,
            skip_import=args.skip_import)

if __name__ == '__main__':
    main()
