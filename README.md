# dsplice

Docker image merge utility

NOTE: Combining images from multiple sources (and especially from multiple base images) isn't the best practice. Or even an accepted practice. Regardless, it can be useful in some scenarios. I hold no responsibility for the broken abominations you may create with this tool.

## Installation
```
pip install dsplice
```

## Usage

```bash
dsplice -t newimage:latest image-to-merge1:latest image-to-merge2:latest
```

dsplice will automatically resolve any file conflicts between the two images by using the most recently modified version of a file. You can prevent this behavior with the `-i` interactive mode option. 

## Options

Option | Description
--- | ---
-h | show help message and exit
-i |  Interactive mode. Prompt for user selection on any file conflicts
-t image_tag |  Optional tag for created image
-s |  Skip importing of image and create container archive(tar) in current directory
