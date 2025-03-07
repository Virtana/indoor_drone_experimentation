#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/fs.h>
#include <linux/uaccess.h>


#define DEVICE_NAME "char_dev"

static char message[100];

static int device_open(struct inode* inode, struct file* f)
{
  pr_alert("DEVICE OPENED\n");
  return 0;
}

static int device_release(struct inode* inode, struct file* f)
{
  pr_alert("DEVICE CLOSED\n");
  return 0;
}

static ssize_t device_read(struct file* f, char* buffer, size_t len, loff_t* offset)
{
  if(*message == 0)
  {
    return 0;
  }

  int i;
  for(i=0;i<len;i++)
  {
    put_user(message[i], buffer + i);
  }

  return 0;
}

static ssize_t device_write(struct file* f, const char* buffer, size_t len, loff_t* offset)
{
  int i;
  for (i=0;i<len && i < 100; i++)
  {
    get_user(message[i], buffer + i);
  }
  return i;
}

static struct file_operations file_ops = {
  .read = device_read,
  .write = device_write,
  .open = device_open,
  .release = device_release,
};

static int major;

static int __init testchardev_init(void)
{
  pr_alert("Init function for hello module!\n");
  major = register_chrdev(0, DEVICE_NAME, &file_ops);
  if (major < 0)
  {
    pr_alert("Failed to register chrdev\n");
    return major;
  }

  pr_alert("Char Driver loaded with major %d\n", major);

  return 0;
}

static void __exit testchardev_exit(void)
{
  unregister_chrdev(major, DEVICE_NAME);
  pr_alert("exit function for the hello module!\n");
}

module_init(testchardev_init);
module_exit(testchardev_exit);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Greeting module");
MODULE_AUTHOR("Hello Module Author");
