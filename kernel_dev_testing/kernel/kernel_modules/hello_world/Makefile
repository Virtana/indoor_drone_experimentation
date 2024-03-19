ifneq ($(KERNELRELEASE),)
obj-m := hello.o
else
KDIR := /compulab_kernel/build/

all:
	$(MAKE) -C $(KDIR) M=$(PWD)
endif
