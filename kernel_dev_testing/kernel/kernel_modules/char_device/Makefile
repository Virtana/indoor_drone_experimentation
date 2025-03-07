ifneq ($(KERNELRELEASE),)
obj-m := testchardev.o
else
KDIR := /compulab_kernel/build/

all:
	$(MAKE) -C $(KDIR) M=$(PWD)
endif
