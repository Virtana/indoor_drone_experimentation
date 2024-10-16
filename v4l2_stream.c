#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/ioctl.h>
#include <unistd.h>
#include <linux/videodev2.h>

#define NBUF 2

void query_capabilities(int fd)
{
    struct v4l2_capability cap;

    if (-1 == ioctl(fd, VIDIOC_QUERYCAP, &cap))
    {
        perror("Query Capabilities Failed\n");
        exit(EXIT_FAILURE);
    }

    if (!(cap.capabilities & V4L2_CAP_VIDEO_CAPTURE_MPLANE))
    {
        printf("No video capture device\n");
        exit(EXIT_FAILURE);
    }

    if (!(cap.capabilities & V4L2_CAP_STREAMING))
    {
        printf("No streaming\n");
        exit(EXIT_FAILURE);
    }
}

int set_format(int fd)
{
    struct v4l2_format format = {0};

    format.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    format.fmt.pix.width = 1280;
    format.fmt.pix.height = 720;

    format.fmt.pix.pixelformat = V4L2_PIX_FMT_Y10;
    format.fmt.pix.field = V4L2_FIELD_NONE;

    int res = ioctl(fd, VIDIOC_S_FMT, &format);

    if(res == -1)
    {
        perror("Failed to set format\n");
        exit(EXIT_FAILURE);
    }

    return res;
}

int request_buffer(int fd, int count)
{
    struct v4l2_requestbuffers req = {0};
    req.count = count;
    req.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    req.memory = V4L2_MEMORY_MMAP;

    if (ioctl(fd, VIDIOC_REQBUFS, &req) == -1)
    {
        perror("Error requesting buffer\n");
        exit(EXIT_FAILURE);
    }

    return req.count;
}

int query_buffer(int fd, int index, unsigned char **buffer)
{
    struct v4l2_buffer buf = {0};
    struct v4l2_plane planes[1];
    // planes[0].bytesused = 1280*720;

    buf.m.planes = planes;
    buf.length = 1;

    buf.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    buf.memory = V4L2_MEMORY_MMAP;
    buf.index = index;

    // printf("%i %x\n", index, &buf);

    if (ioctl(fd, VIDIOC_QUERYBUF, &buf) == -1)
    {
        perror("Error querying buffer\n");
        exit(EXIT_FAILURE);
    }

    *buffer = (uint8_t*)mmap (NULL, buf.m.planes[0].length, PROT_READ | PROT_WRITE, MAP_SHARED, fd, buf.m.planes[0].m.mem_offset);
    return buf.m.planes[0].length;
}

int queue_buffer(int fd, int index)
{
    struct v4l2_buffer bufd = {0};
    struct v4l2_plane planes[1];
    planes[0].bytesused = 1280*720;

    bufd.m.planes = planes;
    bufd.length = 1;

    bufd.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    bufd.memory = V4L2_MEMORY_MMAP;

    bufd.index = index;

    if (ioctl(fd, VIDIOC_QBUF, &bufd) == -1)
    {
        perror("Error queueing buffer\n");
        exit(EXIT_FAILURE);
    }

    return bufd.bytesused;
}

int start_streaming(int fd)
{
    unsigned int type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    if (ioctl(fd, VIDIOC_STREAMON, &type) == -1)
    {
        perror("Error starting stream\n");
        exit(EXIT_FAILURE);
    }

    return 0;
}

int dequeue_buffer(int fd)
{
    struct v4l2_buffer bufd = {0};
    bufd.type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    bufd.memory = V4L2_MEMORY_MMAP;

    struct v4l2_plane planes[1];
    planes[0].bytesused = 1280*720;

    bufd.m.planes = planes;
    bufd.length = 1;

    bufd.index = 0;

    if (ioctl(fd, VIDIOC_DQBUF, &bufd) == -1)
    {
        perror("Error dequeueing buffer\n");
        exit(EXIT_FAILURE);
    }

    return bufd.index;
}

int stop_streaming(int fd)
{
    unsigned int type = V4L2_BUF_TYPE_VIDEO_CAPTURE_MPLANE;
    if (ioctl(fd, VIDIOC_STREAMOFF, &type) == -1)
    {
        perror("Error stopping stream\n");
        exit(EXIT_FAILURE);
    }

    return 0;
}

int main()
{
    unsigned char* buffer[NBUF];
    int fd = open("/dev/video0", O_RDWR);
    int size;
    int index;
    int nbufs;

    int qsize;

    query_capabilities(fd);

    set_format(fd);

    nbufs = request_buffer(fd, NBUF);

    if(nbufs > NBUF)
    {
        printf("Increase buffers to %i\n", nbufs);
        exit(EXIT_FAILURE);
    }

    for(int i=0; i < NBUF; i++)
    {
        size = query_buffer(fd, i, &buffer[i]);
        qsize = queue_buffer(fd, i);
    }

    printf("Buffer Size %i\n", size);
    printf("QBuffer Size %i\n", qsize);

    start_streaming(fd);
    
    for (int i=0; i < 10; i++)
    {
        fd_set fds;
        FD_ZERO(&fds);
        FD_SET(fd, &fds);

        struct timeval tv = {0};
        tv.tv_sec = 2;

        int r = select(fd+1, &fds, NULL, NULL, &tv);
        if (-1 == r)
        {
            perror("Select failed\n");
            exit(EXIT_FAILURE);
        }

        if (0 == r)
        {
            perror("Timed out waiting for frame\n");
            exit(EXIT_FAILURE);
        }

        index = dequeue_buffer(fd);

        printf("DQBuffer\n");

        queue_buffer(fd, index);

        char fname[12];
        snprintf(fname, 12, "output%i.raw", i);

        int file = open(fname, O_RDWR | O_CREAT, 0666);
        write(file, buffer[index], size);

        printf("Created image %s\n", fname);
        close(file);
    }

    stop_streaming(fd);

    for(int i=0; i<NBUF; i++)
    {
        munmap(buffer[i], size);
    }

    close(fd);

    return 0;
}
