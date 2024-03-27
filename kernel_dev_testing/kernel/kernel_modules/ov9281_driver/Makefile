ifneq ($(KERNELRELEASE),)
obj-m := ov9282.o
else
KDIR := /compulab_kernel/build/

all:
	$(MAKE) -C $(KDIR) M=$(PWD)
endif
