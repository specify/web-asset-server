"""EXIF parser subprocess: bounded address space, CPU time, input and output."""
import json
import resource
import sys


def main():
    memory = int(sys.argv[2])
    resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    import exifread
    with open(sys.argv[1], 'rb') as source:
        tags = exifread.process_file(source, details=False)
    encoded = json.dumps({key: str(value) for key,value in tags.items()})
    if len(encoded.encode('utf-8')) > 1024*1024:
        return 2
    print(encoded)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception:
        sys.exit(2)
